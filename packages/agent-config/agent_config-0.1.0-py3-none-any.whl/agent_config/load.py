"""Configuration loading and merging for agent configurations."""

import re
from pathlib import Path
from typing import Any

from .defaults import get_defaults
from .env import load_from_env, EnvParseError
from .formats import parse_file
from .validate import validate_config, has_errors, ValidationIssue

# Configuration file discovery order
CONFIG_FILES = [
    "agent.config.yaml",
    "agent.config.yml",
    "agent.config.json",
    "agent.config.toml",
    ".agent-configrc",
    ".agent-configrc.json",
]

# Keys that should be redacted
REDACT_PATTERNS = [
    re.compile(r"key", re.IGNORECASE),
    re.compile(r"token", re.IGNORECASE),
    re.compile(r"secret", re.IGNORECASE),
    re.compile(r"password", re.IGNORECASE),
]

REDACT_MASK = "***REDACTED***"


class ConfigError(Exception):
    """Raised when configuration loading or validation fails.
    
    Attributes:
        issues: List of validation issues that caused the error.
    """
    
    def __init__(self, message: str, issues: list[ValidationIssue] | None = None):
        super().__init__(message)
        self.issues = issues or []


def discover_config_file(cwd: Path) -> Path | None:
    """Discover a configuration file in the given directory.
    
    Searches for configuration files in order of precedence.
    
    Args:
        cwd: Directory to search in.
        
    Returns:
        Path to the first configuration file found, or None.
    """
    for filename in CONFIG_FILES:
        path = cwd / filename
        if path.exists() and path.is_file():
            return path
    return None


def normalize_config(config: dict[str, Any], base_path: Path | None = None) -> dict[str, Any]:
    """Normalize configuration values.
    
    - Coerces numeric fields to correct types
    - Sets default enabled=True for tools if omitted
    - Loads prompt_file content into system_prompt if needed
    - Preserves unknown keys
    
    Args:
        config: Configuration dictionary to normalize.
        base_path: Base path for resolving relative file paths.
        
    Returns:
        Normalized configuration dictionary.
    """
    result = config.copy()
    
    # Coerce temperature to float
    if "temperature" in result and result["temperature"] is not None:
        try:
            result["temperature"] = float(result["temperature"])
        except (ValueError, TypeError):
            pass  # Let validation catch this
    
    # Coerce top_p to float
    if "top_p" in result and result["top_p"] is not None:
        try:
            result["top_p"] = float(result["top_p"])
        except (ValueError, TypeError):
            pass
    
    # Coerce max_tokens to int
    if "max_tokens" in result and result["max_tokens"] is not None:
        try:
            result["max_tokens"] = int(result["max_tokens"])
        except (ValueError, TypeError):
            pass
    
    # Coerce timeout_ms to int
    if "timeout_ms" in result and result["timeout_ms"] is not None:
        try:
            result["timeout_ms"] = int(result["timeout_ms"])
        except (ValueError, TypeError):
            pass
    
    # Normalize tools
    if "tools" in result and result["tools"] is not None:
        if isinstance(result["tools"], list):
            normalized_tools = []
            for tool in result["tools"]:
                if isinstance(tool, dict):
                    normalized_tool = tool.copy()
                    # Default enabled to True if not set
                    if "enabled" not in normalized_tool:
                        normalized_tool["enabled"] = True
                    normalized_tools.append(normalized_tool)
                else:
                    normalized_tools.append(tool)
            result["tools"] = normalized_tools
    
    # Load prompt_file if system_prompt is not set
    if result.get("prompt_file") and not result.get("system_prompt"):
        prompt_path = Path(result["prompt_file"])
        if base_path and not prompt_path.is_absolute():
            prompt_path = base_path / prompt_path
        
        try:
            result["system_prompt"] = prompt_path.read_text(encoding="utf-8")
        except (IOError, OSError) as e:
            # Keep prompt_file set but don't fail - validation will warn
            pass
    
    return result


