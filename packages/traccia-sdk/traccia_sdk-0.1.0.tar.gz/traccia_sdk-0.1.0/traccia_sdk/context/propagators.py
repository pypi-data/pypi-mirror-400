"""W3C trace context propagation helpers (traceparent + tracestate)."""

from __future__ import annotations

import string
from typing import Dict, Optional, Tuple

from traccia_sdk.tracer.span_context import SpanContext

TRACEPARENT_VERSION = "00"
_HEX = set(string.hexdigits.lower())
_TRACESTATE_KEY_CHARS = set("abcdefghijklmnopqrstuvwxyz0123456789_-/@*")


def _is_hex(value: str, length: int) -> bool:
    return len(value) == length and all(ch in _HEX for ch in value.lower())

def _sanitize_tracestate_key(key: str) -> Optional[str]:
    if not key:
        return None
    k = key.strip().lower()
    if not k:
        return None
    # Replace invalid chars with underscore and enforce max length (W3C allows up to 256).
    cleaned = []
    for ch in k:
        cleaned.append(ch if ch in _TRACESTATE_KEY_CHARS else "_")
    out = "".join(cleaned)[:256]
    return out or None


def _sanitize_tracestate_value(value: str) -> str:
    # tracestate value must not contain ',' or '='; keep printable subset.
    v = (value or "").strip()
    v = v.replace(",", "_").replace("=", "_")
    # Enforce max length (256 per W3C).
    return v[:256]


def format_tracestate(state: Dict[str, str]) -> str:
    """
    Format a tracestate header value from a dict.

    Note: this is a simplified formatter; it sanitizes keys/values to remain valid.
    """
    items = []
    for k, v in (state or {}).items():
        sk = _sanitize_tracestate_key(str(k))
        if not sk:
            continue
        items.append(f"{sk}={_sanitize_tracestate_value(str(v))}")
    return ",".join(items)


def parse_tracestate(header_value: str) -> Dict[str, str]:
    """Parse a tracestate header into a dict; invalid entries are ignored."""
    out: Dict[str, str] = {}
    if not header_value:
        return out
    for item in header_value.split(","):
        item = item.strip()
        if not item or "=" not in item:
            continue
        k, v = item.split("=", 1)
        sk = _sanitize_tracestate_key(k)
        if not sk:
            continue
        out[sk] = _sanitize_tracestate_value(v)
    return out


def format_traceparent(context: SpanContext) -> str:
    """Return a traceparent header value for the given SpanContext."""
    flags = f"{context.trace_flags:02x}"
    return f"{TRACEPARENT_VERSION}-{context.trace_id}-{context.span_id}-{flags}"


def inject_traceparent(headers: Dict[str, str], context: SpanContext) -> None:
    """Inject traceparent header into a headers mapping."""
    headers["traceparent"] = format_traceparent(context)

def inject_tracestate(headers: Dict[str, str], context: SpanContext) -> None:
    """Inject tracestate header if present on the context."""
    if context.trace_state:
        headers["tracestate"] = context.trace_state


def parse_traceparent(header_value: str) -> Optional[SpanContext]:
    """Parse a traceparent header into a SpanContext or None if invalid."""
    if not header_value:
        return None
    parts = header_value.split("-")
    if len(parts) != 4:
        return None
    version, trace_id, span_id, flags = parts
    if version != TRACEPARENT_VERSION:
        return None
    if not (_is_hex(trace_id, 32) and _is_hex(span_id, 16) and _is_hex(flags, 2)):
        return None
    return SpanContext(trace_id=trace_id, span_id=span_id, trace_flags=int(flags, 16))


def extract_tracestate(headers: Dict[str, str]) -> Optional[str]:
    """Extract tracestate header value (case-insensitive)."""
    for key, value in headers.items():
        if key.lower() == "tracestate":
            return value
    return None


def extract_trace_context(headers: Dict[str, str]) -> Optional[SpanContext]:
    """
    Extract both traceparent and tracestate and return a combined SpanContext.
    """
    parent = extract_traceparent(headers)
    if parent is None:
        return None
    ts = extract_tracestate(headers)
    if not ts:
        return parent
    return SpanContext(
        trace_id=parent.trace_id,
        span_id=parent.span_id,
        trace_flags=parent.trace_flags,
        trace_state=ts,
    )


def extract_traceparent(headers: Dict[str, str]) -> Optional[SpanContext]:
    """Extract traceparent header from headers and parse it."""
    # Case-insensitive lookup
    for key, value in headers.items():
        if key.lower() == "traceparent":
            return parse_traceparent(value)
    return None

