"""Command-line interface for agent-config."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any

from . import __version__
from .load import load_config, get_value_by_path, redact_config, ConfigError
from .validate import validate_config, has_errors, format_issues, ValidationIssue
from .env import EnvParseError


# Exit codes
EXIT_SUCCESS = 0
EXIT_CONFIG_ERROR = 1
EXIT_RUNTIME_ERROR = 2


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog="agent-config",
        description="Agent configuration loader and normalizer",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Common arguments for config loading
    def add_common_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument(
            "--file", "-f",
            type=str,
            help="Path to configuration file",
        )
        subparser.add_argument(
            "--cwd", "-C",
            type=str,
            help="Working directory for config discovery",
        )
        subparser.add_argument(
            "--strict",
            action="store_true",
            help="Fail if no configuration file is found",
        )
        subparser.add_argument(
            "--no-env",
            action="store_true",
            help="Ignore environment variable overrides",
        )
    
    # print command
    print_parser = subparsers.add_parser(
        "print",
        help="Print resolved configuration as JSON",
    )
    add_common_args(print_parser)
    print_parser.add_argument(
        "--pretty", "-p",
        action="store_true",
        help="Pretty-print JSON output",
    )
    print_parser.add_argument(
        "--redact",
        action="store_true",
        help="Redact sensitive values (api_key, tokens, secrets)",
    )
    print_parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Do not redact sensitive values (use with caution)",
    )
    
    # get command
    get_parser = subparsers.add_parser(
        "get",
        help="Get a specific value by path",
    )
    add_common_args(get_parser)
    get_parser.add_argument(
        "path",
        type=str,
        help="Dot-notation path to value (e.g., 'model', 'tools.0.name')",
    )
    get_parser.add_argument(
        "--default", "-d",
        type=str,
        help="Default value if path not found",
    )
    get_parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="output_json",
        help="Output value as JSON",
    )
    get_parser.add_argument(
        "--redact",
        action="store_true",
        help="Redact sensitive values",
    )
    get_parser.add_argument(
        "--no-redact",
        action="store_true",
        help="Do not redact sensitive values",
    )
    
    # validate command
    validate_parser = subparsers.add_parser(
        "validate",
        help="Validate configuration",
    )
    add_common_args(validate_parser)
    validate_parser.add_argument(
        "--json", "-j",
        action="store_true",
        dest="output_json",
        help="Output issues as JSON",
    )
    
    # init command
    init_parser = subparsers.add_parser(
        "init",
        help="Create a starter configuration file",
    )
    init_parser.add_argument(
        "--format", "-t",
        type=str,
        choices=["yaml", "json"],
        default="yaml",
        help="Configuration file format (default: yaml)",
    )
    init_parser.add_argument(
        "--force", "-f",
        action="store_true",
        help="Overwrite existing configuration file",
    )
    init_parser.add_argument(
        "--cwd", "-C",
        type=str,
        help="Directory to create configuration file in",
    )
    
    return parser


def cmd_print(args: argparse.Namespace) -> int:
    """Handle the 'print' command."""
    try:
        # Determine redaction behavior
        redact = args.redact or (not args.no_redact)
        
        config = load_config(
            file=args.file,
            cwd=args.cwd,
            strict=args.strict,
            use_env=not args.no_env,
            redact=redact,
        )
        
        indent = 2 if args.pretty else None
        print(json.dumps(config, indent=indent))
        return EXIT_SUCCESS
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except EnvParseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


def cmd_get(args: argparse.Namespace) -> int:
    """Handle the 'get' command."""
    try:
        # Determine redaction behavior
        redact = args.redact or (not args.no_redact)
        
        config = load_config(
            file=args.file,
            cwd=args.cwd,
            strict=args.strict,
            use_env=not args.no_env,
            redact=redact,
        )
        
        value, found = get_value_by_path(config, args.path)
        
        if not found:
            if args.default is not None:
                value = args.default
                found = True
            else:
                print(f"Error: Path '{args.path}' not found in configuration", file=sys.stderr)
                return EXIT_CONFIG_ERROR
        
        if args.output_json:
            print(json.dumps(value))
        else:
            if isinstance(value, (dict, list)):
                print(json.dumps(value))
            elif value is None:
                print("null")
            else:
                print(value)
        
        return EXIT_SUCCESS
        
    except FileNotFoundError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except ConfigError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except EnvParseError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


def cmd_validate(args: argparse.Namespace) -> int:
    """Handle the 'validate' command."""
    try:
        # Load without raising on validation errors
        from .defaults import get_defaults
        from .formats import parse_file
        from .load import discover_config_file, merge_configs, normalize_config
        from .env import load_from_env
        
        work_dir = Path(args.cwd) if args.cwd else Path.cwd()
        config = get_defaults()
        config_path = None
        
        if args.file:
            config_path = Path(args.file)
            if not config_path.is_absolute():
                config_path = work_dir / config_path
            if not config_path.exists():
                raise FileNotFoundError(f"Configuration file not found: {config_path}")
            file_config = parse_file(config_path)
        else:
            config_path = discover_config_file(work_dir)
            if config_path:
                file_config = parse_file(config_path)
            elif args.strict:
                raise ConfigError(f"No configuration file found in {work_dir}")
            else:
                file_config = {}
        
        env_config = load_from_env() if not args.no_env else {}
        config = merge_configs(config, file_config, env_config)
        
        base_path = config_path.parent if config_path else work_dir
        config = normalize_config(config, base_path)
        
        issues = validate_config(config)
        
        if args.output_json:
            issues_data = [
                {"level": i.level, "path": i.path, "message": i.message}
                for i in issues
            ]
            print(json.dumps({"valid": not has_errors(issues), "issues": issues_data}))
        else:
            if issues:
                print(format_issues(issues))
            else:
                print("Configuration is valid.")
        
        return EXIT_CONFIG_ERROR if has_errors(issues) else EXIT_SUCCESS
        
    except FileNotFoundError as e:
        if args.output_json:
            print(json.dumps({"valid": False, "issues": [{"level": "error", "path": None, "message": str(e)}]}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except ConfigError as e:
        if args.output_json:
            print(json.dumps({"valid": False, "issues": [{"level": "error", "path": None, "message": str(e)}]}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except EnvParseError as e:
        if args.output_json:
            print(json.dumps({"valid": False, "issues": [{"level": "error", "path": None, "message": str(e)}]}))
        else:
            print(f"Error: {e}", file=sys.stderr)
        return EXIT_CONFIG_ERROR
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


def cmd_init(args: argparse.Namespace) -> int:
    """Handle the 'init' command."""
    try:
        work_dir = Path(args.cwd) if args.cwd else Path.cwd()
        
        if args.format == "yaml":
            filename = "agent.config.yaml"
            content = """# Agent Configuration
