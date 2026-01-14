"""Unit tests for sync export functionality."""

import json
from datetime import datetime
from pathlib import Path

from taskng.core.models import Priority, Task, TaskStatus
from taskng.sync.export import (
    task_to_sync_dict,
    write_task_file,
    write_tombstone,
)


def make_task(
    uuid: str = "test-uuid",
    description: str = "Test task",
    status: TaskStatus = TaskStatus.PENDING,
    priority: Priority | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    due: datetime | None = None,
    entry: datetime | None = None,
    modified: datetime | None = None,
    annotations: list[dict[str, str]] | None = None,
    uda: dict[str, str] | None = None,
) -> Task:
    """Create a test task."""
    return Task(
        uuid=uuid,
        description=description,
        status=status,
        priority=priority,
        project=project,
        tags=tags or [],
        due=due,
        entry=entry or datetime.now(),
        modified=modified or datetime.now(),
        annotations=annotations or [],
        uda=uda or {},
    )


class TestTaskToSyncDict:
    """Test task to dictionary conversion."""

    def test_basic_fields(self):
        """Should include all basic fields."""
        task = make_task(
            uuid="abc-123",
            description="Test description",
            status=TaskStatus.PENDING,
        )
        result = task_to_sync_dict(task)

        assert result["uuid"] == "abc-123"
        assert result["description"] == "Test description"
        assert result["status"] == "pending"

    def test_optional_fields(self):
        """Should include optional fields when set."""
        task = make_task(
            priority=Priority.HIGH,
            project="work",
            tags=["urgent", "important"],
        )
        result = task_to_sync_dict(task)

        assert result["priority"] == "H"
        assert result["project"] == "work"
        assert result["tags"] == ["urgent", "important"]

    def test_datetime_fields(self):
        """Should serialize datetime fields as ISO strings."""
        due = datetime(2025, 12, 25, 10, 0, 0)
        entry = datetime(2025, 12, 17, 9, 0, 0)
        modified = datetime(2025, 12, 17, 10, 0, 0)

        task = make_task(
            due=due,
            entry=entry,
            modified=modified,
        )
        result = task_to_sync_dict(task)

        assert result["due"] == due.isoformat()
        assert result["entry"] == entry.isoformat()
        assert result["modified"] == modified.isoformat()

    def test_none_values_omitted(self):
        """Should not include None values."""
        task = make_task(priority=None, project=None, due=None)
        result = task_to_sync_dict(task)

        assert result.get("priority") is None
        assert result.get("project") is None
        assert result.get("due") is None

    def test_empty_lists(self):
        """Should include empty lists."""
        task = make_task(tags=[])
        result = task_to_sync_dict(task)
        assert result["tags"] == []

    def test_annotations(self):
        """Should include annotations."""
        task = make_task(
            annotations=[
                {"entry": "2025-12-17T10:00:00", "description": "Note 1"},
                {"entry": "2025-12-17T11:00:00", "description": "Note 2"},
            ]
        )
        result = task_to_sync_dict(task)
        assert len(result["annotations"]) == 2

    def test_uda(self):
        """Should include UDA fields."""
        task = make_task(uda={"custom": "value", "estimate": "2h"})
        result = task_to_sync_dict(task)
        assert result["uda"] == {"custom": "value", "estimate": "2h"}


class TestWriteTaskFile:
    """Test writing task files."""

    def test_write_creates_file(self, tmp_path: Path):
        """Should create task JSON file."""
        task = make_task(uuid="abc-123")
        write_task_file(task, tmp_path)

        file_path = tmp_path / "tasks" / "abc-123.json"
        assert file_path.exists()

    def test_write_valid_json(self, tmp_path: Path):
        """Should write valid JSON with nested format."""
        task = make_task(uuid="abc-123", description="Test")
        write_task_file(task, tmp_path)

        file_path = tmp_path / "tasks" / "abc-123.json"
        data = json.loads(file_path.read_text())

        # File has nested format with version and data
        assert data["uuid"] == "abc-123"
        assert data["version"] == 1
        assert data["data"]["description"] == "Test"

    def test_write_overwrite_existing(self, tmp_path: Path):
        """Should overwrite existing file."""
        task1 = make_task(uuid="abc-123", description="Original")
        write_task_file(task1, tmp_path)

        task2 = make_task(uuid="abc-123", description="Updated")
        write_task_file(task2, tmp_path)

        file_path = tmp_path / "tasks" / "abc-123.json"
        data = json.loads(file_path.read_text())
        assert data["data"]["description"] == "Updated"

    def test_write_creates_tasks_dir(self, tmp_path: Path):
        """Should create tasks directory if needed."""
        task = make_task(uuid="test-uuid")
        write_task_file(task, tmp_path)

        assert (tmp_path / "tasks").is_dir()


class TestWriteTombstone:
    """Test writing tombstone files for deleted tasks."""

    def test_tombstone_creates_file(self, tmp_path: Path):
        """Should create tombstone file."""
        write_tombstone("deleted-uuid", tmp_path)

        file_path = tmp_path / "tasks" / "deleted-uuid.json"
        assert file_path.exists()

    def test_tombstone_marked_deleted(self, tmp_path: Path):
        """Should mark task as deleted in JSON."""
        write_tombstone("deleted-uuid", tmp_path)

        file_path = tmp_path / "tasks" / "deleted-uuid.json"
        data = json.loads(file_path.read_text())

        assert data["deleted"] is True
        assert data["uuid"] == "deleted-uuid"

    def test_tombstone_has_modified(self, tmp_path: Path):
        """Should include modified timestamp."""
        write_tombstone("deleted-uuid", tmp_path)

        file_path = tmp_path / "tasks" / "deleted-uuid.json"
        data = json.loads(file_path.read_text())

        assert "modified" in data
        # Verify it's a valid ISO timestamp
        datetime.fromisoformat(data["modified"])

    def test_tombstone_replaces_task_file(self, tmp_path: Path):
        """Should replace existing task file with tombstone."""
        # First write a normal task
        task = make_task(uuid="task-uuid", description="Will be deleted")
        write_task_file(task, tmp_path)

        # Then write tombstone
        write_tombstone("task-uuid", tmp_path)

        file_path = tmp_path / "tasks" / "task-uuid.json"
        data = json.loads(file_path.read_text())

        assert data["deleted"] is True
        assert data["data"] is None
