"""Unit tests for main CLI module."""

import re

from typer.testing import CliRunner

from taskng.cli.main import _is_filter_arg, app

runner = CliRunner()


class TestHelperFunctions:
    """Test helper functions in main module."""

    def test_is_filter_arg_with_tag(self):
        """Should recognize tag filter."""
        assert _is_filter_arg("+urgent")
        assert _is_filter_arg("-waiting")

    def test_is_filter_arg_with_attribute(self):
        """Should recognize attribute filter."""
        assert _is_filter_arg("project:Work")
        assert _is_filter_arg("priority:H")
        assert _is_filter_arg("status:pending")

    def test_is_filter_arg_with_number(self):
        """Should not recognize plain number as filter."""
        assert not _is_filter_arg("1")
        assert not _is_filter_arg("42")
        assert not _is_filter_arg("123")

    def test_is_filter_arg_with_text(self):
        """Should not recognize plain text as filter."""
        assert not _is_filter_arg("task")
        assert not _is_filter_arg("description")


class TestVersionCommand:
    """Test version command."""

    def test_version_command(self):
        """Should show version information."""
        result = runner.invoke(app, ["version"])

        assert result.exit_code == 0
        assert "Task-NG" in result.stdout
        # Version is dynamic, just check it contains a version-like string
        assert re.search(r"\d+\.\d+\.\d+", result.stdout)

    def test_version_flag(self):
        """Should show version with --version flag."""
        result = runner.invoke(app, ["--version"])

        assert result.exit_code == 0
        assert "Task-NG" in result.stdout
        # Version is dynamic, just check it contains a version-like string
        assert re.search(r"\d+\.\d+\.\d+", result.stdout)


class TestStartStopCommands:
    """Test start/stop time tracking commands."""

    def test_start_command_help(self):
        """Should show help for start command."""
        result = runner.invoke(app, ["start", "--help"])

        assert result.exit_code == 0
        assert "start" in result.stdout.lower()
        assert "tracking" in result.stdout.lower()

    def test_stop_command_help(self):
        """Should show help for stop command."""
        result = runner.invoke(app, ["stop", "--help"])

        assert result.exit_code == 0
        assert "stop" in result.stdout.lower()


class TestStatsCommand:
    """Test stats command."""

    def test_stats_command_help(self):
        """Should show help for stats command."""
        result = runner.invoke(app, ["stats", "--help"])

        assert result.exit_code == 0
        assert "stats" in result.stdout.lower() or "statistics" in result.stdout.lower()

    def test_stats_no_database(self, temp_db_path):
        """Should handle no database gracefully."""
        result = runner.invoke(app, ["stats"])

        assert result.exit_code == 0


class TestProjectSubcommands:
    """Test project subcommand group."""

    def test_project_list_help(self):
        """Should show help for project list."""
        result = runner.invoke(app, ["project", "list", "--help"])

        assert result.exit_code == 0
        assert "project" in result.stdout.lower()

    def test_project_rename_help(self):
        """Should show help for project rename."""
        result = runner.invoke(app, ["project", "rename", "--help"])

        assert result.exit_code == 0
        assert "rename" in result.stdout.lower()


class TestTagSubcommands:
    """Test tag subcommand group."""

    def test_tag_list_help(self):
        """Should show help for tag list."""
        result = runner.invoke(app, ["tag", "list", "--help"])

        assert result.exit_code == 0
        assert "tag" in result.stdout.lower()


class TestBoardSubcommands:
    """Test board subcommand group."""

    def test_board_list_help(self):
        """Should show help for board list."""
        result = runner.invoke(app, ["board", "list", "--help"])

        assert result.exit_code == 0
        assert "board" in result.stdout.lower()

    def test_board_show_help(self):
        """Should show help for board show."""
        result = runner.invoke(app, ["board", "show", "--help"])

        assert result.exit_code == 0
        assert "board" in result.stdout.lower()


class TestReportSubcommands:
    """Test report subcommand group."""

    def test_report_list_help(self):
        """Should show help for report list."""
        result = runner.invoke(app, ["report", "list", "--help"])

        assert result.exit_code == 0
        assert "report" in result.stdout.lower()

    def test_report_run_help(self):
        """Should show help for report run."""
        result = runner.invoke(app, ["report", "run", "--help"])

        assert result.exit_code == 0
        assert "report" in result.stdout.lower()


