"""Initialization helpers for wiring tracer provider, processors, and patches."""

from __future__ import annotations

import atexit
import inspect
import os
from pathlib import Path
from typing import Optional

from traccia_sdk.exporter import HttpExporter, ConsoleExporter
from traccia_sdk.exporter.http_exporter import DEFAULT_ENDPOINT
from traccia_sdk.instrumentation import patch_anthropic, patch_openai, patch_requests
from traccia_sdk.processors import (
    BatchSpanProcessor,
    Sampler,
    TokenCountingProcessor,
    CostAnnotatingProcessor,
    LoggingSpanProcessor,
    AgentEnrichmentProcessor,
)
from traccia_sdk import pricing_config
import threading
import time
from traccia_sdk.tracer.provider import TracerProvider
from traccia_sdk import config as sdk_config
from traccia_sdk import runtime_config
from traccia_sdk import auto_instrumentation

_started = False
_registered_shutdown = False
_active_processor: Optional[BatchSpanProcessor] = None


def start_tracing(
    *,
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    sample_rate: float = 1.0,
    max_queue_size: int = 5000,
    max_export_batch_size: int = 512,
    schedule_delay_millis: int = 5000,
    exporter: Optional[HttpExporter] = None,
    transport=None,
    enable_patching: bool = True,
    enable_token_counting: bool = True,
    enable_costs: bool = True,
    pricing_override=None,
    pricing_refresh_seconds: Optional[int] = None,
    enable_console_exporter: bool = False,
    load_env: bool = True,
    enable_span_logging: bool = False,
    auto_instrument_tools: bool = False,
    tool_include: Optional[list] = None,
    max_tool_spans: int = 100,
    max_span_depth: int = 10,
    session_id: Optional[str] = None,
    user_id: Optional[str] = None,
    tenant_id: Optional[str] = None,
    project_id: Optional[str] = None,
    debug: bool = False,
    attr_truncation_limit: Optional[int] = None,
) -> TracerProvider:
    """
    Initialize global tracing:
    - Builds HttpExporter (or uses provided one)
    - Attaches BatchSpanProcessor with sampling and bounded queue
    - Registers monkey patches (OpenAI, Anthropic, requests)
    - Registers atexit shutdown hook
    """
    global _started, _active_processor
    if _started:
        return _get_provider()

    if load_env:
        sdk_config.load_dotenv()
    env_cfg = sdk_config.load_config(
        {"api_key": api_key, "endpoint": endpoint, "sample_rate": str(sample_rate)}
    )

    # Resolve agent configuration path automatically if not provided by env.
    agent_cfg_path = _resolve_agent_config_path()
    if agent_cfg_path:
        os.environ.setdefault("AGENT_DASHBOARD_AGENT_CONFIG", agent_cfg_path)

    provider = _get_provider()
    key = env_cfg.get("api_key") or api_key
    endpoint = env_cfg.get("endpoint") or endpoint
    try:
        sample_rate = float(env_cfg.get("sample_rate", sample_rate))
    except Exception:
        sample_rate = sample_rate

    # Set runtime config for auto-instrumentation
    runtime_config.set_auto_instrument_tools(auto_instrument_tools)
    runtime_config.set_tool_include(tool_include or [])
    runtime_config.set_max_tool_spans(max_tool_spans)
    runtime_config.set_max_span_depth(max_span_depth)
    runtime_config.set_session_id(session_id)
    runtime_config.set_user_id(user_id)
    runtime_config.set_tenant_id(_resolve_tenant_id(tenant_id))
    runtime_config.set_project_id(_resolve_project_id(project_id))
    runtime_config.set_debug(_resolve_debug(debug))
    runtime_config.set_attr_truncation_limit(attr_truncation_limit)

    network_exporter = exporter or HttpExporter(
        endpoint=endpoint or DEFAULT_ENDPOINT,
        api_key=key,
        transport=transport,
    )

    if enable_console_exporter:
        network_exporter = _combine_exporters(network_exporter, ConsoleExporter())

    sampler = Sampler(sample_rate)
    # Use the sampler at trace start (head sampling) and also to make the
    # batch processor respect trace_flags.
    try:
        provider.set_sampler(sampler)
    except Exception:
        pass

    # Ordering matters: enrich spans before batching/export.
    if enable_token_counting:
        provider.add_span_processor(TokenCountingProcessor())
    cost_processor = None
    if enable_costs:
        pricing_table, pricing_source = pricing_config.load_pricing_with_source(pricing_override)
        cost_processor = CostAnnotatingProcessor(
            pricing_table=pricing_table, pricing_source=pricing_source
        )
        provider.add_span_processor(cost_processor)
    if enable_span_logging:
        provider.add_span_processor(LoggingSpanProcessor())
    # Agent enrichment should run after cost/token processors so it can fill any gaps.
    provider.add_span_processor(
        AgentEnrichmentProcessor(agent_config_path=os.getenv("AGENT_DASHBOARD_AGENT_CONFIG"))
    )

    processor = BatchSpanProcessor(
        exporter=network_exporter,
        sampler=sampler,
        max_queue_size=max_queue_size,
        max_export_batch_size=max_export_batch_size,
        schedule_delay_millis=schedule_delay_millis,
    )
    provider.add_span_processor(processor)
    _active_processor = processor

    _register_shutdown(provider, processor)
    _start_pricing_refresh(cost_processor, pricing_override, pricing_refresh_seconds)

    # Auto-instrument in-repo functions/tools if enabled
    if auto_instrument_tools and tool_include:
        try:
            auto_instrumentation.instrument_functions(tool_include or [])
        except Exception:
            pass

    if enable_patching:
        try:
            patch_openai()
        except Exception:
            pass
        try:
            patch_anthropic()
        except Exception:
            pass
        try:
            patch_requests()
        except Exception:
            pass

    _started = True
    return provider


