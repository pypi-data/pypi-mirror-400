"""Batching span processor with bounded queue and background flush."""

from __future__ import annotations

import threading
import time
from collections import deque
from typing import Deque, Iterable, List, Optional

from traccia_sdk.processors.drop_policy import DEFAULT_DROP_POLICY, DropPolicy
from traccia_sdk.processors.sampler import Sampler
from traccia_sdk.tracer.provider import SpanProcessor
from traccia_sdk.tracer.span import Span


class BatchSpanProcessor(SpanProcessor):
    def __init__(
        self,
        exporter=None,
        *,
        max_queue_size: int = 5000,
        max_export_batch_size: int = 512,
        schedule_delay_millis: int = 5000,
        drop_policy: Optional[DropPolicy] = None,
        sampler: Optional[Sampler] = None,
    ) -> None:
        self.exporter = exporter
        self.max_queue_size = max_queue_size
        self.max_export_batch_size = max_export_batch_size
        self.schedule_delay = schedule_delay_millis / 1000.0
        self.drop_policy = drop_policy or DEFAULT_DROP_POLICY
        self.sampler = sampler

        self._queue: Deque[Span] = deque()
        self._lock = threading.Lock()
        self._event = threading.Event()
        self._shutdown = False
        self._worker = threading.Thread(target=self._worker_loop, daemon=True)
        self._worker.start()

    def on_end(self, span: Span) -> None:
        if self._shutdown:
            return

        # Head-based sampling is recorded on SpanContext.trace_flags.
        # If a sampler is configured, traces marked as not-sampled (0) are dropped.
        if self.sampler and getattr(span.context, "trace_flags", 1) == 0:
            return

        with self._lock:
            enqueued = self.drop_policy.handle(self._queue, span, self.max_queue_size)
            if not enqueued:
                return
            self._event.set()

    def force_flush(self, timeout: Optional[float] = None) -> None:
        deadline = time.time() + timeout if timeout else None
        while True:
            flushed_any = self._flush_once()
            if not flushed_any:
                return
            if deadline and time.time() >= deadline:
                return

    def shutdown(self) -> None:
        self._shutdown = True
        self._event.set()
        self._worker.join(timeout=self.schedule_delay * 2)
        self.force_flush()

    # Internal
    def _worker_loop(self) -> None:
        while not self._shutdown:
            self._event.wait(timeout=self.schedule_delay)
            self._event.clear()
            self._flush_once()

    def _flush_once(self) -> bool:
        spans = self._drain_queue(self.max_export_batch_size)
        if not spans:
            return False
        self._export(spans)
        return True

    def _drain_queue(self, limit: int) -> List[Span]:
        items: List[Span] = []
        with self._lock:
            while self._queue and len(items) < limit:
                items.append(self._queue.popleft())
        return items

    def _export(self, spans: Iterable[Span]) -> None:
        if self.exporter is None:
            return
        try:
            self.exporter.export(list(spans))
        except Exception:
            # Export errors are swallowed; resilience over strictness.
            return

