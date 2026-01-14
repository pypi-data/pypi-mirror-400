"""Integration tests for stats command."""

import json

from taskng.cli.main import app


class TestStatsCommand:
    """Integration tests for stats command."""

    def test_stats_no_tasks(self, temp_db, cli_runner):
        """Should show stats with no tasks."""
        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        # Either shows "No tasks" or shows stats table with zeros
        assert "No tasks" in result.output or "Total Tasks" in result.output

    def test_stats_with_tasks(self, temp_db, cli_runner):
        """Should show task statistics."""
        # Add some tasks
        cli_runner.invoke(
            app, ["add", "Task 1", "--project", "Work", "--priority", "H"]
        )
        cli_runner.invoke(app, ["add", "Task 2", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 3", "--project", "Home"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "Task Statistics" in result.output
        assert "Total Tasks" in result.output
        assert "Pending" in result.output
        assert "3" in result.output  # 3 pending tasks

    def test_stats_shows_completion_rate(self, temp_db, cli_runner):
        """Should show completion rate."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "Completion Rate" in result.output
        assert "50.0%" in result.output

    def test_stats_by_project(self, temp_db, cli_runner):
        """Should show distribution by project."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 2", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 3", "--project", "Home"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "By Project" in result.output
        assert "Work" in result.output
        assert "Home" in result.output

    def test_stats_by_priority(self, temp_db, cli_runner):
        """Should show distribution by priority."""
        cli_runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 3", "--priority", "M"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "By Priority" in result.output
        assert "H" in result.output
        assert "M" in result.output

    def test_stats_by_tag(self, temp_db, cli_runner):
        """Should show distribution by tag."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent"])
        cli_runner.invoke(app, ["add", "Task 2 +urgent +review"])
        cli_runner.invoke(app, ["add", "Task 3 +docs"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "By Tag" in result.output
        assert "urgent" in result.output

    def test_stats_json_output(self, temp_db, cli_runner):
        """Should output stats as JSON."""
        cli_runner.invoke(app, ["add", "Task 1", "--project", "Work"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(app, ["--json", "stats"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data["total"] == 2
        assert data["pending"] == 1
        assert data["completed"] == 1
        assert "completion_rate" in data
        assert "by_project" in data

    def test_stats_overdue_count(self, temp_db, cli_runner):
        """Should count overdue tasks."""
        cli_runner.invoke(app, ["add", "Task 1", "--due", "yesterday"])
        cli_runner.invoke(app, ["add", "Task 2", "--due", "tomorrow"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert "Overdue" in result.output or '"overdue": 1' in result.output

    def test_stats_completed_this_week(self, temp_db, cli_runner):
        """Should show completed this week."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["done", "1"])

        result = cli_runner.invoke(app, ["stats"])

        assert result.exit_code == 0
        assert (
            "Completed This Week" in result.output
            or "completed_this_week" in result.output
        )


class TestStatsFilterSupport:
    """Test filter expression support in stats command."""

    def test_stats_with_project_filter(self, temp_db, cli_runner):
        """Stats command with project filter."""
        cli_runner.invoke(app, ["add", "Task 1", "-p", "Work", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2", "-p", "Work", "--priority", "L"])
        cli_runner.invoke(app, ["add", "Task 3", "-p", "Home", "--priority", "H"])

        result = cli_runner.invoke(app, ["stats", "project:Work"])
        assert result.exit_code == 0

        # Check JSON output for precise verification
        json_result = cli_runner.invoke(app, ["--json", "stats", "project:Work"])
        data = json.loads(json_result.output)
        assert data["total"] == 2  # Only Work tasks
        assert "Work" in data["by_project"]
        assert "Home" not in data["by_project"]

    def test_stats_with_priority_filter(self, temp_db, cli_runner):
        """Stats command with priority filter."""
        cli_runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 3", "--priority", "L"])

        json_result = cli_runner.invoke(app, ["--json", "stats", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 2  # Only high priority tasks
        assert data["by_priority"]["H"] == 2
        assert "L" not in data["by_priority"]

    def test_stats_with_tag_filter(self, temp_db, cli_runner):
        """Stats command with tag filter."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        cli_runner.invoke(app, ["add", "Task 2 +blocked", "-p", "Work"])
        cli_runner.invoke(app, ["add", "Task 3 +urgent", "-p", "Home"])

        json_result = cli_runner.invoke(app, ["--json", "stats", "+urgent"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 2  # Only urgent tasks
        assert data["by_project"]["Work"] == 1
        assert data["by_project"]["Home"] == 1

    def test_stats_with_multiple_filters(self, temp_db, cli_runner):
        """Stats command with multiple filters."""
        cli_runner.invoke(
            app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2 +urgent", "-p", "Work", "--priority", "L"]
        )
        cli_runner.invoke(app, ["add", "Task 3 +blocked", "-p", "Home"])

        json_result = cli_runner.invoke(
            app, ["--json", "stats", "project:Work", "priority:H"]
        )
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 1  # Only Work + high priority
        assert data["by_priority"]["H"] == 1

    def test_stats_with_status_filter(self, temp_db, cli_runner):
        """Stats command with status filter."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["add", "Task 3"])
        cli_runner.invoke(app, ["done", "1"])
        cli_runner.invoke(app, ["done", "2"])

        # Show stats for completed tasks only
        json_result = cli_runner.invoke(app, ["--json", "stats", "status:completed"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 2  # Only completed tasks counted
        assert data["completed"] == 2

    def test_stats_respects_context(self, temp_db, cli_runner):
        """Stats command respects active context."""
        # Set up tasks
        cli_runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        cli_runner.invoke(app, ["add", "Task 2 +blocked", "-p", "Work"])
        cli_runner.invoke(app, ["add", "Task 3 +urgent", "-p", "Home"])

        # Create and activate a context for Work project
        cli_runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Stats should only show Work project
        json_result = cli_runner.invoke(app, ["--json", "stats"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 2  # Only Work tasks
        assert "Work" in data["by_project"]
        assert "Home" not in data["by_project"]

        # Clean up context
        cli_runner.invoke(app, ["context", "none"])

    def test_stats_filter_with_context(self, temp_db, cli_runner):
        """Stats command filter arguments work with context."""
        # Set up tasks
        cli_runner.invoke(
            app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2 +urgent", "-p", "Work", "--priority", "L"]
        )
        cli_runner.invoke(app, ["add", "Task 3", "-p", "Home"])

        # Set context to Work project
        cli_runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Add additional filter for high priority
        json_result = cli_runner.invoke(app, ["--json", "stats", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Should only show Work AND high priority
        assert data["total"] == 1
        assert data["by_priority"]["H"] == 1

        # Clean up
        cli_runner.invoke(app, ["context", "none"])

    def test_stats_with_no_matches(self, temp_db, cli_runner):
        """Stats command with filter that matches nothing."""
        cli_runner.invoke(app, ["add", "Task 1 +work"])

        json_result = cli_runner.invoke(app, ["--json", "stats", "+nonexistent"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        assert data["total"] == 0  # No matching tasks

    def test_stats_shows_filtered_distributions(self, temp_db, cli_runner):
        """Stats shows distribution tables based on filtered tasks."""
        cli_runner.invoke(
            app, ["add", "Task 1 +urgent", "-p", "Work.Backend", "--priority", "H"]
        )
        cli_runner.invoke(
            app, ["add", "Task 2 +urgent", "-p", "Work.Frontend", "--priority", "L"]
        )
        cli_runner.invoke(
            app, ["add", "Task 3 +blocked", "-p", "Home", "--priority", "H"]
        )

        # Filter by Work project
        result = cli_runner.invoke(app, ["stats", "project:Work"])
        assert result.exit_code == 0
        # Should show Work subprojects in distribution
        assert "Backend" in result.output or "Work.Backend" in result.output
        assert "Frontend" in result.output or "Work.Frontend" in result.output
        # Should not show Home
        assert result.output.count("Home") == 0 or "Home" not in result.output

    def test_stats_json_with_filter(self, temp_db, cli_runner):
        """Stats JSON output works with filters."""
        cli_runner.invoke(app, ["add", "Task 1 +urgent", "--priority", "H"])
        cli_runner.invoke(app, ["add", "Task 2 +blocked", "--priority", "L"])
        cli_runner.invoke(app, ["add", "Task 3 +waiting", "--priority", "H"])

        json_result = cli_runner.invoke(app, ["--json", "stats", "priority:H"])
        assert json_result.exit_code == 0
        data = json.loads(json_result.output)
        # Should show only high priority tasks
        assert data["total"] == 2
        assert data["by_priority"]["H"] == 2
        assert "L" not in data["by_priority"]
        # Check tag distribution
        assert data["by_tag"]["urgent"] == 1
        assert data["by_tag"]["waiting"] == 1
        assert "blocked" not in data["by_tag"]
