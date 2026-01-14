"""Runtime configuration shared across instrumentation and exporters.

This module intentionally keeps state minimal and process-local. It is used to
configure optional auto-instrumentation behavior and safe serialization limits.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class _RuntimeConfig:
    auto_instrument_tools: bool = False
    tool_include: List[str] = field(default_factory=list)
    max_tool_spans: int = 100
    max_span_depth: int = 10
    session_id: Optional[str] = None
    user_id: Optional[str] = None
    tenant_id: Optional[str] = None
    project_id: Optional[str] = None
    debug: bool = False
    attr_truncation_limit: Optional[int] = None


_CFG = _RuntimeConfig()


def set_auto_instrument_tools(value: bool) -> None:
    _CFG.auto_instrument_tools = bool(value)


def get_auto_instrument_tools() -> bool:
    return _CFG.auto_instrument_tools


def set_tool_include(values: List[str]) -> None:
    _CFG.tool_include = list(values or [])


def get_tool_include() -> List[str]:
    return list(_CFG.tool_include)


def set_max_tool_spans(value: int) -> None:
    _CFG.max_tool_spans = int(value)


def get_max_tool_spans() -> int:
    return _CFG.max_tool_spans


def set_max_span_depth(value: int) -> None:
    _CFG.max_span_depth = int(value)


def get_max_span_depth() -> int:
    return _CFG.max_span_depth


def set_session_id(value: Optional[str]) -> None:
    _CFG.session_id = value


def get_session_id() -> Optional[str]:
    return _CFG.session_id


def set_user_id(value: Optional[str]) -> None:
    _CFG.user_id = value


def get_user_id() -> Optional[str]:
    return _CFG.user_id


def set_tenant_id(value: Optional[str]) -> None:
    _CFG.tenant_id = value


def get_tenant_id() -> Optional[str]:
    return _CFG.tenant_id


def set_project_id(value: Optional[str]) -> None:
    _CFG.project_id = value


def get_project_id() -> Optional[str]:
    return _CFG.project_id


def set_debug(value: bool) -> None:
    _CFG.debug = bool(value)


def get_debug() -> bool:
    return bool(_CFG.debug)


def set_attr_truncation_limit(value: Optional[int]) -> None:
    _CFG.attr_truncation_limit = int(value) if value is not None else None


def get_attr_truncation_limit() -> Optional[int]:
    return _CFG.attr_truncation_limit


