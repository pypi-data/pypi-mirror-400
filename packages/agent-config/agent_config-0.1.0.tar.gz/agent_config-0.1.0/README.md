# agent-config

A lightweight Python library and CLI for loading, merging, and validating agent configurations from files and environment variables.

## Installation

```bash
pip install agent-config
```

For TOML support on Python < 3.11:

```bash
pip install agent-config[toml]
```

## Quick Start

### CLI Usage

Initialize a new configuration file:

```bash
agent-config init
```

This creates an `agent.config.yaml` file with sensible defaults.

Print the resolved configuration:

```bash
agent-config print --pretty
```

Get a specific value:

```bash
agent-config get model
agent-config get tools.0.name
```

Validate your configuration:

```bash
agent-config validate
```

### Library Usage

```python
from agent_config import load_config, validate_config

# Load configuration from file + environment
config = load_config()

# Access values
print(config["model"])
print(config["temperature"])

# Validate a configuration dict
issues = validate_config(config)
for issue in issues:
    print(f"{issue.level}: {issue.message}")
```

## Configuration Sources

Configuration is loaded and merged from multiple sources in this order (later sources override earlier ones):

1. **Built-in defaults** - Sensible defaults for all fields
2. **Configuration file** - YAML, JSON, or TOML
3. **Environment variables** - Highest precedence

### Configuration Files

The CLI automatically discovers configuration files in this order:

- `agent.config.yaml`
- `agent.config.yml`
- `agent.config.json`
- `agent.config.toml`
- `.agent-configrc`
- `.agent-configrc.json`

### Example Configuration (YAML)

```yaml
name: my-agent
model: gpt-4
temperature: 0.2
max_tokens: 4096

system_prompt: "You are a helpful assistant."

api_base: https://api.openai.com/v1
timeout_ms: 60000

tools:
  - name: web_search
    enabled: true
    config:
      max_results: 10
```

### Example Configuration (JSON)

```json
{
  "name": "my-agent",
  "model": "gpt-4",
  "temperature": 0.2,
  "max_tokens": 4096,
  "system_prompt": "You are a helpful assistant.",
  "timeout_ms": 60000,
  "tools": [
    {
      "name": "web_search",
      "enabled": true
    }
  ]
}
```

## Environment Variables

Override any configuration value using environment variables:

| Environment Variable | Config Key | Type |
|---------------------|------------|------|
| `AGENT_NAME` | `name` | string |
| `AGENT_MODEL` | `model` | string |
| `AGENT_TEMPERATURE` | `temperature` | float |
| `AGENT_TOP_P` | `top_p` | float |
| `AGENT_MAX_TOKENS` | `max_tokens` | int |
| `AGENT_SYSTEM_PROMPT` | `system_prompt` | string |
| `AGENT_PROMPT_FILE` | `prompt_file` | string |
| `AGENT_API_BASE` | `api_base` | string |
| `AGENT_API_KEY` | `api_key` | string |
| `AGENT_TIMEOUT_MS` | `timeout_ms` | int |
| `AGENT_TOOLS_JSON` | `tools` | JSON array |

Example:

```bash
export AGENT_MODEL="gpt-4-turbo"
export AGENT_TEMPERATURE="0.5"
export AGENT_API_KEY="sk-..."
agent-config print
```

## CLI Reference

### `agent-config print`

Print the resolved configuration as JSON.

```bash
agent-config print [OPTIONS]

Options:
  -f, --file PATH    Path to configuration file
  -C, --cwd PATH     Working directory for config discovery
  -p, --pretty       Pretty-print JSON output
  --strict           Fail if no configuration file is found
  --no-env           Ignore environment variable overrides
  --redact           Redact sensitive values (default)
  --no-redact        Show sensitive values (use with caution)
```

### `agent-config get`

Get a specific value by dot-notation path.

```bash
agent-config get PATH [OPTIONS]

Options:
  -f, --file PATH    Path to configuration file
  -C, --cwd PATH     Working directory for config discovery
  -d, --default VAL  Default value if path not found
  -j, --json         Output value as JSON
  --strict           Fail if no configuration file is found
  --no-env           Ignore environment variable overrides
```

Examples:

```bash
agent-config get model
agent-config get temperature --default 0.7
agent-config get tools.0.name
agent-config get tools --json
```

### `agent-config validate`

Validate configuration and report issues.

```bash
agent-config validate [OPTIONS]

Options:
  -f, --file PATH    Path to configuration file
  -C, --cwd PATH     Working directory for config discovery
  -j, --json         Output issues as JSON
  --strict           Fail if no configuration file is found
  --no-env           Ignore environment variable overrides
```

Exit codes:
- `0` - Valid configuration
- `1` - Validation errors found

### `agent-config init`

Create a starter configuration file.

```bash
agent-config init [OPTIONS]

Options:
  -t, --format FMT   File format: yaml or json (default: yaml)
  -f, --force        Overwrite existing configuration file
  -C, --cwd PATH     Directory to create configuration file in
```

## Library API

### `load_config()`

Load and merge configuration from all sources.

```python
from agent_config import load_config

config = load_config(
    file=None,        # Explicit path to config file
    cwd=None,         # Working directory for discovery
    strict=False,     # Require config file to exist
    use_env=True,     # Apply environment overrides
    env=None,         # Custom environment dict
    redact=False,     # Mask sensitive values
)
```

### `validate_config()`

Validate a configuration dictionary.

```python
from agent_config import validate_config, ValidationIssue

issues = validate_config(config)
for issue in issues:
    print(f"[{issue.level}] {issue.path}: {issue.message}")
```

### `ValidationIssue`

```python
@dataclass
class ValidationIssue:
    level: Literal["error", "warn"]
    path: str | None
    message: str
```

### `ConfigError`

Raised when configuration loading or validation fails.

```python
from agent_config import load_config, ConfigError

try:
    config = load_config(strict=True)
except ConfigError as e:
    print(f"Config error: {e}")
    for issue in e.issues:
        print(f"  - {issue}")
```

## Sensitive Data Handling

By default, the CLI redacts sensitive values (fields matching `key`, `token`, `secret`, `password`) when printing configuration. Use `--no-redact` to disable this behavior.

**Warning:** Be careful when using `--no-redact` in logs or shared environments.

## Configuration Schema

| Field | Type | Default | Description |
|-------|------|---------|-------------|
| `name` | string | null | Agent identifier |
| `model` | string | null | Model name/identifier |
| `temperature` | float | 0.2 | Sampling temperature |
| `top_p` | float | null | Nucleus sampling parameter |
| `max_tokens` | int | null | Maximum tokens to generate |
| `system_prompt` | string | null | System prompt text |
| `prompt_file` | string | null | Path to system prompt file |
| `tools` | array | [] | Tool configurations |
| `api_base` | string | null | API base URL |
| `api_key` | string | null | API key |
| `timeout_ms` | int | 60000 | Request timeout in milliseconds |

Additional keys are preserved and passed through.

## Import Name

Note: The PyPI package name is `agent-config` (with hyphen), but the Python import name uses underscores:

```python
import agent_config
```

This follows Python naming conventions since hyphens are not valid in Python identifiers.