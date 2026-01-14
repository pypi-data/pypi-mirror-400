"""Unit tests for sync import functionality."""

import json
from datetime import datetime
from pathlib import Path

import pytest

from taskng.core.models import Priority, TaskStatus
from taskng.sync.import_ import (
    get_file_modified_time,
    parse_datetime,
    parse_priority,
    parse_status,
    read_task_file,
    scan_changes_since,
    scan_sync_dir,
    sync_dict_to_task,
)


class TestParseDatetime:
    """Test datetime parsing."""

    def test_parse_valid_iso(self):
        """Should parse valid ISO datetime."""
        result = parse_datetime("2025-12-17T10:30:00")
        assert result == datetime(2025, 12, 17, 10, 30, 0)

    def test_parse_with_microseconds(self):
        """Should parse ISO with microseconds."""
        result = parse_datetime("2025-12-17T10:30:00.123456")
        assert result is not None
        assert result.year == 2025

    def test_parse_none(self):
        """Should return None for None input."""
        assert parse_datetime(None) is None

    def test_parse_empty_string(self):
        """Should return None for empty string."""
        assert parse_datetime("") is None

    def test_parse_invalid_format(self):
        """Should return None for invalid format."""
        assert parse_datetime("not-a-date") is None


class TestParseStatus:
    """Test status parsing."""

    def test_parse_pending(self):
        """Should parse pending status."""
        assert parse_status("pending") == TaskStatus.PENDING

    def test_parse_completed(self):
        """Should parse completed status."""
        assert parse_status("completed") == TaskStatus.COMPLETED

    def test_parse_deleted(self):
        """Should parse deleted status."""
        assert parse_status("deleted") == TaskStatus.DELETED

    def test_parse_none(self):
        """Should default to pending for None."""
        assert parse_status(None) == TaskStatus.PENDING

    def test_parse_invalid(self):
        """Should default to pending for invalid."""
        assert parse_status("invalid") == TaskStatus.PENDING


class TestParsePriority:
    """Test priority parsing."""

    def test_parse_high(self):
        """Should parse high priority."""
        assert parse_priority("H") == Priority.HIGH

    def test_parse_medium(self):
        """Should parse medium priority."""
        assert parse_priority("M") == Priority.MEDIUM

    def test_parse_low(self):
        """Should parse low priority."""
        assert parse_priority("L") == Priority.LOW

    def test_parse_none(self):
        """Should return None for None input."""
        assert parse_priority(None) is None

    def test_parse_empty(self):
        """Should return None for empty string."""
        assert parse_priority("") is None

    def test_parse_invalid(self):
        """Should return None for invalid value."""
        assert parse_priority("invalid") is None


class TestSyncDictToTask:
    """Test dictionary to task conversion."""

    def test_basic_fields(self):
        """Should convert basic fields."""
        data = {
            "uuid": "abc-123",
            "description": "Test task",
            "status": "pending",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
        }
        task = sync_dict_to_task(data)

        assert task.uuid == "abc-123"
        assert task.description == "Test task"
        assert task.status == TaskStatus.PENDING

    def test_optional_fields(self):
        """Should convert optional fields."""
        data = {
            "uuid": "abc-123",
            "description": "Test",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
            "priority": "H",
            "project": "work",
            "tags": ["urgent"],
        }
        task = sync_dict_to_task(data)

        assert task.priority == Priority.HIGH
        assert task.project == "work"
        assert task.tags == ["urgent"]

    def test_datetime_fields(self):
        """Should convert datetime fields."""
        data = {
            "uuid": "abc-123",
            "description": "Test",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
            "due": "2025-12-25T09:00:00",
        }
        task = sync_dict_to_task(data)

        assert task.entry == datetime(2025, 12, 17, 10, 0, 0)
        assert task.modified == datetime(2025, 12, 17, 11, 0, 0)
        assert task.due == datetime(2025, 12, 25, 9, 0, 0)

    def test_missing_required_uuid(self):
        """Should raise error for missing UUID."""
        data = {"description": "Test"}
        with pytest.raises(ValueError, match="uuid"):
            sync_dict_to_task(data)

    def test_missing_required_description(self):
        """Should raise error for missing description."""
        data = {"uuid": "abc-123"}
        with pytest.raises(ValueError, match="description"):
            sync_dict_to_task(data)

    def test_nested_data_format(self):
        """Should handle nested data format."""
        data = {
            "uuid": "abc-123",
            "data": {
                "uuid": "abc-123",
                "description": "Nested task",
                "status": "pending",
                "entry": "2025-12-17T10:00:00",
                "modified": "2025-12-17T11:00:00",
            },
        }
        task = sync_dict_to_task(data)
        assert task.description == "Nested task"

    def test_annotations(self):
        """Should convert annotations."""
        data = {
            "uuid": "abc-123",
            "description": "Test",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
            "annotations": [
                {"entry": "2025-12-17T10:00:00", "description": "Note 1"},
                {"entry": "2025-12-17T11:00:00", "description": "Note 2"},
            ],
        }
        task = sync_dict_to_task(data)
        assert len(task.annotations) == 2

    def test_uda(self):
        """Should convert UDA fields."""
        data = {
            "uuid": "abc-123",
            "description": "Test",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
            "uda": {"custom": "value"},
        }
        task = sync_dict_to_task(data)
        assert task.uda == {"custom": "value"}

    def test_depends(self):
        """Should convert depends list."""
        data = {
            "uuid": "abc-123",
            "description": "Test",
            "entry": "2025-12-17T10:00:00",
            "modified": "2025-12-17T11:00:00",
            "depends": ["dep-1", "dep-2"],
        }
        task = sync_dict_to_task(data)
        assert task.depends == ["dep-1", "dep-2"]