# See: https://github.com/andrewgcodes/merciful-delicate-samovar

# Model settings
name: my-agent
model: gpt-4
temperature: 0.2
# top_p: 1.0
# max_tokens: 4096

# Prompts
# system_prompt: "You are a helpful assistant."
# prompt_file: ./prompts/system.txt

# API settings
# api_base: https://api.openai.com/v1
# api_key: ${OPENAI_API_KEY}
timeout_ms: 60000

# Tools
tools: []
#  - name: web_search
#    enabled: true
#    config:
#      max_results: 10
"""
        else:  # json
            filename = "agent.config.json"
            content = """{
  "name": "my-agent",
  "model": "gpt-4",
  "temperature": 0.2,
  "timeout_ms": 60000,
  "tools": []
}
"""
        
        filepath = work_dir / filename
        
        if filepath.exists() and not args.force:
            print(f"Error: {filename} already exists. Use --force to overwrite.", file=sys.stderr)
            return EXIT_CONFIG_ERROR
        
        filepath.write_text(content, encoding="utf-8")
        print(f"Created {filepath}")
        return EXIT_SUCCESS
        
    except IOError as e:
        print(f"Error: {e}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        return EXIT_RUNTIME_ERROR


def main(argv: list[str] | None = None) -> int:
    """Main entry point for the CLI.
    
    Args:
        argv: Command-line arguments. Defaults to sys.argv[1:].
        
    Returns:
        Exit code.
    """
    parser = create_parser()
    args = parser.parse_args(argv)
    
    if args.command is None:
        parser.print_help()
        return EXIT_SUCCESS
    
    commands = {
        "print": cmd_print,
        "get": cmd_get,
        "validate": cmd_validate,
        "init": cmd_init,
    }
    
    handler = commands.get(args.command)
    if handler:
        return handler(args)
    
    parser.print_help()
    return EXIT_SUCCESS


if __name__ == "__main__":
    sys.exit(main())
