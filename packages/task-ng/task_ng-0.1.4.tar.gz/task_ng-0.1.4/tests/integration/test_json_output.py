"""Integration tests for JSON output mode."""

import json

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.cli.output import set_json_mode

runner = CliRunner()


@pytest.fixture(autouse=True)
def temp_db(isolate_test_data):
    """Use temporary database for each test."""
    return isolate_test_data / "task.db"


@pytest.fixture(autouse=True)
def reset_json_mode():
    """Reset JSON mode after each test."""
    yield
    set_json_mode(False)


class TestJsonOutput:
    """Tests for JSON output mode."""

    def test_list_json_empty(self):
        """Should return empty array when no tasks."""
        result = runner.invoke(app, ["--json", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert data == []

    def test_list_json_with_tasks(self):
        """Should return tasks as JSON array."""
        # Add a task first
        runner.invoke(app, ["add", "Test task", "--project", "Work"])

        result = runner.invoke(app, ["--json", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, list)
        assert len(data) == 1
        assert data[0]["description"] == "Test task"
        assert data[0]["project"] == "Work"

    def test_list_json_multiple_tasks(self):
        """Should return multiple tasks as JSON array."""
        runner.invoke(app, ["add", "Task 1"])
        runner.invoke(app, ["add", "Task 2"])
        runner.invoke(app, ["add", "Task 3"])

        result = runner.invoke(app, ["--json", "list"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 3

    def test_show_json(self):
        """Should return task as JSON object."""
        runner.invoke(app, ["add", "Test task", "--project", "Work", "--priority", "H"])

        result = runner.invoke(app, ["--json", "show", "1"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert isinstance(data, dict)
        assert data["id"] == 1
        assert data["description"] == "Test task"
        assert data["project"] == "Work"
        assert data["priority"] == "H"

    def test_json_has_all_fields(self):
        """Should include all task fields in JSON."""
        runner.invoke(app, ["add", "Full task", "--project", "Test", "--priority", "M"])

        result = runner.invoke(app, ["--json", "show", "1"])

        data = json.loads(result.output)
        # Check required fields
        assert "id" in data
        assert "uuid" in data
        assert "description" in data
        assert "status" in data
        assert "entry" in data
        assert "modified" in data

    def test_json_dates_serialized(self):
        """Should serialize dates correctly."""
        runner.invoke(app, ["add", "Test task"])

        result = runner.invoke(app, ["--json", "show", "1"])

        data = json.loads(result.output)
        # Dates should be ISO format strings
        assert isinstance(data["entry"], str)
        assert isinstance(data["modified"], str)

    def test_list_json_with_filters(self):
        """Should filter tasks in JSON mode."""
        runner.invoke(app, ["add", "Work task", "--project", "Work"])
        runner.invoke(app, ["add", "Home task", "--project", "Home"])

        result = runner.invoke(app, ["--json", "list", "project:Work"])

        assert result.exit_code == 0
        data = json.loads(result.output)
        assert len(data) == 1
        assert data[0]["project"] == "Work"

    def test_json_valid_always(self):
        """Should always return valid JSON."""
        # Empty list
        result = runner.invoke(app, ["--json", "list"])
        json.loads(result.output)  # Should not raise

        # With tasks
        runner.invoke(app, ["add", "Test"])
        result = runner.invoke(app, ["--json", "list"])
        json.loads(result.output)  # Should not raise

        result = runner.invoke(app, ["--json", "show", "1"])
        json.loads(result.output)  # Should not raise