class TestReadTaskFile:
    """Test reading task files."""

    def test_read_valid_task(self, tmp_path: Path):
        """Should read valid task file."""
        data = {
            "uuid": "abc-123",
            "data": {
                "uuid": "abc-123",
                "description": "Test task",
                "status": "pending",
                "entry": "2025-12-17T10:00:00",
                "modified": "2025-12-17T11:00:00",
            },
        }
        file_path = tmp_path / "task.json"
        file_path.write_text(json.dumps(data))

        task, is_deleted = read_task_file(file_path)

        assert task is not None
        assert task.uuid == "abc-123"
        assert is_deleted is False

    def test_read_tombstone(self, tmp_path: Path):
        """Should detect tombstone file."""
        data = {
            "uuid": "deleted-uuid",
            "deleted": True,
            "modified": datetime.now().isoformat(),
        }
        file_path = tmp_path / "task.json"
        file_path.write_text(json.dumps(data))

        task, is_deleted = read_task_file(file_path)

        assert task is None
        assert is_deleted is True

    def test_read_nested_format(self, tmp_path: Path):
        """Should read nested data format."""
        data = {
            "uuid": "abc-123",
            "data": {
                "uuid": "abc-123",
                "description": "Nested",
                "status": "completed",
                "entry": "2025-12-17T10:00:00",
                "modified": "2025-12-17T11:00:00",
            },
        }
        file_path = tmp_path / "task.json"
        file_path.write_text(json.dumps(data))

        task, is_deleted = read_task_file(file_path)

        assert task is not None
        assert task.description == "Nested"


class TestGetFileModifiedTime:
    """Test getting file modified timestamp."""

    def test_from_json_modified_field(self, tmp_path: Path):
        """Should get time from JSON modified field."""
        data = {
            "uuid": "abc-123",
            "modified": "2025-12-17T15:30:00",
        }
        file_path = tmp_path / "task.json"
        file_path.write_text(json.dumps(data))

        result = get_file_modified_time(file_path)
        assert result == datetime(2025, 12, 17, 15, 30, 0)

    def test_fallback_to_filesystem(self, tmp_path: Path):
        """Should fall back to filesystem mtime."""
        data = {"uuid": "abc-123"}  # No modified field
        file_path = tmp_path / "task.json"
        file_path.write_text(json.dumps(data))

        result = get_file_modified_time(file_path)
        # Should return filesystem time (approximately now)
        assert isinstance(result, datetime)


class TestScanSyncDir:
    """Test scanning sync directory."""

    def test_scan_empty_dir(self, tmp_path: Path):
        """Should return empty list for empty directory."""
        (tmp_path / "tasks").mkdir()
        result = scan_sync_dir(tmp_path)
        assert result == []

    def test_scan_nonexistent_dir(self, tmp_path: Path):
        """Should return empty list if tasks dir doesn't exist."""
        result = scan_sync_dir(tmp_path)
        assert result == []

    def test_scan_finds_json_files(self, tmp_path: Path):
        """Should find JSON files in tasks directory."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        (tasks_dir / "task1.json").write_text("{}")
        (tasks_dir / "task2.json").write_text("{}")
        (tasks_dir / "not-json.txt").write_text("text")

        result = scan_sync_dir(tmp_path)
        assert len(result) == 2
        assert all(p.suffix == ".json" for p in result)


class TestScanChangesSince:
    """Test scanning for changed files."""

    def test_scan_all_when_since_none(self, tmp_path: Path):
        """Should return all files when since is None."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        (tasks_dir / "task1.json").write_text('{"modified": "2025-12-17T10:00:00"}')
        (tasks_dir / "task2.json").write_text('{"modified": "2025-12-17T11:00:00"}')

        result = scan_changes_since(tmp_path, since=None)
        assert len(result) == 2

    def test_scan_filters_by_time(self, tmp_path: Path):
        """Should filter files by modified time."""
        tasks_dir = tmp_path / "tasks"
        tasks_dir.mkdir()

        # Old file
        (tasks_dir / "old.json").write_text('{"modified": "2025-12-17T10:00:00"}')
        # New file
        (tasks_dir / "new.json").write_text('{"modified": "2025-12-17T15:00:00"}')

        since = datetime(2025, 12, 17, 12, 0, 0)
        result = scan_changes_since(tmp_path, since=since)

        assert len(result) == 1
        assert result[0].stem == "new"
