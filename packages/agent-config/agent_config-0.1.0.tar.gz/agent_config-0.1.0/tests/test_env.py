"""Tests for environment variable handling."""

import pytest
from agent_config.env import (
    load_from_env,
    parse_env_value,
    get_env_var_for_key,
    EnvParseError,
    ENV_MAPPING,
)


class TestParseEnvValue:
    """Tests for parse_env_value function."""
    
    def test_parse_string(self):
        """String values should pass through unchanged."""
        assert parse_env_value("hello", "str", "TEST") == "hello"
        assert parse_env_value("", "str", "TEST") == ""
    
    def test_parse_int(self):
        """Integer values should be converted."""
        assert parse_env_value("42", "int", "TEST") == 42
        assert parse_env_value("-10", "int", "TEST") == -10
        assert parse_env_value("0", "int", "TEST") == 0
    
    def test_parse_int_invalid(self):
        """Invalid integers should raise EnvParseError."""
        with pytest.raises(EnvParseError) as exc_info:
            parse_env_value("not-a-number", "int", "TEST_VAR")
        
        assert exc_info.value.var_name == "TEST_VAR"
        assert exc_info.value.expected_type == "int"
    
    def test_parse_float(self):
        """Float values should be converted."""
        assert parse_env_value("0.5", "float", "TEST") == 0.5
        assert parse_env_value("1.0", "float", "TEST") == 1.0
        assert parse_env_value("-0.1", "float", "TEST") == -0.1
        assert parse_env_value("42", "float", "TEST") == 42.0
    
    def test_parse_float_invalid(self):
        """Invalid floats should raise EnvParseError."""
        with pytest.raises(EnvParseError):
            parse_env_value("not-a-float", "float", "TEST")
    
    def test_parse_json(self):
        """JSON values should be parsed."""
        assert parse_env_value('{"key": "value"}', "json", "TEST") == {"key": "value"}
        assert parse_env_value('[1, 2, 3]', "json", "TEST") == [1, 2, 3]
        assert parse_env_value('null', "json", "TEST") is None
    
    def test_parse_json_invalid(self):
        """Invalid JSON should raise EnvParseError."""
        with pytest.raises(EnvParseError):
            parse_env_value('{invalid json}', "json", "TEST")


class TestLoadFromEnv:
    """Tests for load_from_env function."""
    
    def test_empty_env(self):
        """Empty environment should return empty dict."""
        result = load_from_env({})
        assert result == {}
    
    def test_load_string_values(self):
        """String environment variables should be loaded."""
        env = {
            "AGENT_NAME": "test-agent",
            "AGENT_MODEL": "gpt-4",
        }
        result = load_from_env(env)
        assert result["name"] == "test-agent"
        assert result["model"] == "gpt-4"
    
    def test_load_numeric_values(self):
        """Numeric environment variables should be converted."""
        env = {
            "AGENT_TEMPERATURE": "0.7",
            "AGENT_MAX_TOKENS": "1000",
            "AGENT_TIMEOUT_MS": "30000",
        }
        result = load_from_env(env)
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 1000
        assert result["timeout_ms"] == 30000
    
    def test_load_tools_json(self):
        """AGENT_TOOLS_JSON should be parsed as JSON array."""
        env = {
            "AGENT_TOOLS_JSON": '[{"name": "search", "enabled": true}]',
        }
        result = load_from_env(env)
        assert result["tools"] == [{"name": "search", "enabled": True}]
    
    def test_ignores_unrelated_env_vars(self):
        """Unrelated environment variables should be ignored."""
        env = {
            "PATH": "/usr/bin",
            "HOME": "/home/user",
            "AGENT_MODEL": "gpt-4",
        }
        result = load_from_env(env)
        assert "PATH" not in result
        assert "HOME" not in result
        assert result["model"] == "gpt-4"
    
    def test_invalid_env_value_raises(self):
        """Invalid environment variable values should raise EnvParseError."""
        env = {"AGENT_TEMPERATURE": "not-a-float"}
        with pytest.raises(EnvParseError):
            load_from_env(env)


class TestGetEnvVarForKey:
    """Tests for get_env_var_for_key function."""
    
    def test_known_keys(self):
        """Known config keys should return correct env var names."""
        assert get_env_var_for_key("model") == "AGENT_MODEL"
        assert get_env_var_for_key("temperature") == "AGENT_TEMPERATURE"
        assert get_env_var_for_key("api_key") == "AGENT_API_KEY"
    
    def test_unknown_key(self):
        """Unknown config keys should return None."""
        assert get_env_var_for_key("unknown_key") is None
        assert get_env_var_for_key("") is None
