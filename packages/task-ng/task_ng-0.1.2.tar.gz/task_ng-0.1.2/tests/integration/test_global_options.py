"""Integration tests for global CLI options."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestConfigOption:
    """Tests for --config global option."""

    def test_custom_config_file(self, runner, tmp_path):
        """Should use custom config file."""
        # Create custom config
        config_dir = tmp_path / "custom"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        data_dir = tmp_path / "custom_data"
        config_file.write_text(
            f"""[data]
location = "{data_dir}"
"""
        )

        # Create data directory
        data_dir.mkdir(exist_ok=True)

        result = runner.invoke(app, ["--config", str(config_file), "add", "Test task"])
        assert result.exit_code == 0
        assert "Created task" in result.output

        # Verify task was created in custom data location
        assert (data_dir / "task.db").exists()

    def test_config_option_short(self, runner, tmp_path):
        """Should support -c short option."""
        config_dir = tmp_path / "custom"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        data_dir = tmp_path / "custom_data"
        config_file.write_text(
            f"""[data]
location = "{data_dir}"
"""
        )

        data_dir.mkdir(exist_ok=True)

        result = runner.invoke(app, ["-c", str(config_file), "add", "Test task"])
        assert result.exit_code == 0


class TestDataDirOption:
    """Tests for --data-dir global option."""

    def test_custom_data_dir(self, runner, tmp_path):
        """Should use custom data directory."""
        data_dir = tmp_path / "mydata"
        data_dir.mkdir(exist_ok=True)

        result = runner.invoke(app, ["--data-dir", str(data_dir), "add", "Test task"])
        assert result.exit_code == 0
        assert "Created task" in result.output

        # Verify database in custom location
        assert (data_dir / "task.db").exists()

    def test_data_dir_overrides_config(self, runner, tmp_path):
        """--data-dir should override config file setting."""
        # Config points to one location
        config_dir = tmp_path / "override_config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        config_file.write_text(
            f"""[data]
location = "{tmp_path / "config_data"}"
"""
        )

        # But we specify different data dir
        actual_data = tmp_path / "actual_data"
        actual_data.mkdir(exist_ok=True)

        result = runner.invoke(
            app,
            [
                "--config",
                str(config_file),
                "--data-dir",
                str(actual_data),
                "add",
                "Test task",
            ],
        )
        assert result.exit_code == 0

        # Should use explicit --data-dir, not config's data_dir
        assert (actual_data / "task.db").exists()
        assert not (tmp_path / "config_data").exists()


class TestLocalDirectory:
    """Tests for automatic ./taskng detection."""

    def test_detect_local_taskng_dir(self, runner, tmp_path, monkeypatch):
        """Should auto-detect ./taskng directory."""
        from taskng.config import settings

        # Reset isolation to test actual local directory detection
        settings.reset_config()

        # Change to tmp directory
        monkeypatch.chdir(tmp_path)

        # Create local .taskng directory with config
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir(exist_ok=True)
        config_file = local_dir / "config.toml"
        data_dir = tmp_path / "local_data"
        config_file.write_text(
            f"""[data]
location = "{data_dir}"
"""
        )
        data_dir.mkdir(exist_ok=True)

        result = runner.invoke(app, ["add", "Local task"])
        assert result.exit_code == 0

        # Should use local config's data_dir
        assert (data_dir / "task.db").exists()

    def test_explicit_config_overrides_local(self, runner, tmp_path, monkeypatch):
        """Explicit --config should override local ./.taskng."""
        monkeypatch.chdir(tmp_path)

        # Create local .taskng directory
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir(exist_ok=True)
        local_config = local_dir / "config.toml"
        local_config.write_text(
            f"""[data]
location = "{tmp_path / "local"}"
"""
        )

        # Create explicit config
        explicit_dir = tmp_path / "explicit"
        explicit_dir.mkdir(exist_ok=True)
        explicit_config = explicit_dir / "config.toml"
        explicit_data = tmp_path / "explicit_data"
        explicit_config.write_text(
            f"""[data]
location = "{explicit_data}"
"""
        )
        explicit_data.mkdir(exist_ok=True)

        result = runner.invoke(app, ["--config", str(explicit_config), "add", "Task"])
        assert result.exit_code == 0

        # Should use explicit config, not local
        assert (explicit_data / "task.db").exists()
        assert not (tmp_path / "local").exists()


class TestContextWithCustomPaths:
    """Tests for context with custom config paths."""

    def test_context_uses_custom_config_dir(self, runner, tmp_path):
        """Context state should be stored in custom config directory."""
        config_dir = tmp_path / "ctx_config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"

        # Create config with a context defined
        data_dir = tmp_path / "ctx_data"
        config_file.write_text(
            f"""
[data]
location = "{data_dir}"

[context.work]
project = "Work"
"""
        )

        data_dir.mkdir(exist_ok=True)

        # Set context
        result = runner.invoke(
            app, ["--config", str(config_file), "context", "set", "work"]
        )
        assert result.exit_code == 0

        # Context state should be in custom config dir
        context_file = config_dir / "context"
        assert context_file.exists()
        assert context_file.read_text().strip() == "work"


class TestDefaultCommand:
    """Tests for default command when no subcommand provided."""

    def test_no_args_runs_default_command(self, runner, tmp_path):
        """Running with no args should run default command (next report)."""
        data_dir = tmp_path / "data"
        data_dir.mkdir(exist_ok=True)

        # Add a task first
        runner.invoke(app, ["--data-dir", str(data_dir), "add", "Test task"])

        # Run with no subcommand
        result = runner.invoke(app, ["--data-dir", str(data_dir)])
        assert result.exit_code == 0
        # Default is "next" report which shows tasks
        assert "Test task" in result.output

    def test_custom_default_command_list(self, runner, tmp_path):
        """Should use custom default command from config."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        data_dir = tmp_path / "data"

        # Set default command to "list"
        config_file.write_text(
            f"""
[data]
location = "{data_dir}"

[default]
command = "list"
"""
        )
        data_dir.mkdir(exist_ok=True)

        # Add a task
        runner.invoke(app, ["--config", str(config_file), "add", "Test task"])

        # Run with no subcommand
        result = runner.invoke(app, ["--config", str(config_file)])
        assert result.exit_code == 0
        assert "Test task" in result.output

    def test_custom_default_command_projects(self, runner, tmp_path):
        """Should support 'projects' as default command."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        data_dir = tmp_path / "data"

        config_file.write_text(
            f"""
[data]
location = "{data_dir}"

[default]
command = "projects"
"""
        )
        data_dir.mkdir(exist_ok=True)

        # Add a task with project
        runner.invoke(app, ["--config", str(config_file), "add", "Test", "-p", "Work"])

        # Run with no subcommand
        result = runner.invoke(app, ["--config", str(config_file)])
        assert result.exit_code == 0
        assert "Work" in result.output

    def test_default_command_report(self, runner, tmp_path):
        """Should run a report as default command."""
        config_dir = tmp_path / "config"
        config_dir.mkdir(exist_ok=True)
        config_file = config_dir / "config.toml"
        data_dir = tmp_path / "data"

        # Use "all" report as default
        config_file.write_text(
            f"""
[data]
location = "{data_dir}"

[default]
command = "all"
"""
        )
        data_dir.mkdir(exist_ok=True)

        # Add and complete a task
        runner.invoke(app, ["--config", str(config_file), "add", "Test task"])
        runner.invoke(app, ["--config", str(config_file), "done", "1"])

        # Run with no subcommand - "all" report shows completed tasks
        result = runner.invoke(app, ["--config", str(config_file)])
        assert result.exit_code == 0
        assert "Test task" in result.output
