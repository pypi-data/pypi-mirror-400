"""Integration tests for project list command and hierarchy filtering."""

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


class TestProjectsCommand:
    def test_projects_no_tasks(self, runner, temp_db):
        """Projects with no tasks shows message."""
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "No tasks found" in result.output

    def test_projects_no_projects(self, runner, temp_db):
        """Projects with tasks but no projects shows message."""
        runner.invoke(app, ["add", "Task without project"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_projects_single_project(self, runner, temp_db):
        """Projects shows single project."""
        runner.invoke(app, ["add", "Task", "-p", "Work"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work" in result.output
        assert "(1)" in result.output

    def test_projects_multiple_projects(self, runner, temp_db):
        """Projects shows multiple projects."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Home"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work" in result.output
        assert "Home" in result.output

    def test_projects_hierarchy(self, runner, temp_db):
        """Projects shows hierarchical structure."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend"])
        runner.invoke(app, ["add", "Task 3", "-p", "Work.Backend.API"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work" in result.output
        assert "Backend" in result.output
        assert "API" in result.output

    def test_projects_counts(self, runner, temp_db):
        """Projects shows correct counts."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        runner.invoke(app, ["add", "Task 3", "-p", "Work.Backend"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        # Work should show (2/3) - 2 direct, 3 total
        assert "Work" in result.output

    def test_projects_json_output(self, runner, temp_db):
        """Projects with --json outputs JSON."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend"])
        result = runner.invoke(app, ["--json", "project", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["name"] == "Work"
        assert data[0]["count"] == 1
        assert data[0]["total"] == 2
        assert len(data[0]["children"]) == 1
        assert data[0]["children"][0]["name"] == "Backend"

    def test_projects_json_empty(self, runner, temp_db):
        """Projects JSON with no projects returns empty list."""
        result = runner.invoke(app, ["--json", "project", "list"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_projects_excludes_completed_by_default(self, runner, temp_db):
        """Projects excludes completed tasks by default."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        # Complete one task
        runner.invoke(app, ["done", "2"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work (1)" in result.output

    def test_projects_excludes_waiting_by_default(self, runner, temp_db):
        """Projects excludes waiting tasks by default."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work", "--wait", "tomorrow"])
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work (1)" in result.output

    def test_projects_all_flag_includes_completed(self, runner, temp_db):
        """Projects --all includes completed tasks."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        runner.invoke(app, ["done", "2"])
        result = runner.invoke(app, ["project", "list", "--all"])
        assert result.exit_code == 0
        assert "Work (2)" in result.output

    def test_projects_all_flag_includes_waiting(self, runner, temp_db):
        """Projects --all includes waiting tasks."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work", "--wait", "tomorrow"])
        result = runner.invoke(app, ["project", "list", "--all"])
        assert result.exit_code == 0
        assert "Work (2)" in result.output


class TestHierarchyFiltering:
    def test_filter_exact_project(self, runner, temp_db):
        """Filter by exact project name."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Home"])
        result = runner.invoke(app, ["list", "project:Work"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output

    def test_filter_includes_children(self, runner, temp_db):
        """Filter by parent project includes children."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend"])
        runner.invoke(app, ["add", "Task 3", "-p", "Work.Backend.API"])
        runner.invoke(app, ["add", "Task 4", "-p", "Home"])
        result = runner.invoke(app, ["list", "project:Work"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output
        assert "Task 3" in result.output
        assert "Task 4" not in result.output

    def test_filter_specific_child(self, runner, temp_db):
        """Filter by child project only shows that branch."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend"])
        runner.invoke(app, ["add", "Task 3", "-p", "Work.Frontend"])
        result = runner.invoke(app, ["list", "project:Work.Backend"])
        assert result.exit_code == 0
        assert "Task 1" not in result.output
        assert "Task 2" in result.output
        assert "Task 3" not in result.output

    def test_filter_deep_hierarchy(self, runner, temp_db):
        """Filter works with deep hierarchies."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work.Backend.API.v1"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend.API.v2"])
        runner.invoke(app, ["add", "Task 3", "-p", "Work.Frontend"])
        result = runner.invoke(app, ["list", "project:Work.Backend.API"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" in result.output
        assert "Task 3" not in result.output

    def test_filter_no_partial_match(self, runner, temp_db):
        """Filter doesn't match partial project names."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Workshop"])
        result = runner.invoke(app, ["list", "project:Work"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output


class TestProjectsFilterSupport:
    """Test filter expression support in projects command."""

    def test_projects_with_priority_filter(self, runner, temp_db):
        """Projects command with priority filter."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home", "--priority", "H"])
        result = runner.invoke(app, ["project", "list", "priority:H"])
        assert result.exit_code == 0
        # Should show both Work and Home with 1 task each
        assert "Work" in result.output
        assert "Home" in result.output

    def test_projects_with_tag_filter(self, runner, temp_db):
        """Projects command with tag filter."""
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        runner.invoke(app, ["add", "Task 3 +urgent", "-p", "Home"])
        result = runner.invoke(app, ["project", "list", "+urgent"])
        assert result.exit_code == 0
        # Should show both Work and Home with urgent tasks only
        assert "Work" in result.output
        assert "Home" in result.output
        # Work should show (1) not (2)
        assert "Work (1)" in result.output

    def test_projects_with_project_filter(self, runner, temp_db):
        """Projects command with project filter."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work.Backend"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home"])
        result = runner.invoke(app, ["project", "list", "project:Work"])
        assert result.exit_code == 0
        # Should only show Work hierarchy
        assert "Work" in result.output
        assert "Backend" in result.output
        assert "Home" not in result.output

    def test_projects_with_multiple_filters(self, runner, temp_db):
        """Projects command with multiple filters."""
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home", "--priority", "H"])
        result = runner.invoke(app, ["project", "list", "priority:H", "+urgent"])
        assert result.exit_code == 0
        # Should only show Work with the one task matching both filters
        assert "Work (1)" in result.output
        assert "Home" not in result.output

    def test_projects_with_status_filter(self, runner, temp_db):
        """Projects command with status filter."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        runner.invoke(app, ["done", "2"])
        # Show only completed tasks
        result = runner.invoke(app, ["project", "list", "status:completed"])
        assert result.exit_code == 0
        assert "Work (1)" in result.output

    def test_projects_respects_context(self, runner, temp_db):
        """Projects command respects active context."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home"])

        # Create and activate a context for urgent tasks
        runner.invoke(app, ["context", "set", "urgent", "+urgent"])

        # Projects should only show Work (the one with urgent task)
        result = runner.invoke(app, ["project", "list"])
        assert result.exit_code == 0
        assert "Work (1)" in result.output
        assert "Home" not in result.output

        # Clean up context
        runner.invoke(app, ["context", "none"])

    def test_projects_filter_overrides_context(self, runner, temp_db):
        """Projects command filter arguments work with context."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +urgent", "-p", "Work", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home"])

        # Set context to urgent tasks
        runner.invoke(app, ["context", "set", "urgent", "+urgent"])

        # Add additional filter for high priority
        result = runner.invoke(app, ["project", "list", "priority:H"])
        assert result.exit_code == 0
        # Should only show Work with 1 task (urgent AND high priority)
        assert "Work (1)" in result.output
        assert "Home" not in result.output

        # Clean up
        runner.invoke(app, ["context", "none"])

    def test_projects_with_no_matches_shows_message(self, runner, temp_db):
        """Projects command with filter that matches nothing."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        result = runner.invoke(app, ["project", "list", "+nonexistent"])
        assert result.exit_code == 0
        assert "No projects found" in result.output

    def test_projects_json_with_filter(self, runner, temp_db):
        """Projects JSON output works with filters."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2", "-p", "Work", "--priority", "L"])
        runner.invoke(app, ["add", "Task 3", "-p", "Home", "--priority", "H"])
        result = runner.invoke(app, ["--json", "project", "list", "priority:H"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        # Should show both Work and Home with 1 task each
        assert len(data) == 2
        project_names = {p["name"] for p in data}
        assert "Work" in project_names
        assert "Home" in project_names