def redact_config(config: dict[str, Any]) -> dict[str, Any]:
    """Redact sensitive values from configuration.
    
    Masks values for keys matching sensitive patterns.
    
    Args:
        config: Configuration dictionary.
        
    Returns:
        Configuration with sensitive values redacted.
    """
    result = {}
    
    for key, value in config.items():
        should_redact = any(pattern.search(key) for pattern in REDACT_PATTERNS)
        
        if should_redact and value is not None:
            result[key] = REDACT_MASK
        elif isinstance(value, dict):
            result[key] = redact_config(value)
        elif isinstance(value, list):
            result[key] = [
                redact_config(item) if isinstance(item, dict) else item
                for item in value
            ]
        else:
            result[key] = value
    
    return result


def merge_configs(*configs: dict[str, Any]) -> dict[str, Any]:
    """Merge multiple configuration dictionaries.
    
    Later configs override earlier ones. Only non-None values override.
    
    Args:
        *configs: Configuration dictionaries to merge in order.
        
    Returns:
        Merged configuration dictionary.
    """
    result: dict[str, Any] = {}
    
    for config in configs:
        for key, value in config.items():
            if value is not None:
                result[key] = value
            elif key not in result:
                result[key] = value
    
    return result


def load_config(
    file: str | None = None,
    cwd: str | None = None,
    strict: bool = False,
    use_env: bool = True,
    env: dict[str, str] | None = None,
    redact: bool = False,
) -> dict[str, Any]:
    """Load and merge agent configuration from all sources.
    
    Loads configuration from:
    1. Built-in defaults
    2. Configuration file (discovered or specified)
    3. Environment variables (highest precedence)
    
    Args:
        file: Explicit path to configuration file. If None, auto-discovers.
        cwd: Working directory for file discovery. Defaults to current directory.
        strict: If True, require a configuration file to exist.
        use_env: If True, apply environment variable overrides.
        env: Custom environment dictionary. Defaults to os.environ.
        redact: If True, mask sensitive values in output.
        
    Returns:
        Merged and normalized configuration dictionary.
        
    Raises:
        ConfigError: If configuration is invalid or file not found in strict mode.
        FileNotFoundError: If specified file does not exist.
        EnvParseError: If an environment variable cannot be parsed.
    """
    # Determine working directory
    work_dir = Path(cwd) if cwd else Path.cwd()
    
    # Start with defaults
    config = get_defaults()
    
    # Load from file
    config_path: Path | None = None
    file_config: dict[str, Any] = {}
    
    if file:
        config_path = Path(file)
        if not config_path.is_absolute():
            config_path = work_dir / config_path
        
        if not config_path.exists():
            raise FileNotFoundError(f"Configuration file not found: {config_path}")
        
        file_config = parse_file(config_path)
    else:
        # Auto-discover
        config_path = discover_config_file(work_dir)
        if config_path:
            file_config = parse_file(config_path)
        elif strict:
            raise ConfigError(
                f"No configuration file found in {work_dir}. "
                f"Searched for: {', '.join(CONFIG_FILES)}"
            )
    
    # Load from environment
    env_config: dict[str, Any] = {}
    if use_env:
        env_config = load_from_env(env)
    
    # Merge: defaults < file < env
    config = merge_configs(config, file_config, env_config)
    
    # Normalize
    base_path = config_path.parent if config_path else work_dir
    config = normalize_config(config, base_path)
    
    # Validate
    issues = validate_config(config)
    if has_errors(issues):
        error_messages = [str(i) for i in issues if i.level == "error"]
        raise ConfigError(
            f"Configuration validation failed:\n" + "\n".join(error_messages),
            issues=issues
        )
    
    # Redact if requested
    if redact:
        config = redact_config(config)
    
    return config


def get_value_by_path(config: dict[str, Any], path: str) -> tuple[Any, bool]:
    """Get a value from config by dot-notation path.
    
    Args:
        config: Configuration dictionary.
        path: Dot-notation path (e.g., 'tools.0.name').
        
    Returns:
        Tuple of (value, found). If found is False, value is None.
    """
    parts = path.split(".")
    current: Any = config
    
    for part in parts:
        if isinstance(current, dict):
            if part in current:
                current = current[part]
            else:
                return None, False
        elif isinstance(current, list):
            try:
                index = int(part)
                if 0 <= index < len(current):
                    current = current[index]
                else:
                    return None, False
            except ValueError:
                return None, False
        else:
            return None, False
    
    return current, True