def stop_tracing(flush_timeout: Optional[float] = None) -> None:
    """Force flush and shutdown registered processors and provider."""
    global _started
    _stop_pricing_refresh()
    provider = _get_provider()
    if _active_processor:
        try:
            _active_processor.force_flush(timeout=flush_timeout)
        finally:
            _active_processor.shutdown()
    provider.shutdown()
    _started = False


def _register_shutdown(provider: TracerProvider, processor: BatchSpanProcessor) -> None:
    global _registered_shutdown
    if _registered_shutdown:
        return

    def _cleanup():
        try:
            processor.force_flush()
        finally:
            processor.shutdown()
        provider.shutdown()

    atexit.register(_cleanup)
    _registered_shutdown = True


def _get_provider() -> TracerProvider:
    import traccia_sdk

    return traccia_sdk.get_tracer_provider()


def _resolve_agent_config_path() -> Optional[str]:
    """
    Locate agent_config.json for users automatically:
      1) Respect AGENT_DASHBOARD_AGENT_CONFIG if set and file exists
      2) Use ./agent_config.json from current working directory if present
      3) Try to find agent_config.json adjacent to the first non-sdk caller
    """
    env_path = os.getenv("AGENT_DASHBOARD_AGENT_CONFIG")
    if env_path:
        path = Path(env_path)
        if path.exists():
            return str(path.resolve())

    cwd_path = Path.cwd() / "agent_config.json"
    if cwd_path.exists():
        return str(cwd_path.resolve())

    try:
        for frame in inspect.stack():
            frame_path = Path(frame.filename)
            # Skip SDK internal files
            if "traccia_sdk" in frame_path.parts:
                continue
            candidate = frame_path.parent / "agent_config.json"
            if candidate.exists():
                return str(candidate.resolve())
    except Exception:
        return None
    return None


def _resolve_debug(cli_value: bool) -> bool:
    raw = os.getenv("AGENT_DASHBOARD_DEBUG")
    if raw is None:
        return bool(cli_value)
    return raw.strip().lower() in {"1", "true", "yes", "y", "on"}


def _resolve_tenant_id(cli_value: Optional[str]) -> str:
    return (
        cli_value
        or os.getenv("AGENT_DASHBOARD_TENANT_ID")
        or "study-agent-sf23jj56c34234"
    )


def _resolve_project_id(cli_value: Optional[str]) -> str:
    return cli_value or os.getenv("AGENT_DASHBOARD_PROJECT_ID") or "gmail"


def _combine_exporters(primary, secondary):
    if primary is None:
        return secondary
    if secondary is None:
        return primary

    class _Multi:
        def export(self, spans):
            ok1 = primary.export(spans)
            ok2 = secondary.export(spans)
            return ok1 and ok2

        def shutdown(self):
            for exp in (primary, secondary):
                if hasattr(exp, "shutdown"):
                    exp.shutdown()

    return _Multi()


_pricing_refresh_stop: Optional[threading.Event] = None
_pricing_refresh_thread: Optional[threading.Thread] = None


def _start_pricing_refresh(cost_processor: Optional[CostAnnotatingProcessor], override, interval: Optional[int]) -> None:
    global _pricing_refresh_stop, _pricing_refresh_thread
    if not cost_processor or not interval or interval <= 0:
        return
    _pricing_refresh_stop = threading.Event()

    def _loop():
        while not _pricing_refresh_stop.is_set():
            time.sleep(interval)
            if _pricing_refresh_stop.is_set():
                break
            try:
                table, source = pricing_config.load_pricing_with_source(override)
                cost_processor.update_pricing_table(table, pricing_source=source)
            except Exception:
                continue

    _pricing_refresh_thread = threading.Thread(target=_loop, daemon=True)
    _pricing_refresh_thread.start()


def _stop_pricing_refresh() -> None:
    if _pricing_refresh_stop:
        _pricing_refresh_stop.set()
    if _pricing_refresh_thread:
        _pricing_refresh_thread.join(timeout=1)

