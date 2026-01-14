"""Configuration helpers including lightweight .env support."""

from __future__ import annotations

import os
from typing import Dict, Optional


def load_dotenv(path: str = ".env") -> None:
    """Minimal .env loader (no external dependency)."""
    if not os.path.exists(path):
        return
    try:
        with open(path, "r", encoding="utf-8") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" not in line:
                    continue
                key, value = line.split("=", 1)
                key, value = key.strip(), value.strip().strip("\"'")
                if key and key not in os.environ:
                    os.environ[key] = value
    except Exception:
        # Fail silently; this loader is best-effort.
        return


def load_config(overrides: Optional[Dict[str, str]] = None) -> Dict[str, str]:
    """
    Load configuration from environment (optionally after load_dotenv).

    Recognized keys:
      - AGENT_DASHBOARD_API_KEY
      - AGENT_DASHBOARD_ENDPOINT
      - AGENT_DASHBOARD_SAMPLE_RATE
    """
    cfg = {
        "api_key": os.getenv("AGENT_DASHBOARD_API_KEY"),
        "endpoint": os.getenv("AGENT_DASHBOARD_ENDPOINT"),
        "sample_rate": os.getenv("AGENT_DASHBOARD_SAMPLE_RATE"),
    }
    if overrides:
        cfg.update({k: v for k, v in overrides.items() if v is not None})
    return cfg

