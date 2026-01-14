"""Default configuration values."""

from typing import Any

# Default configuration values
DEFAULTS: dict[str, Any] = {
    "name": None,
    "model": None,
    "temperature": 0.2,
    "top_p": None,
    "max_tokens": None,
    "system_prompt": None,
    "prompt_file": None,
    "tools": [],
    "api_base": None,
    "api_key": None,
    "timeout_ms": 60000,
}


def get_defaults() -> dict[str, Any]:
    """Return a copy of default configuration values."""
    return DEFAULTS.copy()
