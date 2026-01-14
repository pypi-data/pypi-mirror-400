"""Tests for configuration loading."""

import json
import pytest
from pathlib import Path
from agent_config.load import (
    load_config,
    discover_config_file,
    normalize_config,
    merge_configs,
    redact_config,
    get_value_by_path,
    ConfigError,
    CONFIG_FILES,
)


class TestDiscoverConfigFile:
    """Tests for config file discovery."""
    
    def test_no_config_file(self, tmp_path):
        """No config file should return None."""
        result = discover_config_file(tmp_path)
        assert result is None
    
    def test_finds_yaml(self, tmp_path):
        """Should find agent.config.yaml."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test")
        
        result = discover_config_file(tmp_path)
        assert result == config_file
    
    def test_finds_yml(self, tmp_path):
        """Should find agent.config.yml."""
        config_file = tmp_path / "agent.config.yml"
        config_file.write_text("name: test")
        
        result = discover_config_file(tmp_path)
        assert result == config_file
    
    def test_finds_json(self, tmp_path):
        """Should find agent.config.json."""
        config_file = tmp_path / "agent.config.json"
        config_file.write_text('{"name": "test"}')
        
        result = discover_config_file(tmp_path)
        assert result == config_file
    
    def test_yaml_takes_precedence(self, tmp_path):
        """YAML should take precedence over JSON."""
        yaml_file = tmp_path / "agent.config.yaml"
        json_file = tmp_path / "agent.config.json"
        yaml_file.write_text("name: yaml")
        json_file.write_text('{"name": "json"}')
        
        result = discover_config_file(tmp_path)
        assert result == yaml_file


class TestNormalizeConfig:
    """Tests for config normalization."""
    
    def test_coerce_temperature(self):
        """Should coerce temperature to float."""
        config = {"temperature": "0.5"}
        result = normalize_config(config)
        assert result["temperature"] == 0.5
        assert isinstance(result["temperature"], float)
    
    def test_coerce_max_tokens(self):
        """Should coerce max_tokens to int."""
        config = {"max_tokens": "1000"}
        result = normalize_config(config)
        assert result["max_tokens"] == 1000
        assert isinstance(result["max_tokens"], int)
    
    def test_tools_default_enabled(self):
        """Should default enabled to True for tools."""
        config = {"tools": [{"name": "search"}]}
        result = normalize_config(config)
        assert result["tools"][0]["enabled"] is True
    
    def test_tools_preserve_enabled(self):
        """Should preserve explicit enabled value."""
        config = {"tools": [{"name": "search", "enabled": False}]}
        result = normalize_config(config)
        assert result["tools"][0]["enabled"] is False
    
    def test_preserves_unknown_keys(self):
        """Should preserve unknown keys."""
        config = {"custom_key": "custom_value"}
        result = normalize_config(config)
        assert result["custom_key"] == "custom_value"


class TestMergeConfigs:
    """Tests for config merging."""
    
    def test_later_overrides_earlier(self):
        """Later configs should override earlier ones."""
        result = merge_configs(
            {"name": "first", "model": "a"},
            {"name": "second"},
        )
        assert result["name"] == "second"
        assert result["model"] == "a"
    
    def test_none_does_not_override(self):
        """None values should not override existing values."""
        result = merge_configs(
            {"name": "first"},
            {"name": None},
        )
        assert result["name"] == "first"
    
    def test_three_way_merge(self):
        """Should support three-way merge."""
        result = merge_configs(
            {"a": 1, "b": 2, "c": 3},
            {"b": 20},
            {"c": 300},
        )
        assert result == {"a": 1, "b": 20, "c": 300}


class TestRedactConfig:
    """Tests for config redaction."""
    
    def test_redacts_api_key(self):
        """Should redact api_key."""
        config = {"api_key": "sk-secret123"}
        result = redact_config(config)
        assert "***" in result["api_key"]
        assert "sk-secret123" not in result["api_key"]
    
    def test_redacts_token(self):
        """Should redact fields with 'token' in name."""
        config = {"auth_token": "secret", "model": "gpt-4"}
        result = redact_config(config)
        assert "***" in result["auth_token"]
        assert result["model"] == "gpt-4"
    
    def test_redacts_nested(self):
        """Should redact nested sensitive fields."""
        config = {
            "credentials": {
                "api_key": "secret",
                "name": "test"
            }
        }
        result = redact_config(config)
        assert "***" in result["credentials"]["api_key"]
        assert result["credentials"]["name"] == "test"
    
    def test_preserves_none(self):
        """Should preserve None values."""
        config = {"api_key": None}
        result = redact_config(config)
        assert result["api_key"] is None


class TestGetValueByPath:
    """Tests for dot-path value access."""
    
    def test_simple_key(self):
        """Should get simple key."""
        config = {"name": "test"}
        value, found = get_value_by_path(config, "name")
        assert found is True
        assert value == "test"
    
    def test_nested_key(self):
        """Should get nested key."""
        config = {"outer": {"inner": "value"}}
        value, found = get_value_by_path(config, "outer.inner")
        assert found is True
        assert value == "value"
    
    def test_array_index(self):
        """Should get array element by index."""
        config = {"tools": [{"name": "first"}, {"name": "second"}]}
        value, found = get_value_by_path(config, "tools.1.name")
        assert found is True
        assert value == "second"
    
    def test_missing_key(self):
        """Should return (None, False) for missing key."""
        config = {"name": "test"}
        value, found = get_value_by_path(config, "missing")
        assert found is False
        assert value is None
    
    def test_missing_nested_key(self):
        """Should return (None, False) for missing nested key."""
        config = {"outer": {"inner": "value"}}
        value, found = get_value_by_path(config, "outer.missing")
        assert found is False
    
    def test_index_out_of_range(self):
        """Should return (None, False) for out of range index."""
        config = {"tools": [{"name": "only"}]}
        value, found = get_value_by_path(config, "tools.5.name")
        assert found is False


class TestLoadConfig:
    """Tests for load_config function."""
    
    def test_loads_defaults_without_file(self, tmp_path):
        """Should load defaults when no file exists."""
        config = load_config(cwd=str(tmp_path))
        assert "temperature" in config
        assert config["temperature"] == 0.2
    
    def test_strict_mode_fails_without_file(self, tmp_path):
        """Strict mode should fail when no file exists."""
        with pytest.raises(ConfigError):
            load_config(cwd=str(tmp_path), strict=True)
    
    def test_loads_yaml_file(self, tmp_path):
        """Should load YAML config file."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test-agent\nmodel: gpt-4")
        
        config = load_config(cwd=str(tmp_path))
        assert config["name"] == "test-agent"
        assert config["model"] == "gpt-4"
    
    def test_loads_json_file(self, tmp_path):
        """Should load JSON config file."""
        config_file = tmp_path / "agent.config.json"
        config_file.write_text('{"name": "json-agent", "model": "gpt-4"}')
        
        config = load_config(cwd=str(tmp_path))
        assert config["name"] == "json-agent"
    
    def test_env_overrides_file(self, tmp_path):
        """Environment should override file values."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: file-model")
        
        env = {"AGENT_MODEL": "env-model"}
        config = load_config(cwd=str(tmp_path), env=env)
        assert config["model"] == "env-model"
    
    def test_no_env_flag(self, tmp_path):
        """use_env=False should ignore environment."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: file-model")
        
        env = {"AGENT_MODEL": "env-model"}
        config = load_config(cwd=str(tmp_path), env=env, use_env=False)
        assert config["model"] == "file-model"
    
    def test_explicit_file_path(self, tmp_path):
        """Should load explicit file path."""
        config_file = tmp_path / "custom.yaml"
        config_file.write_text("name: custom")
        
        config = load_config(file=str(config_file))
        assert config["name"] == "custom"
    
    def test_file_not_found(self, tmp_path):
        """Should raise FileNotFoundError for missing explicit file."""
        with pytest.raises(FileNotFoundError):
            load_config(file=str(tmp_path / "nonexistent.yaml"))
    
    def test_validation_errors_raise(self, tmp_path):
        """Validation errors should raise ConfigError."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("max_tokens: -100\nmodel: test")
        
        with pytest.raises(ConfigError) as exc_info:
            load_config(cwd=str(tmp_path))
        
        assert len(exc_info.value.issues) > 0
    
    def test_redact_option(self, tmp_path):
        """redact=True should mask sensitive values."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("api_key: secret123\nmodel: test")
        
        config = load_config(cwd=str(tmp_path), redact=True)
        assert "secret123" not in config["api_key"]
        assert "***" in config["api_key"]
