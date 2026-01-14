"""Integration tests for tags command."""

import json

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_db(isolate_test_data):
    return isolate_test_data / "task.db"


class TestTagsCommand:
    def test_tags_no_tasks(self, runner, temp_db):
        """Tags with no tasks shows message."""
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_tags_no_tags(self, runner, temp_db):
        """Tags with tasks but no tags shows message."""
        runner.invoke(app, ["add", "Task without tags"])
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "No tags found" in result.output

    def test_tags_single_tag(self, runner, temp_db):
        """Tags shows single tag with count."""
        runner.invoke(app, ["add", "Task +urgent"])
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "urgent" in result.output
        assert "1" in result.output

    def test_tags_multiple_tags(self, runner, temp_db):
        """Tags shows multiple tags with counts."""
        runner.invoke(app, ["add", "Task 1 +work +urgent"])
        runner.invoke(app, ["add", "Task 2 +work"])
        runner.invoke(app, ["add", "Task 3 +home"])
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "work" in result.output
        assert "urgent" in result.output
        assert "home" in result.output

    def test_tags_sorted_by_count(self, runner, temp_db):
        """Tags are sorted by count descending."""
        runner.invoke(app, ["add", "Task 1 +work"])
        runner.invoke(app, ["add", "Task 2 +work"])
        runner.invoke(app, ["add", "Task 3 +work"])
        runner.invoke(app, ["add", "Task 4 +home"])
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        # work should appear before home (3 vs 1)
        work_pos = result.output.find("work")
        home_pos = result.output.find("home")
        assert work_pos < home_pos

    def test_tags_virtual_flag(self, runner, temp_db):
        """Tags with --virtual shows virtual tags."""
        runner.invoke(app, ["add", "Task +work"])
        result = runner.invoke(app, ["tags", "--virtual"])
        assert result.exit_code == 0
        assert "work" in result.output
        assert "PENDING" in result.output
        assert "OVERDUE" in result.output

    def test_tags_virtual_short_flag(self, runner, temp_db):
        """Tags with -v shows virtual tags."""
        runner.invoke(app, ["add", "Task +work"])
        result = runner.invoke(app, ["tags", "-v"])
        assert result.exit_code == 0
        assert "PENDING" in result.output

    def test_tags_json_output(self, runner, temp_db):
        """Tags with --json outputs JSON."""
        runner.invoke(app, ["add", "Task 1 +work"])
        runner.invoke(app, ["add", "Task 2 +work"])
        runner.invoke(app, ["add", "Task 3 +home"])
        result = runner.invoke(app, ["--json", "tags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 2
        # Should be sorted by count
        assert data[0]["tag"] == "work"
        assert data[0]["count"] == 2
        assert data[1]["tag"] == "home"
        assert data[1]["count"] == 1

    def test_tags_json_with_virtual(self, runner, temp_db):
        """Tags JSON output includes virtual tags when requested."""
        runner.invoke(app, ["add", "Task +work"])
        result = runner.invoke(app, ["--json", "tags", "--virtual"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        # Should have work tag plus virtual tags
        tags = [item["tag"] for item in data]
        assert "work" in tags
        assert "PENDING" in tags

    def test_tags_json_no_tasks(self, runner, temp_db):
        """Tags JSON with no tasks returns empty list."""
        result = runner.invoke(app, ["--json", "tags"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_tags_counts_completed_tasks(self, runner, temp_db):
        """Tags counts include completed tasks."""
        runner.invoke(app, ["add", "Task 1 +work"])
        runner.invoke(app, ["add", "Task 2 +work"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "work" in result.output
        # Both tasks should be counted
        assert "2" in result.output


class TestTagsFilterSupport:
    """Test filter expression support in tags command."""

    def test_tags_with_project_filter(self, runner, temp_db):
        """Tags command with project filter."""
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2 +blocked", "-p", "Work"])
        runner.invoke(app, ["add", "Task 3 +urgent", "-p", "Home"])
        result = runner.invoke(app, ["tags", "project:Work"])
        assert result.exit_code == 0
        # Should show tags from Work project only
        assert "urgent" in result.output
        assert "blocked" in result.output

    def test_tags_with_priority_filter(self, runner, temp_db):
        """Tags command with priority filter."""
        runner.invoke(app, ["add", "Task 1 +urgent", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +blocked", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3 +waiting", "--priority", "H"])
        result = runner.invoke(app, ["tags", "priority:H"])
        assert result.exit_code == 0
        # Should show only tags from high priority tasks
        assert "urgent" in result.output
        assert "waiting" in result.output
        assert "blocked" not in result.output

    def test_tags_with_tag_filter(self, runner, temp_db):
        """Tags command with tag filter shows other tags on matching tasks."""
        runner.invoke(app, ["add", "Task 1 +urgent +work"])
        runner.invoke(app, ["add", "Task 2 +urgent +home"])
        runner.invoke(app, ["add", "Task 3 +blocked +work"])
        result = runner.invoke(app, ["tags", "+urgent"])
        assert result.exit_code == 0
        # Should show all tags on tasks that have +urgent
        assert "urgent" in result.output
        assert "work" in result.output
        assert "home" in result.output
        # Should not show tags from non-urgent tasks
        assert "blocked" not in result.output

    def test_tags_with_multiple_filters(self, runner, temp_db):
        """Tags command with multiple filters."""
        runner.invoke(
            app, ["add", "Task 1 +urgent +backend", "-p", "Work", "--priority", "H"]
        )
        runner.invoke(
            app, ["add", "Task 2 +urgent +frontend", "-p", "Work", "--priority", "L"]
        )
        runner.invoke(
            app, ["add", "Task 3 +blocked +backend", "-p", "Home", "--priority", "H"]
        )
        result = runner.invoke(app, ["tags", "project:Work", "priority:H"])
        assert result.exit_code == 0
        # Should show tags from Work project with high priority only
        assert "urgent" in result.output
        assert "backend" in result.output
        assert "frontend" not in result.output
        assert "blocked" not in result.output

    def test_tags_with_status_filter(self, runner, temp_db):
        """Tags command with status filter."""
        runner.invoke(app, ["add", "Task 1 +urgent"])
        runner.invoke(app, ["add", "Task 2 +blocked"])
        runner.invoke(app, ["done", "1"])
        # Show only tags from completed tasks
        result = runner.invoke(app, ["tags", "status:completed"])
        assert result.exit_code == 0
        assert "urgent" in result.output
        assert "blocked" not in result.output

    def test_tags_respects_context(self, runner, temp_db):
        """Tags command respects active context."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent +backend", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2 +blocked +frontend", "-p", "Work"])
        runner.invoke(app, ["add", "Task 3 +urgent +personal", "-p", "Home"])

        # Create and activate a context for Work project
        runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Tags should only show tags from Work project
        result = runner.invoke(app, ["tags"])
        assert result.exit_code == 0
        assert "urgent" in result.output
        assert "backend" in result.output
        assert "blocked" in result.output
        assert "frontend" in result.output
        # Should not show tags from Home project
        assert "personal" not in result.output

        # Clean up context
        runner.invoke(app, ["context", "none"])

    def test_tags_filter_with_context(self, runner, temp_db):
        """Tags command filter arguments work with context."""
        # Set up tasks
        runner.invoke(
            app, ["add", "Task 1 +urgent +backend", "-p", "Work", "--priority", "H"]
        )
        runner.invoke(
            app, ["add", "Task 2 +urgent +frontend", "-p", "Work", "--priority", "L"]
        )
        runner.invoke(app, ["add", "Task 3 +blocked", "-p", "Home"])

        # Set context to Work project
        runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Add additional filter for high priority
        result = runner.invoke(app, ["tags", "priority:H"])
        assert result.exit_code == 0
        # Should show tags from Work AND high priority only
        assert "urgent" in result.output
        assert "backend" in result.output
        assert "frontend" not in result.output
        assert "blocked" not in result.output

        # Clean up
        runner.invoke(app, ["context", "none"])

    def test_tags_with_no_matches(self, runner, temp_db):
        """Tags command with filter that matches nothing."""
        runner.invoke(app, ["add", "Task 1 +work"])
        result = runner.invoke(app, ["tags", "+nonexistent"])
        assert result.exit_code == 0
        assert "No tags found" in result.output

    def test_tags_json_with_filter(self, runner, temp_db):
        """Tags JSON output works with filters."""
        runner.invoke(app, ["add", "Task 1 +urgent", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +blocked", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3 +waiting", "--priority", "H"])
        result = runner.invoke(app, ["--json", "tags", "priority:H"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        # Should show only tags from high priority tasks
        tags = [item["tag"] for item in data]
        assert "urgent" in tags
        assert "waiting" in tags
        assert "blocked" not in tags

    def test_tags_filter_by_specific_project_hierarchy(self, runner, temp_db):
        """Tags command respects project hierarchy in filters."""
        runner.invoke(app, ["add", "Task 1 +api +backend", "-p", "Work.Backend"])
        runner.invoke(app, ["add", "Task 2 +ui +frontend", "-p", "Work.Frontend"])
        runner.invoke(app, ["add", "Task 3 +personal", "-p", "Home"])
        # Filter by Work should include all Work.* projects
        result = runner.invoke(app, ["tags", "project:Work"])
        assert result.exit_code == 0
        assert "api" in result.output
        assert "backend" in result.output
        assert "ui" in result.output
        assert "frontend" in result.output
        assert "personal" not in result.output
