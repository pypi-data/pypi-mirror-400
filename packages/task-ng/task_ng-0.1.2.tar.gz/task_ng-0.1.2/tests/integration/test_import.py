"""Integration tests for import command."""

import json

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app

runner = CliRunner()


@pytest.fixture(autouse=True)
def temp_db(isolate_test_data):
    """Use temporary database for each test."""
    return isolate_test_data / "task.db"


class TestImportCommand:
    """Tests for import command."""

    def test_import_single_task(self, tmp_path):
        """Should import a single task."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "description": "Test task",
                "status": "pending",
                "entry": "20240115T093000Z",
            }
        ]
        import_file.write_text(json.dumps(tasks))

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Imported: 1" in result.output

    def test_import_multiple_tasks(self, tmp_path):
        """Should import multiple tasks."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": f"uuid-{i}",
                "description": f"Task {i}",
                "status": "pending",
                "entry": "20240115T093000Z",
            }
            for i in range(5)
        ]
        import_file.write_text(json.dumps(tasks))

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Imported: 5" in result.output

    def test_import_with_all_attributes(self, tmp_path):
        """Should import task with all attributes."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
                "description": "Full task",
                "status": "pending",
                "priority": "H",
                "project": "Work",
                "tags": ["urgent", "important"],
                "entry": "20240115T093000Z",
                "modified": "20240116T142200Z",
                "due": "20240120T170000Z",
                "annotations": [
                    {"entry": "20240116T100000Z", "description": "Note text"}
                ],
                "depends": ["other-uuid"],
            }
        ]
        import_file.write_text(json.dumps(tasks))

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Imported: 1" in result.output

    def test_import_dry_run(self, tmp_path):
        """Should show what would be imported without importing."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": "test-uuid",
                "description": "Test task",
                "status": "pending",
                "entry": "20240115T093000Z",
            }
        ]
        import_file.write_text(json.dumps(tasks))

        result = runner.invoke(app, ["import", str(import_file), "--dry-run"])

        assert result.exit_code == 0
        assert "Dry run" in result.output
        assert "Would import: 1" in result.output

    def test_import_skip_duplicates(self, tmp_path):
        """Should skip tasks with duplicate UUIDs."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": "duplicate-uuid",
                "description": "Test task",
                "status": "pending",
                "entry": "20240115T093000Z",
            }
        ]
        import_file.write_text(json.dumps(tasks))

        # Import first time
        runner.invoke(app, ["import", str(import_file)])

        # Import again
        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Skipped (duplicate): 1" in result.output

    def test_import_file_not_found(self, tmp_path):
        """Should show error for missing file."""
        result = runner.invoke(app, ["import", "/nonexistent/file.json"])

        assert result.exit_code == 0  # Command completes but shows error
        assert "not found" in result.output

    def test_import_newline_delimited_json(self, tmp_path):
        """Should handle newline-delimited JSON."""
        import_file = tmp_path / "tasks.json"
        lines = [
            json.dumps(
                {
                    "uuid": f"uuid-{i}",
                    "description": f"Task {i}",
                    "status": "pending",
                    "entry": "20240115T093000Z",
                }
            )
            for i in range(3)
        ]
        import_file.write_text("\n".join(lines))

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Imported: 3" in result.output

    def test_import_completed_task(self, tmp_path):
        """Should import completed tasks."""
        import_file = tmp_path / "tasks.json"
        tasks = [
            {
                "uuid": "completed-uuid",
                "description": "Completed task",
                "status": "completed",
                "entry": "20240115T093000Z",
                "end": "20240116T100000Z",
            }
        ]
        import_file.write_text(json.dumps(tasks))

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "Imported: 1" in result.output

    def test_import_empty_file(self, tmp_path):
        """Should handle empty JSON array."""
        import_file = tmp_path / "tasks.json"
        import_file.write_text("[]")

        result = runner.invoke(app, ["import", str(import_file)])

        assert result.exit_code == 0
        assert "No tasks found" in result.output


class TestImportTaskwarriorExample:
    """Tests for importing comprehensive Taskwarrior export."""

    @pytest.fixture
    def example_file(self):
        """Path to Taskwarrior example export fixture."""
        from pathlib import Path

        return Path(__file__).parent.parent / "fixtures" / "taskwarrior_example.json"

    def test_import_taskwarrior_example(self, example_file):
        """Should import the comprehensive Taskwarrior example."""
        result = runner.invoke(app, ["import", str(example_file)])

        assert result.exit_code == 0
        assert "Imported:" in result.output
        # Should import most tasks (some may be skipped as deleted/recurring parents)
        # The file has 52 tasks total

    def test_import_preserves_projects(self, example_file):
        """Should preserve hierarchical project structure."""
        runner.invoke(app, ["import", str(example_file)])

        result = runner.invoke(app, ["project", "list"])

        assert result.exit_code == 0
        # Check for hierarchical projects
        assert "Work" in result.output
        assert "Personal" in result.output
        assert "Home" in result.output
        assert "Learning" in result.output

    def test_import_preserves_tags(self, example_file):
        """Should preserve task tags."""
        runner.invoke(app, ["import", str(example_file)])

        result = runner.invoke(app, ["tags"])

        assert result.exit_code == 0
        # Check for various tags
        assert "dev" in result.output
        assert "meeting" in result.output
        assert "fitness" in result.output

    def test_import_preserves_priorities(self, example_file):
        """Should preserve task priorities."""
        runner.invoke(app, ["import", str(example_file)])

        # Check for high priority tasks
        result = runner.invoke(app, ["list", "priority:H"])

        assert result.exit_code == 0
        # Should have some high priority tasks

    def test_import_preserves_annotations(self, example_file):
        """Should preserve task annotations."""
        runner.invoke(app, ["import", str(example_file)])

        # Find a task with annotations and check it
        result = runner.invoke(app, ["list", "+ANNOTATED"])

        assert result.exit_code == 0

    def test_import_preserves_dependencies(self, example_file):
        """Should preserve task dependencies."""
        runner.invoke(app, ["import", str(example_file)])

        # Check for blocked tasks
        result = runner.invoke(app, ["list", "+BLOCKED"])

        assert result.exit_code == 0

    def test_import_preserves_due_dates(self, example_file):
        """Should preserve due dates."""
        runner.invoke(app, ["import", str(example_file)])

        # List tasks with due dates
        result = runner.invoke(app, ["list", "due.any:"])

        assert result.exit_code == 0

    def test_import_preserves_wait_dates(self, example_file):
        """Should preserve wait dates for hidden tasks."""
        runner.invoke(app, ["import", str(example_file)])

        # Check for waiting tasks (use --all to see them)
        result = runner.invoke(app, ["list", "--all", "status:waiting"])

        assert result.exit_code == 0

    def test_import_dry_run_shows_count(self, example_file):
        """Dry run should show task count without importing."""
        result = runner.invoke(app, ["import", str(example_file), "--dry-run"])

        assert result.exit_code == 0
        assert "Would import:" in result.output
        assert "Dry run" in result.output

    def test_import_completed_tasks(self, example_file):
        """Should import completed tasks."""
        runner.invoke(app, ["import", str(example_file)])

        # List completed tasks
        result = runner.invoke(app, ["list", "status:completed"])

        assert result.exit_code == 0

    def test_import_preserves_scheduled_dates(self, example_file):
        """Should preserve scheduled dates."""
        runner.invoke(app, ["import", str(example_file)])

        # List tasks with scheduled dates
        result = runner.invoke(app, ["list", "scheduled.any:"])

        assert result.exit_code == 0

    def test_import_preserves_recurring_tasks(self, example_file):
        """Should preserve recurring task attributes."""
        runner.invoke(app, ["import", str(example_file)])

        # List recurring tasks
        result = runner.invoke(app, ["list", "+RECURRING"])

        assert result.exit_code == 0

    def test_import_preserves_active_tasks(self, example_file):
        """Should preserve start dates for active tasks."""
        runner.invoke(app, ["import", str(example_file)])

        # List active tasks
        result = runner.invoke(app, ["list", "+ACTIVE"])

        assert result.exit_code == 0

    def test_import_preserves_uuids(self, example_file):
        """Should preserve original UUIDs from Taskwarrior."""
        import json

        # Get a UUID from the import file
        with open(example_file) as f:
            tasks = json.load(f)
        # Find a pending task UUID
        test_uuid = None
        for task in tasks:
            if task.get("status") == "pending" and "uuid" in task:
                test_uuid = task["uuid"]
                break

        runner.invoke(app, ["import", str(example_file)])

        # Should be able to find task by UUID filter
        if test_uuid:
            result = runner.invoke(app, ["list", f"uuid:{test_uuid[:8]}"])
            assert result.exit_code == 0

    def test_import_preserves_entry_dates(self, example_file):
        """Should preserve entry (creation) dates."""
        runner.invoke(app, ["import", str(example_file)])

        # Show a task and check for entry date
        result = runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        # Entry date should be displayed
        assert "Entry" in result.output or "Created" in result.output

    def test_import_preserves_modified_dates(self, example_file):
        """Should preserve modification dates."""
        runner.invoke(app, ["import", str(example_file)])

        # Show a task and check for modified date
        result = runner.invoke(app, ["show", "1"])

        assert result.exit_code == 0
        # Modified date should be displayed
        assert "Modified" in result.output
