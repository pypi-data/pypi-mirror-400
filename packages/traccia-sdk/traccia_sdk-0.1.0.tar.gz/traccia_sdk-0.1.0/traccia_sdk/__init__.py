"""Python SDK entrypoint for the agent tracing library."""

from traccia_sdk.auto import start_tracing, stop_tracing
from traccia_sdk.tracer import TracerProvider

_global_tracer_provider = TracerProvider()


def get_tracer(name: str):
    """Fetch a tracer from the global provider."""
    return _global_tracer_provider.get_tracer(name)


def set_tracer_provider(provider: TracerProvider) -> None:
    """Override the global tracer provider (primarily for tests or customization)."""
    global _global_tracer_provider
    _global_tracer_provider = provider


def get_tracer_provider() -> TracerProvider:
    return _global_tracer_provider


__all__ = [
    "get_tracer",
    "get_tracer_provider",
    "set_tracer_provider",
    "start_tracing",
    "stop_tracing",
]

