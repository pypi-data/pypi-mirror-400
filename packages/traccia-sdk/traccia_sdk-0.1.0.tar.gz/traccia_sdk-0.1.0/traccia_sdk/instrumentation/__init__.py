"""Instrumentation helpers and monkey patching."""

from traccia_sdk.instrumentation.decorator import observe
from traccia_sdk.instrumentation.openai import patch_openai
from traccia_sdk.instrumentation.anthropic import patch_anthropic
from traccia_sdk.instrumentation.requests import patch_requests
from traccia_sdk.instrumentation.http_client import inject_headers as inject_http_headers
from traccia_sdk.instrumentation.http_server import extract_parent_context, start_server_span
from traccia_sdk.instrumentation.fastapi import install_http_middleware

__all__ = [
    "observe",
    "patch_openai",
    "patch_anthropic",
    "patch_requests",
    "inject_http_headers",
    "extract_parent_context",
    "start_server_span",
    "install_http_middleware",
]
