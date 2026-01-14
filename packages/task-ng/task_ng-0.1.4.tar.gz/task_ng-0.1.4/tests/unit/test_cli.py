"""Test CLI basic functionality."""

from taskng.cli.main import app


def test_version_command(cli_runner):
    """--version should print version and exit."""
    result = cli_runner.invoke(app, ["--version"])
    assert result.exit_code == 0
    assert "Task-NG" in result.output
    # Version is dynamic, just check it contains a version-like string
    import re

    assert re.search(r"\d+\.\d+\.\d+", result.output)


def test_help_command(cli_runner):
    """--help should show help text."""
    result = cli_runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    assert "Task-NG" in result.output
    assert "modern" in result.output.lower()


def test_no_args_runs_default_command(cli_runner):
    """Running with no args should run default command."""
    result = cli_runner.invoke(app, [])
    # Default command is "next" report
    assert result.exit_code == 0


def test_add_command(cli_runner):
    """Add command should create task."""
    result = cli_runner.invoke(app, ["add", "Test task"])
    assert result.exit_code == 0
    assert "Created task" in result.output
    assert "Test task" in result.output


def test_list_command(cli_runner, temp_db_path):
    """List command should work."""
    result = cli_runner.invoke(app, ["list"])
    assert result.exit_code == 0
    # With no database, should show helpful message or empty list
    assert "No tasks" in result.output or "[]" in result.output
