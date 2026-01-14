"""Tests for configuration validation."""

import math
import pytest
from agent_config.validate import (
    validate_config,
    ValidationIssue,
    has_errors,
    format_issues,
)


class TestValidateTemperature:
    """Tests for temperature validation."""
    
    def test_valid_temperature(self):
        """Valid temperature values should not produce errors."""
        config = {"temperature": 0.5, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_temperature_zero(self):
        """Temperature of 0 should be valid."""
        config = {"temperature": 0, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_temperature_out_of_range_warns(self):
        """Temperature outside [0, 2] should produce warning."""
        config = {"temperature": 3.0, "model": "test"}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and i.path == "temperature"]
        assert len(warns) == 1
        assert "outside typical range" in warns[0].message
    
    def test_temperature_negative_warns(self):
        """Negative temperature should produce warning."""
        config = {"temperature": -0.5, "model": "test"}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and i.path == "temperature"]
        assert len(warns) == 1
    
    def test_temperature_nan_errors(self):
        """NaN temperature should produce error."""
        config = {"temperature": float("nan"), "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "temperature"]
        assert len(errors) == 1
        assert "finite" in errors[0].message
    
    def test_temperature_infinity_errors(self):
        """Infinity temperature should produce error."""
        config = {"temperature": float("inf"), "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "temperature"]
        assert len(errors) == 1
    
    def test_temperature_wrong_type_errors(self):
        """Non-numeric temperature should produce error."""
        config = {"temperature": "hot", "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "temperature"]
        assert len(errors) == 1
        assert "must be a number" in errors[0].message


class TestValidateTopP:
    """Tests for top_p validation."""
    
    def test_valid_top_p(self):
        """Valid top_p values should not produce errors."""
        config = {"top_p": 0.9, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_top_p_out_of_range_warns(self):
        """top_p outside [0, 1] should produce warning."""
        config = {"top_p": 1.5, "model": "test"}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and i.path == "top_p"]
        assert len(warns) == 1


class TestValidateMaxTokens:
    """Tests for max_tokens validation."""
    
    def test_valid_max_tokens(self):
        """Valid max_tokens should not produce errors."""
        config = {"max_tokens": 1000, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_max_tokens_zero_errors(self):
        """max_tokens of 0 should produce error."""
        config = {"max_tokens": 0, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "max_tokens"]
        assert len(errors) == 1
        assert "must be positive" in errors[0].message
    
    def test_max_tokens_negative_errors(self):
        """Negative max_tokens should produce error."""
        config = {"max_tokens": -100, "model": "test"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "max_tokens"]
        assert len(errors) == 1


class TestValidateTools:
    """Tests for tools validation."""
    
    def test_valid_tools(self):
        """Valid tools array should not produce errors."""
        config = {
            "model": "test",
            "tools": [
                {"name": "search", "enabled": True},
                {"name": "calculator"},
            ]
        }
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error"]
        assert len(errors) == 0
    
    def test_tools_not_list_errors(self):
        """tools as non-list should produce error."""
        config = {"model": "test", "tools": "not a list"}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "tools"]
        assert len(errors) == 1
        assert "must be a list" in errors[0].message
    
    def test_tool_missing_name_errors(self):
        """Tool without name should produce error."""
        config = {"model": "test", "tools": [{"enabled": True}]}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and "name" in (i.path or "")]
        assert len(errors) == 1
        assert "required field" in errors[0].message
    
    def test_tool_empty_name_errors(self):
        """Tool with empty name should produce error."""
        config = {"model": "test", "tools": [{"name": ""}]}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and "name" in (i.path or "")]
        assert len(errors) == 1
        assert "non-empty" in errors[0].message
    
    def test_tool_not_dict_errors(self):
        """Tool that is not a dict should produce error."""
        config = {"model": "test", "tools": ["not a dict"]}
        issues = validate_config(config)
        errors = [i for i in issues if i.level == "error" and i.path == "tools.0"]
        assert len(errors) == 1


class TestValidateModelApiBase:
    """Tests for model/api_base validation."""
    
    def test_neither_set_warns(self):
        """Neither model nor api_base set should produce warning."""
        config = {"temperature": 0.5}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and "model" in i.message]
        assert len(warns) == 1
    
    def test_model_set_no_warning(self):
        """Model set should not produce warning."""
        config = {"model": "gpt-4"}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and "model" in i.message]
        assert len(warns) == 0
    
    def test_api_base_set_no_warning(self):
        """api_base set should not produce warning."""
        config = {"api_base": "https://api.example.com"}
        issues = validate_config(config)
        warns = [i for i in issues if i.level == "warn" and "model" in i.message]
        assert len(warns) == 0


class TestHasErrors:
    """Tests for has_errors function."""
    
    def test_empty_list(self):
        """Empty list should return False."""
        assert has_errors([]) is False
    
    def test_only_warnings(self):
        """Only warnings should return False."""
        issues = [ValidationIssue("warn", "test", "warning")]
        assert has_errors(issues) is False
    
    def test_has_error(self):
        """List with error should return True."""
        issues = [
            ValidationIssue("warn", "test", "warning"),
            ValidationIssue("error", "test", "error"),
        ]
        assert has_errors(issues) is True


class TestFormatIssues:
    """Tests for format_issues function."""
    
    def test_empty_list(self):
        """Empty list should return valid message."""
        result = format_issues([])
        assert "valid" in result.lower()
    
    def test_formats_issue(self):
        """Issues should be formatted with level and path."""
        issues = [ValidationIssue("error", "test.path", "test message")]
        result = format_issues(issues)
        assert "[ERROR]" in result
        assert "test.path" in result
        assert "test message" in result
