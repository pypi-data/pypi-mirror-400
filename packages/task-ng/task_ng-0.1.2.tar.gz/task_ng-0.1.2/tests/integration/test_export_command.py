"""Integration tests for export command."""

import json

from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.core.models import Priority, Task, TaskStatus

runner = CliRunner()


class TestExportCommand:
    """Test task-ng export command."""

    def test_export_no_database(self, temp_db_path):
        """Should show user-friendly message when no database."""
        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        assert "No tasks to export" in result.stdout

    def test_export_empty_database(self, temp_db):
        """Should output empty array for empty database."""
        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert data == []

    def test_export_to_stdout(self, task_repo):
        """Should export tasks to stdout by default."""
        task1 = Task(description="Task 1", status=TaskStatus.PENDING)
        task2 = Task(description="Task 2", status=TaskStatus.PENDING)
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2
        descriptions = {t["description"] for t in data}
        assert descriptions == {"Task 1", "Task 2"}

    def test_export_to_file(self, task_repo, tmp_path):
        """Should export tasks to file when specified."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        output_file = tmp_path / "export.json"
        result = runner.invoke(app, ["export", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Exported 1 tasks" in result.stdout

        data = json.loads(output_file.read_text())
        assert len(data) == 1
        assert data[0]["description"] == "Test task"

    def test_export_excludes_completed_by_default(self, task_repo):
        """Should exclude completed tasks by default."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Pending"

    def test_export_excludes_deleted_by_default(self, task_repo):
        """Should exclude deleted tasks by default."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Pending"

    def test_export_with_all_flag(self, task_repo):
        """Should include all tasks with --all flag."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task3 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)
        task_repo.add(task3)

        result = runner.invoke(app, ["export", "--all"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 3
        descriptions = {t["description"] for t in data}
        assert descriptions == {"Pending", "Completed", "Deleted"}

    def test_export_with_all_flag_short(self, task_repo):
        """Should support -a short flag for --all."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export", "-a"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 2

    def test_export_with_filter(self, task_repo):
        """Should export only filtered tasks."""
        task1 = Task(description="Work task", status=TaskStatus.PENDING, project="Work")
        task2 = Task(description="Home task", status=TaskStatus.PENDING, project="Home")
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export", "--filter", "project:Work"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Work task"

    def test_export_with_filter_short(self, task_repo):
        """Should support -f short flag for --filter."""
        task1 = Task(
            description="Urgent task", status=TaskStatus.PENDING, tags=["urgent"]
        )
        task2 = Task(
            description="Normal task", status=TaskStatus.PENDING, tags=["normal"]
        )
        task_repo.add(task1)
        task_repo.add(task2)

        result = runner.invoke(app, ["export", "-f", "+urgent"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Urgent task"

    def test_export_with_multiple_filters(self, task_repo):
        """Should handle multiple filter arguments."""
        task1 = Task(
            description="Work urgent",
            status=TaskStatus.PENDING,
            project="Work",
            priority=Priority.HIGH,
        )
        task2 = Task(
            description="Work normal",
            status=TaskStatus.PENDING,
            project="Work",
            priority=Priority.MEDIUM,
        )
        task3 = Task(
            description="Home urgent",
            status=TaskStatus.PENDING,
            project="Home",
            priority=Priority.HIGH,
        )
        task_repo.add(task1)
        task_repo.add(task2)
        task_repo.add(task3)

        result = runner.invoke(
            app, ["export", "--filter", "project:Work", "--filter", "priority:H"]
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Work urgent"

    def test_export_preserves_task_data(self, task_repo):
        """Should preserve all task fields in export."""
        task = Task(
            description="Full task",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            project="Work.Backend",
            tags=["urgent", "bug"],
            uda={"estimate": "2h", "sprint": "23"},
        )
        task_repo.add(task)

        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1

        exported = data[0]
        assert exported["description"] == "Full task"
        assert exported["status"] == "pending"
        assert exported["priority"] == "H"
        assert exported["project"] == "Work.Backend"
        assert set(exported["tags"]) == {"urgent", "bug"}
        assert exported["uda"]["estimate"] == "2h"
        assert exported["uda"]["sprint"] == "23"

    def test_export_backup_without_output_fails(self, task_repo):
        """Should require output file for backup mode."""
        task = Task(description="Test", status=TaskStatus.PENDING)
        task_repo.add(task)

        result = runner.invoke(app, ["export", "--backup"])

        assert result.exit_code == 1
        assert "backup requires output file" in result.stdout.lower()

    def test_export_backup_creates_file(self, task_repo, tmp_path):
        """Should create backup file with metadata."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["export", str(output_file), "--backup"])

        assert result.exit_code == 0
        assert output_file.exists()
        assert "Backup created" in result.stdout

        data = json.loads(output_file.read_text())
        assert data["version"] == "1.0"
        assert "exported" in data
        assert data["task_count"] == 2
        assert len(data["tasks"]) == 2

    def test_export_backup_short_flag(self, task_repo, tmp_path):
        """Should support -b short flag for --backup."""
        task = Task(description="Test", status=TaskStatus.PENDING)
        task_repo.add(task)

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["export", str(output_file), "-b"])

        assert result.exit_code == 0
        assert output_file.exists()

        data = json.loads(output_file.read_text())
        assert data["version"] == "1.0"
        assert data["task_count"] == 1

    def test_export_backup_includes_all_statuses(self, task_repo, tmp_path):
        """Should include all task statuses in backup."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task3 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)
        task_repo.add(task3)

        output_file = tmp_path / "backup.json"
        result = runner.invoke(app, ["export", str(output_file), "--backup"])

        assert result.exit_code == 0

        data = json.loads(output_file.read_text())
        assert data["task_count"] == 3
        descriptions = {t["description"] for t in data["tasks"]}
        assert descriptions == {"Pending", "Completed", "Deleted"}

    def test_export_json_format(self, task_repo):
        """Should output valid JSON format."""
        task = Task(
            description='Task with "quotes" and special chars: \n\t',
            status=TaskStatus.PENDING,
        )
        task_repo.add(task)

        result = runner.invoke(app, ["export"])

        assert result.exit_code == 0
        # Should parse without error
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert "quotes" in data[0]["description"]

    def test_export_multiple_tasks_to_file(self, task_repo, tmp_path):
        """Should export multiple tasks to file."""
        for i in range(5):
            task = Task(description=f"Task {i}", status=TaskStatus.PENDING)
            task_repo.add(task)

        output_file = tmp_path / "export.json"
        result = runner.invoke(app, ["export", str(output_file)])

        assert result.exit_code == 0
        assert "Exported 5 tasks" in result.stdout

        data = json.loads(output_file.read_text())
        assert len(data) == 5

    def test_export_with_complex_filter(self, task_repo):
        """Should handle complex filter combinations."""
        task1 = Task(
            description="Match",
            status=TaskStatus.PENDING,
            project="Work",
            tags=["urgent"],
            priority=Priority.HIGH,
        )
        task2 = Task(
            description="No match - wrong project",
            status=TaskStatus.PENDING,
            project="Home",
            tags=["urgent"],
            priority=Priority.HIGH,
        )
        task3 = Task(
            description="No match - no tag",
            status=TaskStatus.PENDING,
            project="Work",
            priority=Priority.HIGH,
        )
        task_repo.add(task1)
        task_repo.add(task2)
        task_repo.add(task3)

        result = runner.invoke(
            app,
            ["export", "--filter", "project:Work", "--filter", "+urgent"],
        )

        assert result.exit_code == 0
        data = json.loads(result.stdout)
        assert len(data) == 1
        assert data[0]["description"] == "Match"
