"""Integration tests for config command."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.config.settings import reset_config

runner = CliRunner()


@pytest.fixture(autouse=True)
def reset_config_singleton():
    """Reset config singleton before each test."""
    reset_config()
    yield
    reset_config()


class TestConfigCommand:
    """Tests for config command."""

    def test_show_all_config(self, tmp_path, monkeypatch):
        """Should show all configuration values."""
        # Use temp config file
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config"])

        assert result.exit_code == 0
        assert "Configuration" in result.output
        assert "data.location" in result.output
        assert "ui.color" in result.output

    def test_show_single_value(self, tmp_path, monkeypatch):
        """Should show single config value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "ui.color"])

        assert result.exit_code == 0
        assert "ui.color=" in result.output

    def test_show_missing_value(self, tmp_path, monkeypatch):
        """Should show message for missing value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "nonexistent.key"])

        assert result.exit_code == 0
        assert "not set" in result.output

    def test_set_string_value(self, tmp_path, monkeypatch):
        """Should set string config value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "default.project", "Work"])

        assert result.exit_code == 0
        assert "default.project" in result.output
        assert "Work" in result.output

    def test_set_boolean_value(self, tmp_path, monkeypatch):
        """Should set boolean config value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "ui.color", "false"])

        assert result.exit_code == 0
        assert "False" in result.output

    def test_set_integer_value(self, tmp_path, monkeypatch):
        """Should set integer config value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "custom.number", "42"])

        assert result.exit_code == 0
        assert "42" in result.output

    def test_unset_value(self, tmp_path, monkeypatch):
        """Should unset config value."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('[custom]\nvalue = "test"')
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "--unset", "custom.value"])

        assert result.exit_code == 0
        assert "Unset" in result.output

    def test_unset_missing_value(self, tmp_path, monkeypatch):
        """Should handle unsetting missing value."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "--unset", "nonexistent.key"])

        assert result.exit_code == 0
        assert "not found" in result.output

    def test_value_persists(self, tmp_path, monkeypatch):
        """Should persist value to file."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        # Set value
        runner.invoke(app, ["config", "custom.test", "value"])

        # Check file
        assert config_file.exists()
        content = config_file.read_text()
        assert "custom" in content

    def test_nested_values(self, tmp_path, monkeypatch):
        """Should handle nested config values."""
        config_file = tmp_path / "config.toml"
        monkeypatch.setenv("TASKNG_CONFIG_FILE", str(config_file))

        result = runner.invoke(app, ["config", "report.list.columns"])

        assert result.exit_code == 0
        assert "report.list.columns" in result.output
