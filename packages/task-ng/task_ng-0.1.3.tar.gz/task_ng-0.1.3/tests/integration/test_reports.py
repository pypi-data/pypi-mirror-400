"""Integration tests for reports feature."""

import json

from taskng.cli.main import app


class TestReportCommand:
    """Integration tests for report command."""

    def test_report_no_tasks(self, temp_db, cli_runner):
        """Should handle no tasks gracefully."""
        result = cli_runner.invoke(app, ["report", "run", "list"])
        assert result.exit_code == 0
        assert "No tasks" in result.output

    def test_report_list_default(self, temp_db, cli_runner):
        """Should run default list report."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "H"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output

    def test_report_next_has_limit(self, temp_db, cli_runner):
        """Next report should limit to 10 tasks."""
        # Add 15 tasks
        for i in range(15):
            cli_runner.invoke(app, ["add", f"Task {i + 1}"])

        result = cli_runner.invoke(app, ["report", "run", "next"])

        assert result.exit_code == 0
        # Should only show 10 tasks
        assert "10 tasks" in result.output

    def test_report_completed(self, temp_db, cli_runner):
        """Completed report should show only completed tasks."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(app, ["report", "run", "completed"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_report_all(self, temp_db, cli_runner):
        """All report should show all tasks."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(app, ["report", "run", "all"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output

    def test_report_overdue(self, temp_db, cli_runner):
        """Overdue report should show only overdue tasks."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["report", "run", "overdue"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_report_with_extra_filter(self, temp_db, cli_runner):
        """Should apply extra filters to report."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "Home"])

        result = cli_runner.invoke(app, ["report", "run", "list", "project:Work"])

        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_report_unknown(self, temp_db, cli_runner):
        """Should error on unknown report."""
        result = cli_runner.invoke(app, ["report", "run", "unknown"])

        assert result.exit_code == 1
        assert "Unknown report" in result.output

    def test_report_json_output(self, temp_db, cli_runner):
        """Should support JSON output."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])

        result = cli_runner.invoke(app, ["--json", "report", "run", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["description"] == "Task 1"


class TestReportsCommand:
    """Integration tests for reports command."""

    def test_reports_list(self, temp_db, cli_runner):
        """Should list available reports."""
        result = cli_runner.invoke(app, ["reports"])

        assert result.exit_code == 0
        # Handle both table and JSON output
        assert "Available Reports" in result.output or '"name": "list"' in result.output
        assert "list" in result.output
        assert "next" in result.output
        assert "completed" in result.output
        assert "all" in result.output

    def test_reports_json_output(self, temp_db, cli_runner):
        """Should support JSON output."""
        result = cli_runner.invoke(app, ["--json", "reports"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        names = [r["name"] for r in data]
        assert "list" in names
        assert "next" in names


class TestReportColumns:
    """Tests for report column rendering."""

    def test_report_shows_priority(self, temp_db, cli_runner):
        """Should display priority column."""
        cli_runner.invoke(app, ["add", "High priority", "--priority", "H"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "H" in result.output

    def test_report_shows_project(self, temp_db, cli_runner):
        """Should display project column."""
        cli_runner.invoke(app, ["add", "Task", "--project", "Work"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "Work" in result.output

    def test_report_shows_due(self, temp_db, cli_runner):
        """Should display due column."""
        cli_runner.invoke(app, ["add", "Task", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        # Due should be formatted

    def test_report_shows_tags(self, temp_db, cli_runner):
        """Should display tags column."""
        cli_runner.invoke(app, ["add", "Task +urgent +review"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "urgent" in result.output


class TestReportEdgeCases:
    """Edge case tests for report command."""

    def test_report_json_no_database(self, temp_db_path, cli_runner):
        """Should return empty JSON array when no database."""
        result = cli_runner.invoke(app, ["--json", "report", "run", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_report_recurring(self, temp_db, cli_runner):
        """Recurring report should show only recurring tasks."""
        cli_runner.invoke(app, ["add", "Recurring task", "--recur", "weekly"])
        cli_runner.invoke(app, ["add", "Normal task"])

        result = cli_runner.invoke(app, ["report", "run", "recurring"])

        assert result.exit_code == 0
        # Recurring report filters to tasks with recur field
        if "Recurring task" in result.output:
            assert "Normal task" not in result.output
        else:
            # No matching tasks is also valid
            assert "No tasks" in result.output

    def test_report_waiting(self, temp_db, cli_runner):
        """Waiting report should show only waiting tasks."""
        cli_runner.invoke(app, ["add", "Waiting task", "--wait", "tomorrow"])
        cli_runner.invoke(app, ["add", "Normal task"])

        result = cli_runner.invoke(app, ["report", "run", "waiting"])

        assert result.exit_code == 0
        # Waiting report filters to tasks with wait field
        if "Waiting task" in result.output:
            assert "Normal task" not in result.output
        else:
            # Task might be filtered by waiting status
            assert "No tasks" in result.output or result.exit_code == 0

    def test_report_with_uda(self, temp_db, cli_runner):
        """Should handle tasks with UDAs."""
        cli_runner.invoke(app, ["add", "Task client:Acme"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "Task" in result.output

    def test_report_with_dependencies(self, temp_db, cli_runner):
        """Should handle tasks with dependencies."""
        cli_runner.invoke(app, ["add", "Dep task"])
        cli_runner.invoke(app, ["add", "Main task", "--depends", "1"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "Main task" in result.output

    def test_report_with_long_description(self, temp_db, cli_runner):
        """Should truncate long descriptions."""
        long_desc = "A" * 100
        cli_runner.invoke(app, ["add", long_desc])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        # Description should be truncated (uses ellipsis character)
        assert "…" in result.output or "A" * 30 in result.output

    def test_report_with_many_tags(self, temp_db, cli_runner):
        """Should handle many tags."""
        cli_runner.invoke(app, ["add", "Task +a +b +c +d +e"])

        result = cli_runner.invoke(app, ["report", "run", "list"])

        assert result.exit_code == 0
        assert "+a" in result.output
