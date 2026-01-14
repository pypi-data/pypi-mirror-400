"""Tests for CLI commands."""

import json
import pytest
from pathlib import Path
from agent_config.cli import main, EXIT_SUCCESS, EXIT_CONFIG_ERROR


class TestCliPrint:
    """Tests for 'print' command."""
    
    def test_print_defaults(self, tmp_path, capsys):
        """Should print default config when no file exists."""
        result = main(["print", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        config = json.loads(captured.out)
        assert "temperature" in config
    
    def test_print_pretty(self, tmp_path, capsys):
        """--pretty should indent output."""
        result = main(["print", "--cwd", str(tmp_path), "--no-env", "--pretty"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert "\n  " in captured.out  # Indented
    
    def test_print_strict_fails(self, tmp_path):
        """--strict should fail without config file."""
        result = main(["print", "--cwd", str(tmp_path), "--strict", "--no-env"])
        assert result == EXIT_CONFIG_ERROR
    
    def test_print_from_file(self, tmp_path, capsys):
        """Should print config from file."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test-agent\nmodel: test")
        
        result = main(["print", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        config = json.loads(captured.out)
        assert config["name"] == "test-agent"
    
    def test_print_redacts_by_default(self, tmp_path, capsys):
        """Should redact sensitive values by default."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("api_key: secret123\nmodel: test")
        
        result = main(["print", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        config = json.loads(captured.out)
        assert "secret123" not in config["api_key"]
    
    def test_print_no_redact(self, tmp_path, capsys):
        """--no-redact should show sensitive values."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("api_key: secret123\nmodel: test")
        
        result = main(["print", "--cwd", str(tmp_path), "--no-env", "--no-redact"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        config = json.loads(captured.out)
        assert config["api_key"] == "secret123"


class TestCliGet:
    """Tests for 'get' command."""
    
    def test_get_simple_key(self, tmp_path, capsys):
        """Should get simple key value."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test-agent\nmodel: gpt-4")
        
        result = main(["get", "model", "--cwd", str(tmp_path), "--no-env", "--no-redact"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert captured.out.strip() == "gpt-4"
    
    def test_get_nested_key(self, tmp_path, capsys):
        """Should get nested key value."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: test\ntools:\n  - name: search\n    enabled: true")
        
        result = main(["get", "tools.0.name", "--cwd", str(tmp_path), "--no-env", "--no-redact"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert captured.out.strip() == "search"
    
    def test_get_missing_fails(self, tmp_path):
        """Should fail for missing key without default."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test\nmodel: test")
        
        result = main(["get", "nonexistent", "--cwd", str(tmp_path), "--no-env"])
        assert result == EXIT_CONFIG_ERROR
    
    def test_get_with_default(self, tmp_path, capsys):
        """Should return default for missing key."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test\nmodel: test")
        
        result = main(["get", "nonexistent", "--default", "fallback", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert captured.out.strip() == "fallback"
    
    def test_get_json_output(self, tmp_path, capsys):
        """--json should output JSON-encoded value."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: test\ntools:\n  - name: search")
        
        result = main(["get", "tools", "--json", "--cwd", str(tmp_path), "--no-env", "--no-redact"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        tools = json.loads(captured.out)
        assert tools[0]["name"] == "search"


class TestCliValidate:
    """Tests for 'validate' command."""
    
    def test_validate_valid_config(self, tmp_path, capsys):
        """Should return 0 for valid config."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("name: test\nmodel: gpt-4\ntemperature: 0.5")
        
        result = main(["validate", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_SUCCESS
        assert "valid" in captured.out.lower()
    
    def test_validate_invalid_config(self, tmp_path, capsys):
        """Should return 1 for invalid config."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: test\nmax_tokens: -100")
        
        result = main(["validate", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        assert result == EXIT_CONFIG_ERROR
        assert "ERROR" in captured.out
    
    def test_validate_json_output(self, tmp_path, capsys):
        """--json should output JSON format."""
        config_file = tmp_path / "agent.config.yaml"
        config_file.write_text("model: test\nmax_tokens: -100")
        
        result = main(["validate", "--json", "--cwd", str(tmp_path), "--no-env"])
        captured = capsys.readouterr()
        
        output = json.loads(captured.out)
        assert output["valid"] is False
        assert len(output["issues"]) > 0


class TestCliInit:
    """Tests for 'init' command."""
    
    def test_init_creates_yaml(self, tmp_path, capsys):
        """Should create agent.config.yaml by default."""
        result = main(["init", "--cwd", str(tmp_path)])
        
        assert result == EXIT_SUCCESS
        assert (tmp_path / "agent.config.yaml").exists()
    
    def test_init_creates_json(self, tmp_path, capsys):
        """--format json should create JSON file."""
        result = main(["init", "--format", "json", "--cwd", str(tmp_path)])
        
        assert result == EXIT_SUCCESS
        assert (tmp_path / "agent.config.json").exists()
        
        # Verify it's valid JSON
        content = (tmp_path / "agent.config.json").read_text()
        config = json.loads(content)
        assert "name" in config
    
    def test_init_fails_if_exists(self, tmp_path):
        """Should fail if config already exists."""
        (tmp_path / "agent.config.yaml").write_text("existing: true")
        
        result = main(["init", "--cwd", str(tmp_path)])
        assert result == EXIT_CONFIG_ERROR
    
    def test_init_force_overwrites(self, tmp_path, capsys):
        """--force should overwrite existing file."""
        (tmp_path / "agent.config.yaml").write_text("existing: true")
        
        result = main(["init", "--force", "--cwd", str(tmp_path)])
        
        assert result == EXIT_SUCCESS
        content = (tmp_path / "agent.config.yaml").read_text()
        assert "existing" not in content


class TestCliHelp:
    """Tests for help and version."""
    
    def test_no_command_shows_help(self, capsys):
        """No command should show help."""
        result = main([])
        assert result == EXIT_SUCCESS
    
    def test_version_flag(self, capsys):
        """--version should show version."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0
