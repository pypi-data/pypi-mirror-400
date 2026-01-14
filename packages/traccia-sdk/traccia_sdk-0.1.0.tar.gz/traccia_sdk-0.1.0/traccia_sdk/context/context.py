"""Context helpers for managing the active span stack."""

from contextvars import ContextVar, Token
from typing import Optional, Tuple, TYPE_CHECKING

if TYPE_CHECKING:
    from traccia_sdk.tracer.span import Span

# Track the current active span and the stack for nested spans.
_current_span: ContextVar[Optional["Span"]] = ContextVar("current_span", default=None)
_span_stack: ContextVar[Tuple["Span", ...]] = ContextVar("span_stack", default=())


def get_current_span() -> Optional["Span"]:
    """Return the currently active span, if any."""
    return _current_span.get()


def push_span(span: "Span") -> Tuple[Token, Token]:
    """
    Push a span onto the stack and set it as current.

    Returns the tokens needed to restore the previous state.
    """
    stack = _span_stack.get()
    token_stack = _span_stack.set(stack + (span,))
    token_current = _current_span.set(span)
    return token_stack, token_current


def pop_span(tokens: Tuple[Token, Token]) -> None:
    """Restore the previous span stack and current span using the provided tokens."""
    token_stack, token_current = tokens
    _current_span.reset(token_current)
    _span_stack.reset(token_stack)

