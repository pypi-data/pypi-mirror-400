"""Unit tests for export functionality."""

import json
from datetime import datetime, timedelta
from uuid import uuid4

from taskng.cli.commands.export import export_backup, export_tasks, task_to_dict
from taskng.core.models import Priority, Task, TaskStatus


class TestTaskToDict:
    """Test task_to_dict() conversion function."""

    def test_minimal_task(self):
        """Should convert task with only required fields."""
        task = Task(
            uuid=str(uuid4()),
            description="Test task",
            status=TaskStatus.PENDING,
            entry=datetime(2025, 1, 15, 10, 0, 0),
        )

        result = task_to_dict(task)

        assert result["uuid"] == task.uuid
        assert result["description"] == "Test task"
        assert result["status"] == "pending"
        assert result["entry"] == "2025-01-15T10:00:00"
        assert isinstance(result["modified"], str)
        assert "id" not in result
        assert "priority" not in result
        assert "project" not in result

    def test_task_with_id(self):
        """Should include id when present."""
        task = Task(
            id=42,
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
        )

        result = task_to_dict(task)

        assert result["id"] == 42

    def test_task_with_priority(self):
        """Should include priority when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
        )

        result = task_to_dict(task)

        assert result["priority"] == "H"

    def test_task_with_project(self):
        """Should include project when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            project="Work",
        )

        result = task_to_dict(task)

        assert result["project"] == "Work"

    def test_task_with_dates(self):
        """Should convert all date fields to ISO format."""
        now = datetime(2025, 1, 15, 10, 0, 0)
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.COMPLETED,
            entry=now,
            modified=now + timedelta(hours=1),
            due=now + timedelta(days=1),
            scheduled=now + timedelta(hours=2),
            wait=now + timedelta(days=2),
            until=now + timedelta(days=3),
            start=now + timedelta(minutes=30),
            end=now + timedelta(hours=2),
        )

        result = task_to_dict(task)

        assert result["entry"] == "2025-01-15T10:00:00"
        assert result["modified"] == "2025-01-15T11:00:00"
        assert result["due"] == "2025-01-16T10:00:00"
        assert result["scheduled"] == "2025-01-15T12:00:00"
        assert result["wait"] == "2025-01-17T10:00:00"
        assert result["until"] == "2025-01-18T10:00:00"
        assert result["start"] == "2025-01-15T10:30:00"
        assert result["end"] == "2025-01-15T12:00:00"

    def test_task_with_recurrence(self):
        """Should include recur field when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            recur="daily",
        )

        result = task_to_dict(task)

        assert result["recur"] == "daily"

    def test_task_with_parent(self):
        """Should include parent UUID when present."""
        parent_uuid = str(uuid4())
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            parent_uuid=parent_uuid,
        )

        result = task_to_dict(task)

        assert result["parent"] == parent_uuid

    def test_task_with_tags(self):
        """Should include tags list when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            tags=["urgent", "work"],
        )

        result = task_to_dict(task)

        assert result["tags"] == ["urgent", "work"]

    def test_task_with_dependencies(self):
        """Should include depends list when present."""
        dep_uuid = str(uuid4())
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            depends=[dep_uuid],
        )

        result = task_to_dict(task)

        assert result["depends"] == [dep_uuid]

    def test_task_with_annotations(self):
        """Should include annotations when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            annotations=[
                {"entry": "2025-01-15T10:00:00", "description": "Note 1"},
                {"entry": "2025-01-15T11:00:00", "description": "Note 2"},
            ],
        )

        result = task_to_dict(task)

        assert len(result["annotations"]) == 2
        assert result["annotations"][0]["entry"] == "2025-01-15T10:00:00"
        assert result["annotations"][0]["description"] == "Note 1"
        assert result["annotations"][1]["entry"] == "2025-01-15T11:00:00"
        assert result["annotations"][1]["description"] == "Note 2"

    def test_task_with_uda(self):
        """Should include UDA fields when present."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            uda={"estimate": "2h", "sprint": "23"},
        )

        result = task_to_dict(task)

        assert result["uda"] == {"estimate": "2h", "sprint": "23"}

    def test_task_with_urgency(self):
        """Should include urgency rounded to 2 decimals."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.PENDING,
            urgency=12.3456789,
        )

        result = task_to_dict(task)

        assert result["urgency"] == 12.35

    def test_completed_task(self):
        """Should handle completed status."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.COMPLETED,
            entry=datetime(2025, 1, 15, 10, 0, 0),
            end=datetime(2025, 1, 15, 11, 0, 0),
        )

        result = task_to_dict(task)

        assert result["status"] == "completed"
        assert result["end"] == "2025-01-15T11:00:00"

    def test_deleted_task(self):
        """Should handle deleted status."""
        task = Task(
            uuid=str(uuid4()),
            description="Test",
            status=TaskStatus.DELETED,
        )

        result = task_to_dict(task)

        assert result["status"] == "deleted"


