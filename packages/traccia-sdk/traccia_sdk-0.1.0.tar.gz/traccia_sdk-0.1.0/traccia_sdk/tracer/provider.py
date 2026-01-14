"""TracerProvider manages tracers and span processors."""

from __future__ import annotations

import secrets
import threading
from typing import Any, Dict, List, Optional

from traccia_sdk.tracer.tracer import Tracer


class SpanProcessor:
    """Base span processor; concrete processors will extend this later phases."""

    def on_end(self, span) -> None:  # pragma: no cover - to be implemented in later phases
        pass

    def shutdown(self) -> None:  # pragma: no cover - to be implemented in later phases
        pass

    def force_flush(self, timeout: Optional[float] = None) -> None:  # pragma: no cover
        pass


class TracerProvider:
    def __init__(self, resource: Optional[Dict[str, str]] = None) -> None:
        self._tracers: Dict[str, Tracer] = {}
        self._span_processors: List[SpanProcessor] = []
        self._lock = threading.Lock()
        self.resource = resource or {}
        # Optional sampler used for head-based sampling at trace start.
        self.sampler: Optional[Any] = None

    def get_tracer(self, name: str) -> Tracer:
        with self._lock:
            tracer = self._tracers.get(name)
            if tracer is None:
                tracer = Tracer(provider=self, instrumentation_scope=name)
                self._tracers[name] = tracer
            return tracer

    def add_span_processor(self, processor: SpanProcessor) -> None:
        self._span_processors.append(processor)

    def set_sampler(self, sampler: Any) -> None:
        """Attach a sampler used when starting new root traces."""
        self.sampler = sampler

    def get_sampler(self) -> Optional[Any]:
        return self.sampler

    def _notify_span_end(self, span) -> None:
        for processor in list(self._span_processors):
            try:
                processor.on_end(span)
            except Exception:
                # Processors should not crash tracing; swallow errors for now.
                continue

    def force_flush(self, timeout: Optional[float] = None) -> None:
        for processor in list(self._span_processors):
            try:
                processor.force_flush(timeout=timeout)
            except Exception:
                continue

    def shutdown(self) -> None:
        for processor in list(self._span_processors):
            try:
                processor.shutdown()
            except Exception:
                continue

    @staticmethod
    def generate_trace_id() -> str:
        return secrets.token_hex(16)

    @staticmethod
    def generate_span_id() -> str:
        return secrets.token_hex(8)

