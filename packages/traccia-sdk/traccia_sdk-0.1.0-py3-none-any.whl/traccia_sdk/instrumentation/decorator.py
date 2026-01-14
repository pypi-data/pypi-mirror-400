"""@observe decorator for instrumenting functions."""

from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, Dict, Iterable, Optional
from traccia_sdk.tracer.span import SpanStatus


def _capture_args(bound_args: inspect.BoundArguments, skip: Iterable[str]) -> Dict[str, Any]:
    captured = {}
    for name, value in bound_args.arguments.items():
        if name in skip:
            continue
        captured[name] = value
    return captured


def observe(
    name: Optional[str] = None,
    *,
    attributes: Optional[Dict[str, Any]] = None,
    as_type: str = "span",
    skip_args: Optional[Iterable[str]] = None,
    skip_result: bool = False,
) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    """
    Decorate a function to create a span around its execution.

    - Supports sync and async functions.
    - Captures errors and records exception events.
    - Optionally captures arguments/results (skip controls).
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        span_name = name or func.__name__
        arg_names = func.__code__.co_varnames
        skip_args_set = set(skip_args or [])

        is_coro = inspect.iscoroutinefunction(func)

        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            tracer = _get_tracer(func.__module__ or "default")
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()

            span_attrs = dict(attributes or {})
            span_attrs["span.type"] = as_type
            span_attrs.update(_capture_args(bound, skip_args_set))

            with tracer.start_as_current_span(span_name, attributes=span_attrs) as span:
                try:
                    result = func(*args, **kwargs)
                    if not skip_result:
                        span.set_attribute("result", result)
                    return result
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(SpanStatus.ERROR, str(exc))
                    raise

        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            tracer = _get_tracer(func.__module__ or "default")
            bound = inspect.signature(func).bind_partial(*args, **kwargs)
            bound.apply_defaults()

            span_attrs = dict(attributes or {})
            span_attrs["span.type"] = as_type
            span_attrs.update(_capture_args(bound, skip_args_set))

            async with tracer.start_as_current_span(span_name, attributes=span_attrs) as span:
                try:
                    result = await func(*args, **kwargs)
                    if not skip_result:
                        span.set_attribute("result", result)
                    return result
                except Exception as exc:
                    span.record_exception(exc)
                    span.set_status(SpanStatus.ERROR, str(exc))
                    raise

        return async_wrapper if is_coro else sync_wrapper

    return decorator


def _get_tracer(name: str):
    import traccia_sdk

    return traccia_sdk.get_tracer(name)

