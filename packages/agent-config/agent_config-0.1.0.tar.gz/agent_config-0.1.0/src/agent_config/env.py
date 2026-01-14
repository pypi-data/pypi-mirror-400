"""Environment variable handling for agent configuration."""

import json
import os
from typing import Any

# Mapping of environment variables to config keys
ENV_MAPPING: dict[str, tuple[str, str]] = {
    # env_var: (config_key, type)
    "AGENT_NAME": ("name", "str"),
    "AGENT_MODEL": ("model", "str"),
    "AGENT_TEMPERATURE": ("temperature", "float"),
    "AGENT_TOP_P": ("top_p", "float"),
    "AGENT_MAX_TOKENS": ("max_tokens", "int"),
    "AGENT_SYSTEM_PROMPT": ("system_prompt", "str"),
    "AGENT_PROMPT_FILE": ("prompt_file", "str"),
    "AGENT_API_BASE": ("api_base", "str"),
    "AGENT_API_KEY": ("api_key", "str"),
    "AGENT_TIMEOUT_MS": ("timeout_ms", "int"),
    "AGENT_TOOLS_JSON": ("tools", "json"),
}


class EnvParseError(Exception):
    """Raised when an environment variable cannot be parsed."""
    
    def __init__(self, var_name: str, expected_type: str, value: str, error: str):
        self.var_name = var_name
        self.expected_type = expected_type
        self.value = value
        self.error = error
        super().__init__(
            f"Failed to parse environment variable {var_name} as {expected_type}: {error}"
        )


def parse_env_value(value: str, expected_type: str, var_name: str) -> Any:
    """Parse an environment variable value to the expected type.
    
    Args:
        value: The string value from the environment.
        expected_type: The expected type ('str', 'int', 'float', 'json').
        var_name: The environment variable name (for error messages).
        
    Returns:
        The parsed value.
        
    Raises:
        EnvParseError: If the value cannot be parsed.
    """
    if expected_type == "str":
        return value
    
    elif expected_type == "int":
        try:
            return int(value)
        except ValueError:
            raise EnvParseError(var_name, "int", value, f"'{value}' is not a valid integer")
    
    elif expected_type == "float":
        try:
            return float(value)
        except ValueError:
            raise EnvParseError(var_name, "float", value, f"'{value}' is not a valid float")
    
    elif expected_type == "json":
        try:
            return json.loads(value)
        except json.JSONDecodeError as e:
            raise EnvParseError(var_name, "JSON", value, str(e))
    
    else:
        raise ValueError(f"Unknown type: {expected_type}")


def load_from_env(env: dict[str, str] | None = None) -> dict[str, Any]:
    """Load configuration values from environment variables.
    
    Args:
        env: Environment dictionary to use. Defaults to os.environ.
        
    Returns:
        Dictionary of configuration values found in environment.
        
    Raises:
        EnvParseError: If an environment variable cannot be parsed.
    """
    if env is None:
        env = dict(os.environ)
    
    result: dict[str, Any] = {}
    
    for env_var, (config_key, expected_type) in ENV_MAPPING.items():
        if env_var in env:
            value = env[env_var]
            result[config_key] = parse_env_value(value, expected_type, env_var)
    
    return result


def get_env_var_for_key(config_key: str) -> str | None:
    """Get the environment variable name for a config key.
    
    Args:
        config_key: The configuration key.
        
    Returns:
        The environment variable name, or None if not mapped.
    """
    for env_var, (key, _) in ENV_MAPPING.items():
        if key == config_key:
            return env_var
    return None
