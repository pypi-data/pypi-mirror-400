"""Tracer for creating spans and managing the active span stack."""

from __future__ import annotations

from typing import Any, Dict, Optional

from traccia_sdk.context import context as span_context
from traccia_sdk.tracer.span import Span
from traccia_sdk.tracer.span_context import SpanContext
from traccia_sdk import runtime_config


class Tracer:
    def __init__(self, provider: "TracerProvider", instrumentation_scope: str) -> None:
        self._provider = provider
        self.instrumentation_scope = instrumentation_scope

    def start_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        parent: Optional[Span] = None,
        parent_context: Optional[SpanContext] = None,
    ) -> Span:
        parent_span = parent or span_context.get_current_span()
        effective_context = parent_context if parent_context and parent_context.is_valid() else None
        trace_id = (
            parent_span.context.trace_id
            if parent_span
            else (effective_context.trace_id if effective_context else self._provider.generate_trace_id())
        )
        parent_span_id = (
            parent_span.context.span_id
            if parent_span
            else (effective_context.span_id if effective_context else None)
        )
        if parent_span is not None:
            trace_flags = parent_span.context.trace_flags
        elif effective_context is not None:
            trace_flags = effective_context.trace_flags
        else:
            sampler = getattr(self._provider, "sampler", None)
            sampled = True
            if sampler is not None:
                try:
                    sampled = bool(sampler.should_sample().sampled)
                except Exception:
                    sampled = True
            trace_flags = 1 if sampled else 0
        # Debug override: if enabled, force sampling for new traces.
        if parent_span is None and effective_context is None and runtime_config.get_debug():
            trace_flags = 1
        context = SpanContext(
            trace_id=trace_id,
            span_id=self._provider.generate_span_id(),
            trace_flags=trace_flags,
            trace_state=effective_context.trace_state if effective_context else None,
        )
        return Span(
            name=name,
            tracer=self,
            context=context,
            parent_span_id=parent_span_id,
            attributes=attributes,
        )

    def start_as_current_span(
        self,
        name: str,
        attributes: Optional[Dict[str, Any]] = None,
        parent: Optional[Span] = None,
        parent_context: Optional[SpanContext] = None,
    ) -> Span:
        return self.start_span(
            name=name,
            attributes=attributes,
            parent=parent,
            parent_context=parent_context,
        )

    def get_current_span(self) -> Optional[Span]:
        return span_context.get_current_span()

    def _activate_span(self, span: Span):
        return span_context.push_span(span)

    def _deactivate_span(self, tokens) -> None:
        span_context.pop_span(tokens)

    def _on_span_end(self, span: Span) -> None:
        self._provider._notify_span_end(span)

