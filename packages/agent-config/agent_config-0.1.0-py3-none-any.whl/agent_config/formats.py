"""Configuration file format parsers."""

import json
from pathlib import Path
from typing import Any


def parse_json(content: str) -> dict[str, Any]:
    """Parse JSON configuration content.
    
    Args:
        content: JSON string to parse.
        
    Returns:
        Parsed configuration dictionary.
        
    Raises:
        ValueError: If JSON is invalid.
    """
    try:
        data = json.loads(content)
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a JSON object, not array or primitive")
        return data
    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON: {e}")


def parse_yaml(content: str) -> dict[str, Any]:
    """Parse YAML configuration content.
    
    Args:
        content: YAML string to parse.
        
    Returns:
        Parsed configuration dictionary.
        
    Raises:
        ValueError: If YAML is invalid.
    """
    try:
        import yaml
    except ImportError:
        raise ImportError("PyYAML is required for YAML support. Install with: pip install PyYAML")
    
    try:
        data = yaml.safe_load(content)
        if data is None:
            return {}
        if not isinstance(data, dict):
            raise ValueError("Configuration must be a YAML mapping, not sequence or scalar")
        return data
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}")


def parse_toml(content: str) -> dict[str, Any]:
    """Parse TOML configuration content.
    
    Args:
        content: TOML string to parse.
        
    Returns:
        Parsed configuration dictionary.
        
    Raises:
        ValueError: If TOML is invalid.
        ImportError: If TOML library is not available.
    """
    import sys
    
    if sys.version_info >= (3, 11):
        import tomllib
        try:
            return tomllib.loads(content)
        except tomllib.TOMLDecodeError as e:
            raise ValueError(f"Invalid TOML: {e}")
    else:
        try:
            import tomli
            try:
                return tomli.loads(content)
            except tomli.TOMLDecodeError as e:
                raise ValueError(f"Invalid TOML: {e}")
        except ImportError:
            raise ImportError(
                "TOML support requires Python 3.11+ or the 'tomli' package. "
                "Install with: pip install agent-config[toml]"
            )


def parse_file(path: Path) -> dict[str, Any]:
    """Parse a configuration file based on its extension.
    
    Args:
        path: Path to the configuration file.
        
    Returns:
        Parsed configuration dictionary.
        
    Raises:
        ValueError: If file format is unsupported or content is invalid.
        FileNotFoundError: If file does not exist.
        IOError: If file cannot be read.
    """
    content = path.read_text(encoding="utf-8")
    suffix = path.suffix.lower()
    name = path.name.lower()
    
    # Handle .rc files (JSON by default)
    if name.startswith(".agent-configrc"):
        if suffix == ".json" or suffix == "":
            return parse_json(content)
        raise ValueError(f"Unsupported .rc file format: {path}")
    
    # Handle by extension
    if suffix in (".yaml", ".yml"):
        return parse_yaml(content)
    elif suffix == ".json":
        return parse_json(content)
    elif suffix == ".toml":
        return parse_toml(content)
    else:
        raise ValueError(f"Unsupported configuration file format: {suffix}")


def detect_format(path: Path) -> str:
    """Detect the format of a configuration file.
    
    Args:
        path: Path to the configuration file.
        
    Returns:
        Format string: 'yaml', 'json', or 'toml'.
    """
    suffix = path.suffix.lower()
    if suffix in (".yaml", ".yml"):
        return "yaml"
    elif suffix == ".json":
        return "json"
    elif suffix == ".toml":
        return "toml"
    else:
        return "json"  # Default for .rc files
