"""Tests for default configuration values."""

import pytest
from agent_config.defaults import get_defaults, DEFAULTS


def test_get_defaults_returns_copy():
    """get_defaults should return a copy, not the original."""
    defaults1 = get_defaults()
    defaults2 = get_defaults()
    
    # Modify one copy
    defaults1["name"] = "modified"
    
    # Other copy should be unchanged
    assert defaults2["name"] is None


def test_default_temperature():
    """Default temperature should be 0.2."""
    defaults = get_defaults()
    assert defaults["temperature"] == 0.2


def test_default_timeout_ms():
    """Default timeout_ms should be 60000."""
    defaults = get_defaults()
    assert defaults["timeout_ms"] == 60000


def test_default_tools():
    """Default tools should be an empty list."""
    defaults = get_defaults()
    assert defaults["tools"] == []


def test_defaults_has_expected_keys():
    """Defaults should have all expected keys."""
    defaults = get_defaults()
    expected_keys = {
        "name", "model", "temperature", "top_p", "max_tokens",
        "system_prompt", "prompt_file", "tools",
        "api_base", "api_key", "timeout_ms"
    }
    assert set(defaults.keys()) == expected_keys
