"""Configuration validation for agent configurations."""

import math
from dataclasses import dataclass
from typing import Any, Literal


@dataclass
class ValidationIssue:
    """Represents a validation issue found in configuration.
    
    Attributes:
        level: Severity level - 'error' for blocking issues, 'warn' for warnings.
        path: Dot-notation path to the problematic value (e.g., 'tools.0.name').
        message: Human-readable description of the issue.
    """
    level: Literal["error", "warn"]
    path: str | None
    message: str
    
    def __str__(self) -> str:
        prefix = f"[{self.level.upper()}]"
        if self.path:
            return f"{prefix} {self.path}: {self.message}"
        return f"{prefix} {self.message}"


def validate_config(config: dict[str, Any]) -> list[ValidationIssue]:
    """Validate an agent configuration dictionary.
    
    Checks for:
    - Type correctness of known fields
    - Value ranges (temperature, top_p, max_tokens, timeout_ms)
    - Structure of tools array
    - Warnings for missing recommended fields
    
    Args:
        config: Configuration dictionary to validate.
        
    Returns:
        List of validation issues found. Empty list means valid config.
    """
    issues: list[ValidationIssue] = []
    
    # Validate temperature
    if "temperature" in config and config["temperature"] is not None:
        temp = config["temperature"]
        if not isinstance(temp, (int, float)):
            issues.append(ValidationIssue(
                level="error",
                path="temperature",
                message=f"must be a number, got {type(temp).__name__}"
            ))
        elif not math.isfinite(temp):
            issues.append(ValidationIssue(
                level="error",
                path="temperature",
                message="must be a finite number"
            ))
        elif temp < 0 or temp > 2:
            issues.append(ValidationIssue(
                level="warn",
                path="temperature",
                message=f"value {temp} is outside typical range [0, 2]"
            ))
    
    # Validate top_p
    if "top_p" in config and config["top_p"] is not None:
        top_p = config["top_p"]
        if not isinstance(top_p, (int, float)):
            issues.append(ValidationIssue(
                level="error",
                path="top_p",
                message=f"must be a number, got {type(top_p).__name__}"
            ))
        elif not math.isfinite(top_p):
            issues.append(ValidationIssue(
                level="error",
                path="top_p",
                message="must be a finite number"
            ))
        elif top_p < 0 or top_p > 1:
            issues.append(ValidationIssue(
                level="warn",
                path="top_p",
                message=f"value {top_p} is outside typical range [0, 1]"
            ))
    
    # Validate max_tokens
    if "max_tokens" in config and config["max_tokens"] is not None:
        max_tokens = config["max_tokens"]
        if not isinstance(max_tokens, int):
            issues.append(ValidationIssue(
                level="error",
                path="max_tokens",
                message=f"must be an integer, got {type(max_tokens).__name__}"
            ))
        elif max_tokens <= 0:
            issues.append(ValidationIssue(
                level="error",
                path="max_tokens",
                message=f"must be positive, got {max_tokens}"
            ))
    
    # Validate timeout_ms
    if "timeout_ms" in config and config["timeout_ms"] is not None:
        timeout = config["timeout_ms"]
        if not isinstance(timeout, int):
            issues.append(ValidationIssue(
                level="error",
                path="timeout_ms",
                message=f"must be an integer, got {type(timeout).__name__}"
            ))
        elif timeout <= 0:
            issues.append(ValidationIssue(
                level="error",
                path="timeout_ms",
                message=f"must be positive, got {timeout}"
            ))
    
    # Validate tools
    if "tools" in config and config["tools"] is not None:
        tools = config["tools"]
        if not isinstance(tools, list):
            issues.append(ValidationIssue(
                level="error",
                path="tools",
                message=f"must be a list, got {type(tools).__name__}"
            ))
        else:
            for i, tool in enumerate(tools):
                tool_path = f"tools.{i}"
                if not isinstance(tool, dict):
                    issues.append(ValidationIssue(
                        level="error",
                        path=tool_path,
                        message=f"must be an object, got {type(tool).__name__}"
                    ))
                    continue
                
                # Check for required 'name' field
                if "name" not in tool:
                    issues.append(ValidationIssue(
                        level="error",
                        path=f"{tool_path}.name",
                        message="required field 'name' is missing"
                    ))
                elif not isinstance(tool["name"], str):
                    issues.append(ValidationIssue(
                        level="error",
                        path=f"{tool_path}.name",
                        message=f"must be a string, got {type(tool['name']).__name__}"
                    ))
                elif not tool["name"].strip():
                    issues.append(ValidationIssue(
                        level="error",
                        path=f"{tool_path}.name",
                        message="must be a non-empty string"
                    ))
                
                # Validate 'enabled' if present
                if "enabled" in tool and tool["enabled"] is not None:
                    if not isinstance(tool["enabled"], bool):
                        issues.append(ValidationIssue(
                            level="error",
                            path=f"{tool_path}.enabled",
                            message=f"must be a boolean, got {type(tool['enabled']).__name__}"
                        ))
                
                # Validate 'config' if present
                if "config" in tool and tool["config"] is not None:
                    if not isinstance(tool["config"], dict):
                        issues.append(ValidationIssue(
                            level="error",
                            path=f"{tool_path}.config",
                            message=f"must be an object, got {type(tool['config']).__name__}"
                        ))
    
    # Warning if neither model nor api_base is set
    model = config.get("model")
    api_base = config.get("api_base")
    if not model and not api_base:
        issues.append(ValidationIssue(
            level="warn",
            path=None,
            message="neither 'model' nor 'api_base' is set"
        ))
    
    return issues


def has_errors(issues: list[ValidationIssue]) -> bool:
    """Check if any issues are errors (not just warnings).
    
    Args:
        issues: List of validation issues.
        
    Returns:
        True if any issue has level 'error'.
    """
    return any(issue.level == "error" for issue in issues)


def format_issues(issues: list[ValidationIssue]) -> str:
    """Format validation issues for display.
    
    Args:
        issues: List of validation issues.
        
    Returns:
        Formatted string with one issue per line.
    """
    if not issues:
        return "Configuration is valid."
    return "\n".join(str(issue) for issue in issues)
