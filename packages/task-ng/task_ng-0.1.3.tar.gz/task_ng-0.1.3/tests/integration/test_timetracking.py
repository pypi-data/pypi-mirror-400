"""Integration tests for time tracking commands."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository


@pytest.fixture
def runner():
    return CliRunner()


@pytest.fixture
def temp_db(isolate_test_data):
    return isolate_test_data / "task.db"


class TestStartCommand:
    def test_start_task(self, runner, temp_db):
        """Start tracking time for a task."""
        runner.invoke(app, ["add", "Test task"])
        result = runner.invoke(app, ["start", "1"])
        assert result.exit_code == 0
        assert "Started task" in result.output
        assert "1" in result.output

    def test_start_nonexistent_task(self, runner, temp_db):
        """Starting nonexistent task fails."""
        result = runner.invoke(app, ["start", "999"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_start_already_active(self, runner, temp_db):
        """Starting already active task shows message."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["start", "1"])
        assert result.exit_code == 0
        assert "already active" in result.output

    def test_start_when_another_active(self, runner, temp_db):
        """Starting task when another is active shows warning."""
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["start", "2"])
        assert result.exit_code == 1
        assert "already active" in result.output

    def test_start_force(self, runner, temp_db):
        """Force start stops active task first."""
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["start", "2", "--force"])
        assert result.exit_code == 0
        assert "Stopped task" in result.output
        assert "Started task" in result.output

    def test_start_completed_task(self, runner, temp_db):
        """Cannot start a completed task."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["done", "1"])
        result = runner.invoke(app, ["start", "1"])
        assert result.exit_code == 1
        assert "not pending" in result.output


class TestStopCommand:
    def test_stop_task(self, runner, temp_db):
        """Stop tracking time for a task."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["stop", "1"])
        assert result.exit_code == 0
        assert "Stopped task" in result.output
        assert "Elapsed" in result.output

    def test_stop_active_task_no_id(self, runner, temp_db):
        """Stop active task without specifying ID."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0
        assert "Stopped task" in result.output

    def test_stop_no_active_task(self, runner, temp_db):
        """Stop with no active task shows message."""
        runner.invoke(app, ["add", "Test task"])
        result = runner.invoke(app, ["stop"])
        assert result.exit_code == 0
        assert "No active task" in result.output

    def test_stop_inactive_task(self, runner, temp_db):
        """Stop inactive task shows message."""
        runner.invoke(app, ["add", "Test task"])
        result = runner.invoke(app, ["stop", "1"])
        assert result.exit_code == 0
        assert "not active" in result.output

    def test_stop_nonexistent_task(self, runner, temp_db):
        """Stop nonexistent task fails."""
        runner.invoke(app, ["add", "Test task"])  # Create database first
        result = runner.invoke(app, ["stop", "999"])
        assert result.exit_code == 1
        assert "not found" in result.output


class TestActiveCommand:
    def test_active_no_tasks(self, runner, temp_db):
        """Active with no tasks shows message."""
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        assert "No active task" in result.output

    def test_active_no_active_task(self, runner, temp_db):
        """Active with no active task shows message."""
        runner.invoke(app, ["add", "Test task"])
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        assert "No active task" in result.output

    def test_active_shows_task(self, runner, temp_db):
        """Active shows current task."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        assert "1" in result.output
        assert "Test task" in result.output
        assert "Elapsed" in result.output

    def test_active_shows_project(self, runner, temp_db):
        """Active shows project if set."""
        runner.invoke(app, ["add", "Test task", "-p", "work"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        assert "work" in result.output


class TestShowWithTimeTracking:
    def test_show_active_task(self, runner, temp_db):
        """Show displays elapsed time for active task."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["show", "1"])
        assert result.exit_code == 0
        assert "Started" in result.output
        assert "Elapsed" in result.output


class TestVirtualTagActive:
    def test_filter_active_tasks(self, runner, temp_db):
        """Filter tasks by +ACTIVE virtual tag."""
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["start", "1"])
        result = runner.invoke(app, ["list", "+ACTIVE"])
        assert result.exit_code == 0
        assert "Task 1" in result.output
        assert "Task 2" not in result.output


class TestActiveFilterSupport:
    """Test filter expression support in active command."""

    def test_active_with_project_filter(self, runner, temp_db):
        """Active command with project filter."""
        runner.invoke(app, ["add", "Task 1", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2", "-p", "Home"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "project:Work"])
        assert result.exit_code == 0
        # Should show Work task
        assert "Task 1" in result.output
        assert "Work" in result.output

    def test_active_with_priority_filter(self, runner, temp_db):
        """Active command with priority filter."""
        runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2", "--priority", "L"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "priority:H"])
        assert result.exit_code == 0
        # Should show high priority task
        assert "Task 1" in result.output

    def test_active_with_priority_filter_no_match(self, runner, temp_db):
        """Active command with priority filter that doesn't match."""
        runner.invoke(app, ["add", "Task 1", "--priority", "H"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "priority:L"])
        assert result.exit_code == 0
        # Should not show any tasks
        assert "No active task" in result.output

    def test_active_with_tag_filter(self, runner, temp_db):
        """Active command with tag filter."""
        runner.invoke(app, ["add", "Task 1 +urgent"])
        runner.invoke(app, ["add", "Task 2 +blocked"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "+urgent"])
        assert result.exit_code == 0
        # Should show urgent task
        assert "Task 1" in result.output

    def test_active_with_multiple_filters(self, runner, temp_db):
        """Active command with multiple filters."""
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +urgent", "-p", "Home", "--priority", "L"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "project:Work", "priority:H"])
        assert result.exit_code == 0
        # Should show only Work + high priority task
        assert "Task 1" in result.output

    def test_active_respects_context(self, runner, temp_db):
        """Active command respects active context."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2 +blocked", "-p", "Home"])
        runner.invoke(app, ["start", "1"])

        # Create and activate a context for Work project
        runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Active should only show Work project
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        # Should show Work task
        assert "Task 1" in result.output
        assert "Work" in result.output

        # Clean up context
        runner.invoke(app, ["context", "none"])

    def test_active_context_no_match(self, runner, temp_db):
        """Active command with context that doesn't match active task."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work"])
        runner.invoke(app, ["add", "Task 2 +blocked", "-p", "Home"])
        runner.invoke(app, ["start", "2"])  # Start Home task

        # Create and activate a context for Work project
        runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Active should show nothing because active task is Home, not Work
        result = runner.invoke(app, ["active"])
        assert result.exit_code == 0
        assert "No active task" in result.output

        # Clean up context
        runner.invoke(app, ["context", "none"])

    def test_active_filter_with_context(self, runner, temp_db):
        """Active command filter arguments work with context."""
        # Set up tasks
        runner.invoke(app, ["add", "Task 1 +urgent", "-p", "Work", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +urgent", "-p", "Work", "--priority", "L"])
        runner.invoke(app, ["start", "1"])

        # Set context to Work project
        runner.invoke(app, ["context", "set", "work", "project:Work"])

        # Add additional filter for high priority
        result = runner.invoke(app, ["active", "priority:H"])
        assert result.exit_code == 0
        # Should only show Work AND high priority
        assert "Task 1" in result.output

        # Clean up
        runner.invoke(app, ["context", "none"])

    def test_active_with_no_matches(self, runner, temp_db):
        """Active command with filter that matches nothing."""
        runner.invoke(app, ["add", "Task 1 +work"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["active", "+nonexistent"])
        assert result.exit_code == 0
        # No matching tasks
        assert "No active task" in result.output

    def test_active_json_with_filter(self, runner, temp_db):
        """Active JSON output works with filters."""
        import json

        runner.invoke(app, ["add", "Task 1 +urgent", "--priority", "H"])
        runner.invoke(app, ["add", "Task 2 +blocked", "--priority", "L"])
        runner.invoke(app, ["start", "1"])

        result = runner.invoke(app, ["--json", "active", "priority:H"])
        assert result.exit_code == 0
        data = json.loads(result.output)
        # Should show only high priority task
        assert len(data) == 1
        assert data[0]["priority"] == "H"


class TestTimeTrackingPersistence:
    def test_start_persists(self, runner, temp_db):
        """Start time is persisted to database."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])

        db = Database()
        repo = TaskRepository(db)
        task = repo.get_by_id(1)
        assert task.start is not None

    def test_stop_clears_start(self, runner, temp_db):
        """Stop clears start time in database."""
        runner.invoke(app, ["add", "Test task"])
        runner.invoke(app, ["start", "1"])
        runner.invoke(app, ["stop", "1"])

        db = Database()
        repo = TaskRepository(db)
        task = repo.get_by_id(1)
        assert task.start is None
