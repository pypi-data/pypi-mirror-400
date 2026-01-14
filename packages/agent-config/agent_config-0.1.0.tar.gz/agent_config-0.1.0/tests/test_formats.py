"""Tests for configuration file format parsing."""

import pytest
from agent_config.formats import parse_json, parse_yaml, detect_format
from pathlib import Path


class TestParseJson:
    """Tests for JSON parsing."""
    
    def test_valid_object(self):
        """Valid JSON object should parse correctly."""
        result = parse_json('{"name": "test", "value": 42}')
        assert result == {"name": "test", "value": 42}
    
    def test_empty_object(self):
        """Empty JSON object should parse to empty dict."""
        result = parse_json('{}')
        assert result == {}
    
    def test_nested_object(self):
        """Nested JSON should parse correctly."""
        result = parse_json('{"outer": {"inner": "value"}}')
        assert result == {"outer": {"inner": "value"}}
    
    def test_array_raises(self):
        """JSON array at root should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_json('[1, 2, 3]')
        assert "JSON object" in str(exc_info.value)
    
    def test_primitive_raises(self):
        """JSON primitive at root should raise ValueError."""
        with pytest.raises(ValueError):
            parse_json('"just a string"')
    
    def test_invalid_json_raises(self):
        """Invalid JSON should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_json('{invalid}')
        assert "Invalid JSON" in str(exc_info.value)


class TestParseYaml:
    """Tests for YAML parsing."""
    
    def test_valid_mapping(self):
        """Valid YAML mapping should parse correctly."""
        result = parse_yaml("name: test\nvalue: 42")
        assert result == {"name": "test", "value": 42}
    
    def test_empty_document(self):
        """Empty YAML document should parse to empty dict."""
        result = parse_yaml("")
        assert result == {}
    
    def test_null_document(self):
        """YAML with just null should parse to empty dict."""
        result = parse_yaml("null")
        assert result == {}
    
    def test_nested_mapping(self):
        """Nested YAML should parse correctly."""
        yaml_content = """
outer:
  inner: value
  list:
    - item1
    - item2
"""
        result = parse_yaml(yaml_content)
        assert result == {
            "outer": {
                "inner": "value",
                "list": ["item1", "item2"]
            }
        }
    
    def test_sequence_raises(self):
        """YAML sequence at root should raise ValueError."""
        with pytest.raises(ValueError) as exc_info:
            parse_yaml("- item1\n- item2")
        assert "YAML mapping" in str(exc_info.value)


class TestDetectFormat:
    """Tests for format detection."""
    
    def test_yaml_extension(self):
        """Files with .yaml extension should be detected as yaml."""
        assert detect_format(Path("config.yaml")) == "yaml"
        assert detect_format(Path("config.YAML")) == "yaml"
    
    def test_yml_extension(self):
        """Files with .yml extension should be detected as yaml."""
        assert detect_format(Path("config.yml")) == "yaml"
    
    def test_json_extension(self):
        """Files with .json extension should be detected as json."""
        assert detect_format(Path("config.json")) == "json"
    
    def test_toml_extension(self):
        """Files with .toml extension should be detected as toml."""
        assert detect_format(Path("config.toml")) == "toml"
    
    def test_unknown_extension(self):
        """Unknown extensions should default to json."""
        assert detect_format(Path(".configrc")) == "json"