class TestContextSubcommands:
    """Test context subcommand group."""

    def test_context_list_help(self):
        """Should show help for context list."""
        result = runner.invoke(app, ["context", "list", "--help"])

        assert result.exit_code == 0
        assert "context" in result.stdout.lower()

    def test_context_set_help(self):
        """Should show help for context set."""
        result = runner.invoke(app, ["context", "set", "--help"])

        assert result.exit_code == 0
        assert "context" in result.stdout.lower()

    def test_context_clear_help(self):
        """Should show help for context clear."""
        result = runner.invoke(app, ["context", "clear", "--help"])

        assert result.exit_code == 0
        assert "context" in result.stdout.lower()

    def test_context_show_help(self):
        """Should show help for context show."""
        result = runner.invoke(app, ["context", "show", "--help"])

        assert result.exit_code == 0
        assert "context" in result.stdout.lower()


class TestCalendarCommand:
    """Test calendar command."""

    def test_calendar_help(self):
        """Should show help for calendar command."""
        result = runner.invoke(app, ["calendar", "--help"])

        assert result.exit_code == 0
        assert "calendar" in result.stdout.lower()


class TestUndoCommand:
    """Test undo command."""

    def test_undo_help(self):
        """Should show help for undo command."""
        result = runner.invoke(app, ["undo", "--help"])

        assert result.exit_code == 0
        assert "undo" in result.stdout.lower()


class TestHelpMessages:
    """Test that all commands have proper help messages."""

    def test_main_help(self):
        """Should show main help."""
        result = runner.invoke(app, ["--help"])

        assert result.exit_code == 0
        assert "Task-NG" in result.stdout
        assert (
            "Task Operations" in result.stdout or "operations" in result.stdout.lower()
        )

    def test_active_help(self):
        """Should show help for active command."""
        result = runner.invoke(app, ["active", "--help"])

        assert result.exit_code == 0
        assert "active" in result.stdout.lower()

    def test_add_help(self):
        """Should show help for add command."""
        result = runner.invoke(app, ["add", "--help"])

        assert result.exit_code == 0
        assert "add" in result.stdout.lower()

    def test_annotate_help(self):
        """Should show help for annotate command."""
        result = runner.invoke(app, ["annotate", "--help"])

        assert result.exit_code == 0
        assert "annotate" in result.stdout.lower()

    def test_delete_help(self):
        """Should show help for delete command."""
        result = runner.invoke(app, ["delete", "--help"])

        assert result.exit_code == 0
        assert "delete" in result.stdout.lower()

    def test_denotate_help(self):
        """Should show help for denotate command."""
        result = runner.invoke(app, ["denotate", "--help"])

        assert result.exit_code == 0
        assert (
            "denotate" in result.stdout.lower() or "annotation" in result.stdout.lower()
        )

    def test_done_help(self):
        """Should show help for done command."""
        result = runner.invoke(app, ["done", "--help"])

        assert result.exit_code == 0
        assert "done" in result.stdout.lower() or "complete" in result.stdout.lower()

    def test_edit_help(self):
        """Should show help for edit command."""
        result = runner.invoke(app, ["edit", "--help"])

        assert result.exit_code == 0
        assert "edit" in result.stdout.lower()

    def test_list_help(self):
        """Should show help for list command."""
        result = runner.invoke(app, ["list", "--help"])

        assert result.exit_code == 0
        assert "list" in result.stdout.lower()

    def test_modify_help(self):
        """Should show help for modify command."""
        result = runner.invoke(app, ["modify", "--help"])

        assert result.exit_code == 0
        assert "modify" in result.stdout.lower()

    def test_show_help(self):
        """Should show help for show command."""
        result = runner.invoke(app, ["show", "--help"])

        assert result.exit_code == 0
        assert "show" in result.stdout.lower()

    def test_config_help(self):
        """Should show help for config command."""
        result = runner.invoke(app, ["config", "--help"])

        assert result.exit_code == 0
        assert "config" in result.stdout.lower()

    def test_export_help(self):
        """Should show help for export command."""
        result = runner.invoke(app, ["export", "--help"])

        assert result.exit_code == 0
        assert "export" in result.stdout.lower()

    def test_import_help(self):
        """Should show help for import command."""
        result = runner.invoke(app, ["import", "--help"])

        assert result.exit_code == 0
        assert "import" in result.stdout.lower()

    def test_init_help(self):
        """Should show help for init command."""
        result = runner.invoke(app, ["init", "--help"])

        assert result.exit_code == 0
        assert "init" in result.stdout.lower()
