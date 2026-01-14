"""Integration tests for date parsing in CLI commands."""

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app


@pytest.fixture
def runner():
    """Create CLI runner."""
    return CliRunner()


@pytest.fixture
def temp_db(isolate_test_data):
    """Create temporary database."""
    return isolate_test_data / "task.db"


class TestAddWithDates:
    """Tests for add command with date parsing."""

    def test_add_with_tomorrow(self, runner, temp_db):
        """Should add task with 'tomorrow' as due date."""
        result = runner.invoke(app, ["add", "Test task", "--due", "tomorrow"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "Due:" in result.output

    def test_add_with_next_week(self, runner, temp_db):
        """Should add task with 'next week' as due date."""
        result = runner.invoke(app, ["add", "Test task", "--due", "next week"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "Due:" in result.output

    def test_add_with_standard_date(self, runner, temp_db):
        """Should add task with standard date format."""
        result = runner.invoke(app, ["add", "Test task", "--due", "2024-12-31"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "2024-12-31" in result.output

    def test_add_with_relative_days(self, runner, temp_db):
        """Should add task with relative days."""
        result = runner.invoke(app, ["add", "Test task", "--due", "in 3 days"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "Due:" in result.output

    def test_add_with_invalid_date(self, runner, temp_db):
        """Should show error for invalid date."""
        result = runner.invoke(app, ["add", "Test task", "--due", "not a date xyz"])
        assert result.exit_code == 1
        assert "Could not parse date" in result.output

    def test_add_with_time(self, runner, temp_db):
        """Should add task with date and time."""
        result = runner.invoke(app, ["add", "Test task", "--due", "tomorrow at 2pm"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "14:00" in result.output


class TestModifyWithDates:
    """Tests for modify command with date parsing."""

    def test_modify_add_due_date(self, runner, temp_db):
        """Should add due date to existing task."""
        # Create task without due date
        runner.invoke(app, ["add", "Test task"])

        # Modify to add due date
        result = runner.invoke(app, ["modify", "1", "--due", "tomorrow"])
        assert result.exit_code == 0
        assert "Modified task" in result.output
        assert "Due:" in result.output

    def test_modify_change_due_date(self, runner, temp_db):
        """Should change existing due date."""
        # Create task with due date
        runner.invoke(app, ["add", "Test task", "--due", "tomorrow"])

        # Modify due date
        result = runner.invoke(app, ["modify", "1", "--due", "next week"])
        assert result.exit_code == 0
        assert "Modified task" in result.output
        assert "Due:" in result.output

    def test_modify_with_invalid_date(self, runner, temp_db):
        """Should show error for invalid date in modify."""
        # Create task
        runner.invoke(app, ["add", "Test task"])

        # Try invalid date
        result = runner.invoke(app, ["modify", "1", "--due", "invalid date xyz"])
        assert result.exit_code == 1
        assert "Could not parse date" in result.output


class TestShowWithDates:
    """Tests for show command with dates."""

    def test_show_displays_due_date(self, runner, temp_db):
        """Should display due date in show command."""
        # Create task with due date
        runner.invoke(app, ["add", "Test task", "--due", "2024-12-31"])

        # Show task
        result = runner.invoke(app, ["show", "1"])
        assert result.exit_code == 0
        assert "2024-12-31" in result.output


class TestListWithDates:
    """Tests for list command with dates."""

    def test_list_shows_due_date(self, runner, temp_db):
        """Should show due date in list output."""
        # Create task with due date
        runner.invoke(app, ["add", "Test task", "--due", "2024-12-31"])

        # List tasks
        result = runner.invoke(app, ["list"])
        assert result.exit_code == 0
        # Due date should appear in some form
        assert "Test task" in result.output
