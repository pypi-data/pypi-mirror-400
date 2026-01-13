"""Configuration helpers for the EdgeAI SDK."""

from __future__ import annotations

import os

_DEFAULT_BACKEND_URL = "https://studio.edgeai.zededa.dev"


def get_service_url() -> str:
    """Return the configured EdgeAI service URL.

    The value is read from environment variables to match runtime configuration.
    Prefers EDGEAI_BACKEND_URL (set by login command) over EDGEAI_SERVICE_URL.
    """

    service_url = os.getenv("EDGEAI_BACKEND_URL") or os.getenv("EDGEAI_SERVICE_URL", _DEFAULT_BACKEND_URL)
    return service_url.rstrip("/")
