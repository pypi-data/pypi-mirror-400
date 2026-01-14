"""Integration tests for exclusion filters."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestProjectExclusion:
    """Tests for project.not: exclusion."""

    def test_exclude_project(self, runner, temp_db):
        """Should exclude tasks from a project."""
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Personal task", "-p", "Personal"])
        runner.invoke(app, ["add", "No project task"])

        result = runner.invoke(app, ["list", "project.not:Work"])
        assert result.exit_code == 0
        assert "Personal task" in result.output
        assert "No project task" in result.output
        assert "Work task" not in result.output

    def test_exclude_project_hierarchy(self, runner, temp_db):
        """Should exclude project and children."""
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Work sub task", "-p", "Work.Frontend"])
        runner.invoke(app, ["add", "Personal task", "-p", "Personal"])

        result = runner.invoke(app, ["list", "project.not:Work"])
        assert result.exit_code == 0
        assert "Personal task" in result.output
        assert "Work task" not in result.output
        assert "Work sub task" not in result.output


class TestPriorityExclusion:
    """Tests for priority.not: exclusion."""

    def test_exclude_priority(self, runner, temp_db):
        """Should exclude tasks with specific priority."""
        runner.invoke(app, ["add", "High priority", "-P", "H"])
        runner.invoke(app, ["add", "Medium priority", "-P", "M"])
        runner.invoke(app, ["add", "No priority"])

        result = runner.invoke(app, ["list", "priority.not:H"])
        assert result.exit_code == 0
        assert "Medium priority" in result.output
        assert "No priority" in result.output
        assert "High priority" not in result.output


class TestStatusExclusion:
    """Tests for status.not: exclusion."""

    def test_exclude_status(self, runner, temp_db):
        """Should exclude tasks with specific status."""
        runner.invoke(app, ["add", "Task one"])
        runner.invoke(app, ["add", "Task two"])
        runner.invoke(app, ["done", "1"])

        result = runner.invoke(app, ["list", "status.not:completed"])
        assert result.exit_code == 0
        assert "Task two" in result.output
        assert "Task one" not in result.output


class TestCombinedFilters:
    """Tests for combined inclusion/exclusion filters."""

    def test_project_with_tag_exclusion(self, runner, temp_db):
        """Should combine project inclusion with tag exclusion."""
        runner.invoke(app, ["add", "Work urgent +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Work normal", "-p", "Work"])
        runner.invoke(app, ["add", "Personal task", "-p", "Personal"])

        # Use -- to separate options from filter arguments
        result = runner.invoke(app, ["list", "--", "project:Work", "-urgent"])
        assert result.exit_code == 0
        assert "Work normal" in result.output
        assert "Work urgent" not in result.output
        assert "Personal task" not in result.output

    def test_exclude_project_with_priority(self, runner, temp_db):
        """Should combine project exclusion with priority inclusion."""
        runner.invoke(app, ["add", "Work high", "-p", "Work", "-P", "H"])
        runner.invoke(app, ["add", "Personal high", "-p", "Personal", "-P", "H"])
        runner.invoke(app, ["add", "Personal low", "-p", "Personal", "-P", "L"])

        result = runner.invoke(app, ["list", "project.not:Work", "priority:H"])
        assert result.exit_code == 0
        assert "Personal high" in result.output
        assert "Work high" not in result.output
        assert "Personal low" not in result.output

    def test_multiple_exclusions(self, runner, temp_db):
        """Should handle multiple exclusion filters."""
        runner.invoke(app, ["add", "Work high", "-p", "Work", "-P", "H"])
        runner.invoke(app, ["add", "Work low", "-p", "Work", "-P", "L"])
        runner.invoke(app, ["add", "Personal high", "-p", "Personal", "-P", "H"])
        runner.invoke(app, ["add", "Personal low", "-p", "Personal", "-P", "L"])

        result = runner.invoke(app, ["list", "project.not:Work", "priority.not:L"])
        assert result.exit_code == 0
        assert "Personal high" in result.output
        assert "Work high" not in result.output
        assert "Personal low" not in result.output


class TestBulkOperationsWithExclusion:
    """Tests for bulk operations with exclusion filters."""

    def test_done_with_project_exclusion(self, runner, temp_db):
        """Should complete tasks except those in excluded project."""
        runner.invoke(app, ["add", "Work task", "-p", "Work"])
        runner.invoke(app, ["add", "Personal task", "-p", "Personal"])

        result = runner.invoke(app, ["done", "project.not:Work", "--force"])
        assert result.exit_code == 0
        assert "Completed 1 task(s)" in result.output

        # Verify work task still pending
        result = runner.invoke(app, ["list"])
        assert "Work task" in result.output
        assert "Personal task" not in result.output

    def test_modify_with_priority_exclusion(self, runner, temp_db):
        """Should modify tasks except those with excluded priority."""
        runner.invoke(app, ["add", "High task", "-P", "H"])
        runner.invoke(app, ["add", "Low task", "-P", "L"])

        result = runner.invoke(
            app, ["modify", "priority.not:H", "-t", "updated", "--force"]
        )
        assert result.exit_code == 0
        assert "Modified 1 task(s)" in result.output
