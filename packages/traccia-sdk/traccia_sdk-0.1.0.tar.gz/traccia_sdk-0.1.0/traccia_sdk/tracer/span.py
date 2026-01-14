"""Span implementation with sync and async context manager support."""

from __future__ import annotations

import time
import traceback
from enum import Enum
from typing import Any, Dict, List, Optional, Tuple, TYPE_CHECKING

from traccia_sdk.context import context as span_context
from traccia_sdk.tracer.span_context import SpanContext

if TYPE_CHECKING:
    from traccia_sdk.tracer.tracer import Tracer


class SpanStatus(Enum):
    UNSET = 0
    OK = 1
    ERROR = 2


class Span:
    def __init__(
        self,
        name: str,
        tracer: "Tracer",
        context: SpanContext,
        parent_span_id: Optional[str] = None,
        attributes: Optional[Dict[str, Any]] = None,
    ) -> None:
        self.name = name
        self.tracer = tracer
        self.context = context
        self.parent_span_id = parent_span_id
        self.attributes: Dict[str, Any] = dict(attributes) if attributes else {}
        self.events: List[Dict[str, Any]] = []
        self.status = SpanStatus.UNSET
        self.status_description: Optional[str] = None
        self.start_time_ns = time.time_ns()
        self.end_time_ns: Optional[int] = None
        self._activation_tokens: Optional[Tuple] = None
        self._ended = False
        # Apply per-process routing/debug metadata to tracestate for propagation.
        try:
            from traccia_sdk.context.propagators import format_tracestate, parse_tracestate
            from traccia_sdk import runtime_config

            base = parse_tracestate(self.context.trace_state or "")
            if runtime_config.get_tenant_id():
                base.setdefault("tenant", runtime_config.get_tenant_id())
            if runtime_config.get_project_id():
                base.setdefault("project", runtime_config.get_project_id())
            if runtime_config.get_debug():
                base.setdefault("dbg", "1")
            # Persist onto the context for downstream injection.
            ts = format_tracestate(base)
            if ts:
                self.context = SpanContext(
                    trace_id=self.context.trace_id,
                    span_id=self.context.span_id,
                    trace_flags=self.context.trace_flags,
                    trace_state=ts,
                )
        except Exception:
            pass

    @property
    def duration_ns(self) -> Optional[int]:
        if self.end_time_ns is None:
            return None
        return self.end_time_ns - self.start_time_ns

    def set_attribute(self, key: str, value: Any) -> None:
        self.attributes[key] = value

    def add_event(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        timestamp_ns: Optional[int] = None,
    ) -> None:
        self.events.append(
            {
                "name": name,
                "attributes": dict(attributes) if attributes else {},
                "timestamp_ns": timestamp_ns or time.time_ns(),
            }
        )

    def record_exception(self, error: BaseException) -> None:
        self.add_event(
            "exception",
            {
                "exception.type": error.__class__.__name__,
                "exception.message": str(error),
                "exception.stacktrace": "".join(
                    traceback.format_exception(error.__class__, error, error.__traceback__)
                ),
            },
        )
        self.set_status(SpanStatus.ERROR, str(error))

    def set_status(self, status: SpanStatus, description: Optional[str] = None) -> None:
        self.status = status
        self.status_description = description

    def end(self) -> None:
        if self._ended:
            return
        self.end_time_ns = time.time_ns()
        if self.status == SpanStatus.UNSET:
            self.status = SpanStatus.OK
        self._ended = True
        self.tracer._on_span_end(self)

    # Context manager support
    def __enter__(self) -> "Span":
        self._activation_tokens = self.tracer._activate_span(self)
        return self

    def __exit__(self, exc_type, exc, tb) -> bool:
        try:
            if exc:
                self.record_exception(exc)
            self.end()
        finally:
            if self._activation_tokens:
                self.tracer._deactivate_span(self._activation_tokens)
                self._activation_tokens = None
        return False

    async def __aenter__(self) -> "Span":
        self._activation_tokens = self.tracer._activate_span(self)
        return self

    async def __aexit__(self, exc_type, exc, tb) -> bool:
        try:
            if exc:
                self.record_exception(exc)
            self.end()
        finally:
            if self._activation_tokens:
                self.tracer._deactivate_span(self._activation_tokens)
                self._activation_tokens = None
        return False