class TestExportTasks:
    """Test export_tasks() function."""

    def test_export_no_database(self, tmp_path, temp_db_path, capsys):
        """Should output empty array when no database exists."""
        # Don't create database - pass output file to get JSON output
        output_file = tmp_path / "export.json"
        export_tasks(output=output_file)

        # Should print to stdout (not create file) when db doesn't exist
        captured = capsys.readouterr()
        assert captured.out.strip() == "[]"

    def test_export_no_tasks(self, temp_db, tmp_path, capsys):
        """Should output empty array when no tasks exist."""
        export_tasks()

        captured = capsys.readouterr()
        assert captured.out == "[]\n"

    def test_export_to_stdout(self, task_repo, capsys):
        """Should export tasks to stdout as JSON."""
        # Create test tasks
        task1 = Task(description="Task 1", status=TaskStatus.PENDING)
        task2 = Task(description="Task 2", status=TaskStatus.PENDING)
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 2
        assert data[0]["description"] == "Task 1"
        assert data[1]["description"] == "Task 2"

    def test_export_to_file(self, task_repo, tmp_path):
        """Should export tasks to file."""
        # Create test tasks
        task1 = Task(description="Task 1", status=TaskStatus.PENDING)
        task2 = Task(description="Task 2", status=TaskStatus.PENDING)
        task_repo.add(task1)
        task_repo.add(task2)

        output_file = tmp_path / "export.json"
        export_tasks(output=output_file)

        assert output_file.exists()
        data = json.loads(output_file.read_text())
        assert len(data) == 2
        assert data[0]["description"] == "Task 1"

    def test_export_excludes_completed_by_default(self, task_repo, capsys):
        """Should exclude completed tasks by default."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["description"] == "Pending"

    def test_export_includes_completed_when_requested(self, task_repo, capsys):
        """Should include completed tasks when requested."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks(include_completed=True)

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 2
        descriptions = {t["description"] for t in data}
        assert descriptions == {"Pending", "Completed"}

    def test_export_excludes_deleted_by_default(self, task_repo, capsys):
        """Should exclude deleted tasks by default."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["description"] == "Pending"

    def test_export_includes_deleted_when_requested(self, task_repo, capsys):
        """Should include deleted tasks when requested."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks(include_deleted=True)

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 2
        descriptions = {t["description"] for t in data}
        assert descriptions == {"Pending", "Deleted"}

    def test_export_with_filters(self, task_repo, capsys):
        """Should export only filtered tasks."""
        task1 = Task(description="Work task", status=TaskStatus.PENDING, project="Work")
        task2 = Task(description="Home task", status=TaskStatus.PENDING, project="Home")
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks(filter_args=["project:Work"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["description"] == "Work task"

    def test_export_with_tag_filter(self, task_repo, capsys):
        """Should export tasks matching tag filter."""
        task1 = Task(
            description="Urgent task", status=TaskStatus.PENDING, tags=["urgent"]
        )
        task2 = Task(
            description="Normal task", status=TaskStatus.PENDING, tags=["normal"]
        )
        task_repo.add(task1)
        task_repo.add(task2)

        export_tasks(filter_args=["+urgent"])

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        assert data[0]["description"] == "Urgent task"

    def test_export_preserves_all_fields(self, task_repo, capsys):
        """Should preserve all task fields in export."""
        task = Task(
            description="Full task",
            status=TaskStatus.PENDING,
            priority=Priority.HIGH,
            project="Work",
            tags=["urgent", "bug"],
            due=datetime(2025, 1, 20, 10, 0, 0),
            uda={"estimate": "2h"},
        )
        task_repo.add(task)

        export_tasks()

        captured = capsys.readouterr()
        data = json.loads(captured.out)

        assert len(data) == 1
        exported = data[0]
        assert exported["description"] == "Full task"
        assert exported["status"] == "pending"
        assert exported["priority"] == "H"
        assert exported["project"] == "Work"
        assert set(exported["tags"]) == {"urgent", "bug"}
        assert "2025-01-20" in exported["due"]
        assert exported["uda"]["estimate"] == "2h"


class TestExportBackup:
    """Test export_backup() function."""

    def test_backup_no_database(self, temp_db_path, tmp_path, capsys):
        """Should show warning when no database exists."""
        output_file = tmp_path / "backup.json"

        export_backup(output_file)

        captured = capsys.readouterr()
        assert "No database to backup" in captured.out

    def test_backup_creates_file(self, task_repo, tmp_path):
        """Should create backup file."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        output_file = tmp_path / "backup.json"
        export_backup(output_file)

        assert output_file.exists()

    def test_backup_includes_metadata(self, task_repo, tmp_path):
        """Should include version, timestamp, and task count."""
        task = Task(description="Test task", status=TaskStatus.PENDING)
        task_repo.add(task)

        output_file = tmp_path / "backup.json"
        export_backup(output_file)

        data = json.loads(output_file.read_text())

        assert data["version"] == "1.0"
        assert "exported" in data
        assert data["task_count"] == 1
        assert "tasks" in data

    def test_backup_includes_all_tasks(self, task_repo, tmp_path):
        """Should include all tasks regardless of status."""
        task1 = Task(description="Pending", status=TaskStatus.PENDING)
        task2 = Task(description="Completed", status=TaskStatus.COMPLETED)
        task3 = Task(description="Deleted", status=TaskStatus.DELETED)
        task_repo.add(task1)
        task_repo.add(task2)
        task_repo.add(task3)

        output_file = tmp_path / "backup.json"
        export_backup(output_file)

        data = json.loads(output_file.read_text())

        assert data["task_count"] == 3
        assert len(data["tasks"]) == 3
        descriptions = {t["description"] for t in data["tasks"]}
        assert descriptions == {"Pending", "Completed", "Deleted"}

    def test_backup_timestamp_format(self, task_repo, tmp_path):
        """Should use ISO format timestamp."""
        task = Task(description="Test", status=TaskStatus.PENDING)
        task_repo.add(task)

        output_file = tmp_path / "backup.json"
        export_backup(output_file)

        data = json.loads(output_file.read_text())

        # Verify ISO format can be parsed
        timestamp = datetime.fromisoformat(data["exported"])
        assert timestamp is not None
        assert timestamp.year == datetime.now().year

    def test_backup_empty_database(self, temp_db, tmp_path):
        """Should create backup for empty database."""
        output_file = tmp_path / "backup.json"
        export_backup(output_file)

        data = json.loads(output_file.read_text())

        assert data["version"] == "1.0"
        assert data["task_count"] == 0
        assert data["tasks"] == []
