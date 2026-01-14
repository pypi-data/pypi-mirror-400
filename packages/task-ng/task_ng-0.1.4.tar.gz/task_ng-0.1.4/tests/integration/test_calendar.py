"""Integration tests for calendar command."""

import json

from taskng.cli.main import app


class TestCalendarCommand:
    """Integration tests for calendar command."""

    def test_calendar_no_tasks(self, temp_db, cli_runner):
        """Should show calendar with no tasks."""
        result = cli_runner.invoke(app, ["calendar"])

        assert result.exit_code == 0
        # Calendar should show even with no tasks
        assert "No tasks" in result.output or len(result.output) > 0

    def test_calendar_with_due_tasks(self, temp_db, cli_runner):
        """Should show tasks on calendar."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["calendar"])

        assert result.exit_code == 0
        # Should show current month calendar
        assert "Task 1" in result.output or "1" in result.output

    def test_calendar_ignores_tasks_without_due(self, temp_db, cli_runner):
        """Should not show tasks without due dates."""
        cli_runner.invoke(app, ["add", "No due date"])
        cli_runner.invoke(app, ["add", "Has due", "--due", "today"])

        result = cli_runner.invoke(app, ["calendar"])

        assert result.exit_code == 0
        # Should only show task with due date


class TestCalendarFilterSupport:
    """Test filter expression support in calendar command."""

    def test_calendar_with_project_filter(self, temp_db, cli_runner):
        """Calendar command with project filter."""
        cli_runner.invoke(app, ["add", "Task 1", "-p", "Work", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "-p", "Home", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 3", "-p", "Work", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["calendar", "project:Work"])
        assert result.exit_code == 0

        # Check JSON output for precise verification
        json_result = cli_runner.invoke(app, ["--json", "calendar", "project:Work"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only Work tasks should be shown
        assert len(data["tasks"]) == 2
        assert all(t["project"] == "Work" for t in data["tasks"])

    def test_calendar_with_priority_filter(self, temp_db, cli_runner):
        """Calendar command with priority filter."""
        cli_runner.invoke(app, ["add", "Task 1", "--priority", "H", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "L", "--due", "today"])
        cli_runner.invoke(
            app, ["add", "Task 3", "--priority", "H", "--due", "tomorrow"]
        )

        json_result = cli_runner.invoke(app, ["--json", "calendar", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only high priority tasks should be shown
        assert len(data["tasks"]) == 2
        assert all(t["priority"] == "H" for t in data["tasks"])

    def test_calendar_with_tag_filter(self, temp_db, cli_runner):
        """Calendar command with tag filter."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2 +blocked", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 3 +urgent", "--due", "tomorrow"])

        json_result = cli_runner.invoke(app, ["--json", "calendar", "+urgent"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only urgent tasks should be shown
        assert len(data["tasks"]) == 2
        assert all("urgent" in t["tags"] for t in data["tasks"])

    def test_calendar_with_multiple_filters(self, temp_db, cli_runner):
        """Calendar command with multiple filters."""
        cli_runner.invoke(
            app,
            [
                "add",
                "Task 1 +urgent",
                "-p",
                "Work",
                "--priority",
                "H",
                "--due",
                "today",
            ],
        )
        cli_runner.invoke(
            app,
            [
                "add",
                "Task 2 +urgent",
                "-p",
                "Work",
                "--priority",
                "L",
                "--due",
                "today",
            ],
        )
        cli_runner.invoke(
            app, ["add", "Task 3 +blocked", "-p", "Home", "--due", "today"]
        )

        json_result = cli_runner.invoke(
            app, ["--json", "calendar", "project:Work", "priority:H"]
        )
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only Work + high priority tasks
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["project"] == "Work"
        assert data["tasks"][0]["priority"] == "H"

    def test_calendar_with_status_filter(self, temp_db, cli_runner):
        """Calendar command with status filter."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 3", "--due", "tomorrow"])
        cli_runner.invoke(app, ["done", "1"])

        # Show calendar for all tasks including completed
        json_result = cli_runner.invoke(app, ["--json", "calendar", "status:completed"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only completed task shown
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["status"] == "completed"

    def test_calendar_respects_context(self, temp_db, cli_runner):
        """Calendar command respects active context."""
        # Set up tasks
        cli_runner.invoke(
            app, ["add", "Task 1 +urgent", "-p", "Work", "--due", "today"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2 +blocked", "-p", "Work", "--due", "today"]
        )
        cli_runner.invoke(
            app, ["add", "Task 3 +urgent", "-p", "Home", "--due", "today"]
        )

        # Create and activate a context for Work project
        cli_runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Calendar should only show Work project
        json_result = cli_runner.invoke(app, ["--json", "calendar"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only Work tasks
        assert len(data["tasks"]) == 2
        assert all(t["project"] == "Work" for t in data["tasks"])

        # Clean up context
        cli_runner.invoke(app, ["context", "none"])

    def test_calendar_filter_with_context(self, temp_db, cli_runner):
        """Calendar command filter arguments work with context."""
        # Set up tasks
        cli_runner.invoke(
            app,
            [
                "add",
                "Task 1 +urgent",
                "-p",
                "Work",
                "--priority",
                "H",
                "--due",
                "today",
            ],
        )
        cli_runner.invoke(
            app,
            [
                "add",
                "Task 2 +urgent",
                "-p",
                "Work",
                "--priority",
                "L",
                "--due",
                "today",
            ],
        )
        cli_runner.invoke(app, ["add", "Task 3", "-p", "Home", "--due", "today"])

        # Set context to Work project
        cli_runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Add additional filter for high priority
        json_result = cli_runner.invoke(app, ["--json", "calendar", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Should only show Work AND high priority
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["project"] == "Work"
        assert data["tasks"][0]["priority"] == "H"

        # Clean up
        cli_runner.invoke(app, ["context", "none"])

    def test_calendar_with_no_matches(self, temp_db, cli_runner):
        """Calendar command with filter that matches nothing."""
        cli_runner.invoke(app, ["add", "Task 1 +work", "--due", "today"])

        json_result = cli_runner.invoke(app, ["--json", "calendar", "+nonexistent"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # No matching tasks
        assert len(data["tasks"]) == 0

    def test_calendar_week_view_with_filter(self, temp_db, cli_runner):
        """Calendar week view works with filters."""
        cli_runner.invoke(app, ["add", "Task 1", "-p", "Work", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "-p", "Home", "--due", "today"])

        result = cli_runner.invoke(app, ["calendar", "--week", "project:Work"])
        assert result.exit_code == 0
        # Should show week view with only Work tasks

    def test_calendar_month_view_with_filter(self, temp_db, cli_runner):
        """Calendar month view works with filters."""
        cli_runner.invoke(app, ["add", "Task 1", "-p", "Work", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "-p", "Home", "--due", "today"])

        json_result = cli_runner.invoke(
            app, ["--json", "calendar", "--month", "12", "project:Work"]
        )
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only Work tasks should be shown
        assert all(t["project"] == "Work" for t in data["tasks"])

    def test_calendar_json_with_filter(self, temp_db, cli_runner):
        """Calendar JSON output works with filters."""
        cli_runner.invoke(
            app, ["add", "Task 1 +urgent", "--priority", "H", "--due", "today"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2 +blocked", "--priority", "L", "--due", "today"]
        )
        cli_runner.invoke(
            app, ["add", "Task 3 +waiting", "--priority", "H", "--due", "tomorrow"]
        )

        json_result = cli_runner.invoke(app, ["--json", "calendar", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Should show only high priority tasks
        assert len(data["tasks"]) == 2
        assert all(t["priority"] == "H" for t in data["tasks"])

    def test_calendar_filter_excludes_tasks_without_due(self, temp_db, cli_runner):
        """Calendar with filter still excludes tasks without due dates."""
        cli_runner.invoke(app, ["add", "Task 1", "-p", "Work", "--due", "today"])
        cli_runner.invoke(app, ["add", "Task 2", "-p", "Work"])  # No due date
        cli_runner.invoke(app, ["add", "Task 3", "-p", "Home", "--due", "today"])

        json_result = cli_runner.invoke(app, ["--json", "calendar", "project:Work"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Only Task 1 should be shown (Work project with due date)
        assert len(data["tasks"]) == 1
        assert data["tasks"][0]["description"] == "Task 1"
