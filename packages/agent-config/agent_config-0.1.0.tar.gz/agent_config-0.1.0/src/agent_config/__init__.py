"""
agent_config - Agent Configuration Loader & Normalizer

A lightweight Python library for loading, merging, and validating
agent configurations from files and environment variables.

Usage:
    from agent_config import load_config, validate_config

    config = load_config()
    issues = validate_config(config)
"""

__version__ = "0.1.0"

from .load import load_config, ConfigError
from .validate import validate_config, ValidationIssue

__all__ = [
    "load_config",
    "validate_config",
    "ConfigError",
    "ValidationIssue",
    "__version__",
]
