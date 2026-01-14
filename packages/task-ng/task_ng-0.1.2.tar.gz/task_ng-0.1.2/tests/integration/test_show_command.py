"""Integration tests for task show command."""

from taskng.cli.main import app


class TestShowCommand:
    """Integration tests for show command."""

    def test_show_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["show", "999"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_show_no_database(self, temp_db_path, cli_runner):
        """Should error when no database exists."""
        result = cli_runner.invoke(app, ["show", "1"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_show_basic_task(self, temp_db, cli_runner):
        """Should display basic task information."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Test task" in result.output
        assert "pending" in result.output

    def test_show_displays_uuid(self, temp_db, cli_runner):
        """Should display full UUID."""
        cli_runner.invoke(app, ["add", "UUID task"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "UUID" in result.output
        # UUID format has dashes
        assert "-" in result.output

    def test_show_with_priority(self, temp_db, cli_runner):
        """Should display priority."""
        cli_runner.invoke(app, ["add", "High priority", "--priority", "H"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Priority" in result.output
        assert "H" in result.output

    def test_show_with_project(self, temp_db, cli_runner):
        """Should display project."""
        cli_runner.invoke(app, ["add", "Work task", "--project", "Work"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Project" in result.output
        assert "Work" in result.output

    def test_show_with_tags(self, temp_db, cli_runner):
        """Should display tags."""
        cli_runner.invoke(app, ["add", "Tagged task +urgent +important"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Tags" in result.output
        assert "+urgent" in result.output
        assert "+important" in result.output

    def test_show_displays_dates(self, temp_db, cli_runner):
        """Should display created and modified dates."""
        cli_runner.invoke(app, ["add", "Dated task"])
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Created" in result.output
        assert "Modified" in result.output

    def test_show_multiple_tasks(self, temp_db, cli_runner):
        """Should show correct task by ID."""
        cli_runner.invoke(app, ["add", "First task"])
        cli_runner.invoke(app, ["add", "Second task"])
        cli_runner.invoke(app, ["add", "Third task"])

        result = cli_runner.invoke(app, ["show", "2"])

        assert result.exit_code == 0
        assert "Second task" in result.output
        assert "First task" not in result.output
        assert "Third task" not in result.output

    def test_show_full_task(self, temp_db, cli_runner):
        """Should display task with all attributes."""
        cli_runner.invoke(
            app,
            ["add", "Full task +tag1 +tag2", "--project", "Test", "--priority", "M"],
        )
        result = cli_runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        assert "Full task" in result.output
        assert "Test" in result.output
        assert "M" in result.output
        assert "+tag1" in result.output
        assert "+tag2" in result.output
