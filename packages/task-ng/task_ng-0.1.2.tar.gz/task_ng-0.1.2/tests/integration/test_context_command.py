"""Integration tests for context command."""

import json

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_config(isolate_test_data, tmp_path):
    """Set up temp config directory with context definitions."""
    from taskng.config import settings

    config_dir = tmp_path / "config"
    config_file = config_dir / "config.toml"

    # Write config with context definitions
    config_file.write_text(
        f"""
[data]
location = "{isolate_test_data}"

[context.work]
description = "Work tasks"
project = "Work"

[context.home]
description = "Home tasks"
project = "Home"

[context.urgent]
description = "Urgent tasks"
tags = ["urgent"]
"""
    )

    settings.set_config_path(config_file)

    return config_dir


class TestContextCommand:
    def test_context_no_active(self, runner, temp_config):
        """Context with no active context shows message."""
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "No context active" in result.output

    def test_context_set(self, runner, temp_config):
        """Set context works."""
        result = runner.invoke(app, ["context", "set", "work"])
        assert result.exit_code == 0
        assert "work" in result.output
        assert "Work tasks" in result.output

    def test_context_show_active(self, runner, temp_config):
        """Show active context."""
        runner.invoke(app, ["context", "set", "work"])
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "work" in result.output

    def test_context_clear(self, runner, temp_config):
        """Clear context with 'none'."""
        runner.invoke(app, ["context", "set", "work"])
        result = runner.invoke(app, ["context", "clear"])
        assert result.exit_code == 0
        assert "cleared" in result.output

    def test_context_set_undefined_becomes_temporary(self, runner, temp_config):
        """Setting undefined context creates temporary context with filter."""
        result = runner.invoke(app, ["context", "set", "project:Test"])
        assert result.exit_code == 0
        assert "Temporary context set" in result.output
        assert "project:Test" in result.output

    def test_context_temporary_with_multiple_filters(self, runner, temp_config):
        """Setting temporary context with multiple filters."""
        result = runner.invoke(
            app, ["context", "set", "project:Work", "+urgent", "+important"]
        )
        assert result.exit_code == 0
        assert "Temporary context set" in result.output
        assert "project:Work" in result.output
        assert "+urgent" in result.output
        assert "config.toml" in result.output

    def test_context_temporary_show(self, runner, temp_config):
        """Show temporary context."""
        runner.invoke(app, ["context", "set", "project:Test", "+tag"])
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "temporary" in result.output
        assert "project:Test" in result.output

    def test_context_list(self, runner, temp_config):
        """List all contexts."""
        result = runner.invoke(app, ["context", "list"])
        assert result.exit_code == 0
        assert "work" in result.output
        assert "home" in result.output
        assert "urgent" in result.output

    def test_context_list_shows_active(self, runner, temp_config):
        """List shows which context is active."""
        runner.invoke(app, ["context", "set", "work"])
        result = runner.invoke(app, ["context", "list"])
        assert result.exit_code == 0
        assert "✓" in result.output

    def test_context_json_output(self, runner, temp_config):
        """Context with --json outputs JSON."""
        runner.invoke(app, ["context", "set", "work"])
        result = runner.invoke(app, ["--json", "context", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] == "work"

    def test_context_list_json(self, runner, temp_config):
        """Context list with --json outputs JSON."""
        result = runner.invoke(app, ["--json", "context", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3
        names = [c["name"] for c in data]
        assert "work" in names
        assert "home" in names

    def test_context_clear_json(self, runner, temp_config):
        """Clearing context with --json outputs JSON."""
        runner.invoke(app, ["context", "set", "work"])
        result = runner.invoke(app, ["--json", "context", "clear"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] is None

    def test_context_show_no_active_json(self, runner, temp_config):
        """Show with no active context in JSON mode."""
        result = runner.invoke(app, ["--json", "context", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] is None

    def test_context_temporary_json(self, runner, temp_config):
        """Temporary context with --json outputs JSON."""
        result = runner.invoke(
            app, ["--json", "context", "set", "project:Test", "+tag"]
        )
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] == "__temporary__"
        assert "project:Test" in data["filters"]
        assert "+tag" in data["filters"]

    def test_context_show_temporary_json(self, runner, temp_config):
        """Show temporary context in JSON mode."""
        runner.invoke(app, ["context", "set", "project:Test"])
        result = runner.invoke(app, ["--json", "context", "show"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] == "__temporary__"
        assert "project:Test" in data["filters"]


class TestContextEdgeCases:
    def test_context_set_json_mode(self, runner, temp_config):
        """Setting context in JSON mode outputs JSON."""
        result = runner.invoke(app, ["--json", "context", "set", "work"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["context"] == "work"

    def test_context_temporary_show_no_filters(self, runner, temp_config):
        """Show temporary context when filters are empty."""
        # This is an edge case that shouldn't happen in normal use
        # but we want to ensure the code handles it gracefully
        from taskng.core.context import set_temporary_context

        set_temporary_context([])
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "temporary" in result.output

    def test_context_toml_with_single_filter(self, runner, temp_config):
        """Temporary context with single filter shows TOML config."""
        result = runner.invoke(app, ["context", "set", "status:pending"])
        assert result.exit_code == 0
        assert "Temporary context set" in result.output
        assert "config.toml" in result.output
        assert "[context.mycontext]" in result.output

    def test_context_toml_with_tag_only(self, runner, temp_config):
        """Temporary context with tag shows TOML config."""
        result = runner.invoke(app, ["context", "set", "+urgent"])
        assert result.exit_code == 0
        assert "Temporary context set" in result.output
        assert "tags" in result.output

    def test_context_toml_with_multiple_other_filters(self, runner, temp_config):
        """Temporary context with multiple other filters shows TOML config."""
        result = runner.invoke(app, ["context", "set", "status:pending", "priority:H"])
        assert result.exit_code == 0
        assert "Temporary context set" in result.output
        assert "status:pending" in result.output

    def test_context_list_empty(self, runner, isolate_test_data, tmp_path):
        """List contexts when none are defined."""
        from taskng.config import settings

        config_dir = tmp_path / "config"
        config_file = config_dir / "config.toml"

        # Write config with no context definitions
        config_file.write_text(
            f"""[data]
location = "{isolate_test_data}"
"""
        )
        settings.set_config_path(config_file)

        result = runner.invoke(app, ["context", "list"])
        assert result.exit_code == 0
        assert "No contexts defined" in result.output
        assert "config.toml" in result.output

    def test_context_list_empty_json(self, runner, isolate_test_data, tmp_path):
        """List contexts when none are defined in JSON mode."""
        from taskng.config import settings

        config_dir = tmp_path / "config"
        config_file = config_dir / "config.toml"

        # Write config with no context definitions
        config_file.write_text(
            f"""[data]
location = "{isolate_test_data}"
"""
        )
        settings.set_config_path(config_file)

        result = runner.invoke(app, ["--json", "context", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_context_with_no_description(self, runner, isolate_test_data, tmp_path):
        """Context without description field."""
        from taskng.config import settings

        config_dir = tmp_path / "config"
        config_file = config_dir / "config.toml"

        # Context with no description
        config_file.write_text(
            f"""
[data]
location = "{isolate_test_data}"

[context.minimal]
project = "Test"
"""
        )
        settings.set_config_path(config_file)

        result = runner.invoke(app, ["context", "set", "minimal"])
        assert result.exit_code == 0
        assert "minimal" in result.output

        # Show should work without description
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "minimal" in result.output

    def test_context_with_no_filter(self, runner, isolate_test_data, tmp_path):
        """Context without any filter fields."""
        from taskng.config import settings

        config_dir = tmp_path / "config"
        config_file = config_dir / "config.toml"

        # Context with only description, no filters
        config_file.write_text(
            f"""
[data]
location = "{isolate_test_data}"

[context.empty]
description = "No filters"
"""
        )
        settings.set_config_path(config_file)

        result = runner.invoke(app, ["context", "set", "empty"])
        assert result.exit_code == 0
        assert "empty" in result.output

        # Show should work without filters
        result = runner.invoke(app, ["context", "show"])
        assert result.exit_code == 0
        assert "empty" in result.output
        assert "No filters" in result.output


class TestContextFiltering:
    def test_context_filters_list(self, runner, temp_config):
        """Context filter applied to list command."""
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Home task", "-p", "Home"])

        # Set work context
        runner.invoke(app, ["context", "set", "work"])

        # List should only show work tasks
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Work task" in result.output
        assert "Home task" not in result.output

    def test_context_with_tags(self, runner, temp_config):
        """Context with tag filter works."""
        runner.invoke(app, ["add", "Urgent task +urgent"])
        runner.invoke(app, ["add", "Normal task"])

        # Set urgent context
        runner.invoke(app, ["context", "set", "urgent"])

        # List should only show urgent tasks
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Urgent task" in result.output
        assert "Normal task" not in result.output

    def test_context_clears_filter(self, runner, temp_config):
        """Clearing context removes filter."""
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Home task", "-p", "Home"])

        # Set and clear context
        runner.invoke(app, ["context", "set", "work"])
        runner.invoke(app, ["context", "clear"])

        # List should show all tasks
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        assert "Work task" in result.output
        assert "Home task" in result.output

    def test_user_filter_with_context(self, runner, temp_config):
        """User filter combines with context filter."""
        runner.invoke(app, ["add", "Work urgent +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Work normal", "-p", "Work"])

        # Set work context
        runner.invoke(app, ["context", "set", "work"])

        # Add user filter for urgent
        result = runner.invoke(app, ["list", "+urgent"])
        assert result.exit_code == 0
        assert "Work urgent" in result.output
        assert "Work normal" not in result.output
