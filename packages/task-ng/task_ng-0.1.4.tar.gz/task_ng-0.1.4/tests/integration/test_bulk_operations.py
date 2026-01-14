"""Integration tests for bulk operations."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    return CliRunner()


class TestBulkDone:
    """Tests for bulk done command."""

    def test_done_by_tag_filter(self, runner, temp_db):
        """Complete tasks by tag filter."""
        # Create tasks with tags
        runner.invoke(app, ["add", "Task one +work"])
        runner.invoke(app, ["add", "Task two +work"])
        runner.invoke(app, ["add", "Task three +personal"])

        # Complete all work tasks
        result = runner.invoke(app, ["done", "+work", "--force"])
        assert result.exit_code == 0
        assert "Completed 2 task(s)" in result.output

        # Verify only personal task remains pending
        result = runner.invoke(app, ["list"])
        assert "Task three" in result.output
        assert "Task one" not in result.output
        assert "Task two" not in result.output

    def test_done_by_project_filter(self, runner, temp_db):
        """Complete tasks by project filter."""
        runner.invoke(app, ["add", "Task one", "-p", "Work"])
        runner.invoke(app, ["add", "Task two", "-p", "Work"])
        runner.invoke(app, ["add", "Task three", "-p", "Personal"])

        result = runner.invoke(app, ["done", "project:Work", "--force"])
        assert result.exit_code == 0
        assert "Completed 2 task(s)" in result.output

    def test_done_dry_run(self, runner, temp_db):
        """Dry run shows tasks but doesn't complete them."""
        runner.invoke(app, ["add", "Task one +work"])
        runner.invoke(app, ["add", "Task two +work"])

        result = runner.invoke(app, ["done", "+work", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output

        # Tasks should still be pending
        result = runner.invoke(app, ["list"])
        assert "Task one" in result.output
        assert "Task two" in result.output

    def test_done_no_matching_tasks(self, runner, temp_db):
        """Complete with no matching tasks shows message."""
        runner.invoke(app, ["add", "Task one +work"])

        result = runner.invoke(app, ["done", "+nonexistent", "--force"])
        assert result.exit_code == 0
        assert "No matching tasks" in result.output


class TestBulkDelete:
    """Tests for bulk delete command."""

    def test_delete_by_tag_filter(self, runner, temp_db):
        """Delete tasks by tag filter."""
        runner.invoke(app, ["add", "Task one +work"])
        runner.invoke(app, ["add", "Task two +work"])
        runner.invoke(app, ["add", "Task three +personal"])

        result = runner.invoke(app, ["delete", "+work", "--force"])
        assert result.exit_code == 0
        assert "Deleted 2 task(s)" in result.output

        # Verify only personal task remains
        result = runner.invoke(app, ["list"])
        assert "Task three" in result.output
        assert "Task one" not in result.output

    def test_delete_by_project_filter(self, runner, temp_db):
        """Delete tasks by project filter."""
        runner.invoke(app, ["add", "Task one", "-p", "Work"])
        runner.invoke(app, ["add", "Task two", "-p", "Personal"])

        result = runner.invoke(app, ["delete", "project:Work", "--force"])
        assert result.exit_code == 0
        assert "Deleted 1 task(s)" in result.output

    def test_delete_dry_run(self, runner, temp_db):
        """Dry run shows tasks but doesn't delete them."""
        runner.invoke(app, ["add", "Task one +work"])
        runner.invoke(app, ["add", "Task two +work"])

        result = runner.invoke(app, ["delete", "+work", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output

        # Tasks should still exist
        result = runner.invoke(app, ["list"])
        assert "Task one" in result.output
        assert "Task two" in result.output


class TestBulkModify:
    """Tests for bulk modify command."""

    def test_modify_by_tag_filter(self, runner, temp_db):
        """Modify tasks by tag filter."""
        runner.invoke(app, ["add", "Task one +work"])
        runner.invoke(app, ["add", "Task two +work"])
        runner.invoke(app, ["add", "Task three +personal"])

        # Add priority to all work tasks
        result = runner.invoke(app, ["modify", "+work", "-P", "H", "--force"])
        assert result.exit_code == 0
        assert "Modified 2 task(s)" in result.output

        # Verify priority was set
        result = runner.invoke(app, ["show", "1"])
        assert "H" in result.output

    def test_modify_add_tag_to_filtered(self, runner, temp_db):
        """Add tag to filtered tasks."""
        runner.invoke(app, ["add", "Task one", "-p", "Work"])
        runner.invoke(app, ["add", "Task two", "-p", "Work"])

        result = runner.invoke(
            app, ["modify", "project:Work", "-t", "urgent", "--force"]
        )
        assert result.exit_code == 0
        assert "Modified 2 task(s)" in result.output

    def test_modify_project_for_tagged(self, runner, temp_db):
        """Change project for tagged tasks."""
        runner.invoke(app, ["add", "Task one +migrate"])
        runner.invoke(app, ["add", "Task two +migrate"])

        result = runner.invoke(
            app, ["modify", "+migrate", "-p", "NewProject", "--force"]
        )
        assert result.exit_code == 0
        assert "Modified 2 task(s)" in result.output

    def test_modify_dry_run(self, runner, temp_db):
        """Dry run shows tasks but doesn't modify them."""
        runner.invoke(app, ["add", "Task one +work"])

        result = runner.invoke(app, ["modify", "+work", "-P", "H", "--dry-run"])
        assert result.exit_code == 0
        assert "Dry run" in result.output

        # Task should not have priority
        result = runner.invoke(app, ["show", "1"])
        # Priority field won't show if not set

    def test_modify_no_matching_tasks(self, runner, temp_db):
        """Modify with no matching tasks shows message."""
        runner.invoke(app, ["add", "Task one +work"])

        result = runner.invoke(app, ["modify", "+nonexistent", "-P", "H", "--force"])
        assert result.exit_code == 0
        assert "No matching tasks" in result.output


class TestBulkOperationsWithIDs:
    """Tests for bulk operations with multiple IDs."""

    def test_done_multiple_ids(self, runner, temp_db):
        """Complete multiple tasks by ID."""
        runner.invoke(app, ["add", "Task one"])
        runner.invoke(app, ["add", "Task two"])
        runner.invoke(app, ["add", "Task three"])

        result = runner.invoke(app, ["done", "1", "2"])
        assert result.exit_code == 0
        assert "Completed 2 task(s)" in result.output

    def test_delete_multiple_ids(self, runner, temp_db):
        """Delete multiple tasks by ID."""
        runner.invoke(app, ["add", "Task one"])
        runner.invoke(app, ["add", "Task two"])
        runner.invoke(app, ["add", "Task three"])

        result = runner.invoke(app, ["delete", "1", "2", "--force"])
        assert result.exit_code == 0
        assert "Deleted 2 task(s)" in result.output

    def test_modify_multiple_ids(self, runner, temp_db):
        """Modify multiple tasks by ID."""
        runner.invoke(app, ["add", "Task one"])
        runner.invoke(app, ["add", "Task two"])

        result = runner.invoke(app, ["modify", "1", "2", "-P", "H"])
        assert result.exit_code == 0

    def test_done_id_range(self, runner, temp_db):
        """Complete tasks by ID range."""
        runner.invoke(app, ["add", "Task one"])
        runner.invoke(app, ["add", "Task two"])
        runner.invoke(app, ["add", "Task three"])

        result = runner.invoke(app, ["done", "1-3"])
        assert result.exit_code == 0
        assert "Completed 3 task(s)" in result.output

    def test_dry_run_only_with_filters(self, runner, temp_db):
        """Dry run option only works with filters, not IDs."""
        runner.invoke(app, ["add", "Task one"])

        result = runner.invoke(app, ["done", "1", "--dry-run"])
        assert result.exit_code == 1
        assert "--dry-run only works with filter" in result.output
