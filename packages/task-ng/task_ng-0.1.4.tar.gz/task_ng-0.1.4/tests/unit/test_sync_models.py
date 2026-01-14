"""Unit tests for sync models."""

from datetime import datetime

from taskng.sync.models import (
    Conflict,
    ConflictResolution,
    FieldConflict,
    PullResult,
    PushResult,
    RemoteChange,
    SyncChange,
    SyncOperation,
    SyncResult,
    SyncStatus,
)


class TestSyncOperation:
    """Test SyncOperation enum."""

    def test_operation_values(self):
        """Should have expected operation values."""
        assert SyncOperation.ADD.value == "add"
        assert SyncOperation.MODIFY.value == "modify"
        assert SyncOperation.DELETE.value == "delete"


class TestConflictResolution:
    """Test ConflictResolution enum."""

    def test_resolution_values(self):
        """Should have expected resolution values."""
        assert ConflictResolution.LAST_WRITE_WINS.value == "last_write_wins"
        assert ConflictResolution.KEEP_LOCAL.value == "keep_local"
        assert ConflictResolution.KEEP_REMOTE.value == "keep_remote"
        assert ConflictResolution.MERGE.value == "merge"


class TestSyncChange:
    """Test SyncChange dataclass."""

    def test_create_sync_change(self):
        """Should create sync change."""
        now = datetime.now()
        change = SyncChange(
            task_uuid="abc-123",
            operation=SyncOperation.ADD,
            timestamp=now,
            data={"description": "Test"},
        )

        assert change.task_uuid == "abc-123"
        assert change.operation == SyncOperation.ADD
        assert change.timestamp == now
        assert change.data == {"description": "Test"}


class TestRemoteChange:
    """Test RemoteChange dataclass."""

    def test_create_remote_change(self):
        """Should create remote change."""
        now = datetime.now()
        change = RemoteChange(
            task_uuid="abc-123",
            operation=SyncOperation.MODIFY,
            timestamp=now,
            data={"description": "Updated"},
        )

        assert change.task_uuid == "abc-123"
        assert change.operation == SyncOperation.MODIFY
        assert change.data == {"description": "Updated"}

    def test_optional_source_device(self):
        """Should support optional source device."""
        change = RemoteChange(
            task_uuid="abc-123",
            operation=SyncOperation.ADD,
            timestamp=datetime.now(),
            data={},
            source_device="device-1",
        )
        assert change.source_device == "device-1"


class TestFieldConflict:
    """Test FieldConflict dataclass."""

    def test_create_field_conflict(self):
        """Should create field conflict."""
        conflict = FieldConflict(
            field="description",
            local_value="Local",
            remote_value="Remote",
            base_value="Original",
        )

        assert conflict.field == "description"
        assert conflict.local_value == "Local"
        assert conflict.remote_value == "Remote"
        assert conflict.base_value == "Original"

    def test_without_base_value(self):
        """Should work without base value."""
        conflict = FieldConflict(
            field="priority",
            local_value="H",
            remote_value="M",
        )
        assert conflict.base_value is None


class TestConflict:
    """Test Conflict dataclass."""

    def test_create_conflict(self):
        """Should create conflict."""
        conflict = Conflict(
            task_uuid="abc-123",
            local_data={"description": "Local"},
            remote_data={"description": "Remote"},
        )

        assert conflict.task_uuid == "abc-123"
        assert conflict.local_data == {"description": "Local"}
        assert conflict.remote_data == {"description": "Remote"}

    def test_with_field_conflicts(self):
        """Should include field conflicts."""
        field_conflict = FieldConflict(
            field="description",
            local_value="Local",
            remote_value="Remote",
        )
        conflict = Conflict(
            task_uuid="abc-123",
            local_data={"description": "Local"},
            remote_data={"description": "Remote"},
            field_conflicts=[field_conflict],
        )

        assert len(conflict.field_conflicts) == 1
        assert conflict.field_conflicts[0].field == "description"


class TestPushResult:
    """Test PushResult dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        result = PushResult(success=True)

        assert result.success is True
        assert result.pushed_count == 0
        assert result.conflicts == []
        assert result.errors == []

    def test_with_conflicts(self):
        """Should store conflicts."""
        conflict = Conflict(
            task_uuid="abc-123",
            local_data={},
            remote_data={},
        )
        result = PushResult(
            success=False,
            conflicts=[conflict],
        )

        assert result.success is False
        assert len(result.conflicts) == 1


class TestPullResult:
    """Test PullResult dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        result = PullResult(success=True)

        assert result.success is True
        assert result.changes == []
        assert result.errors == []
        assert result.last_sync is None

    def test_with_changes(self):
        """Should store changes."""
        change = RemoteChange(
            task_uuid="abc-123",
            operation=SyncOperation.ADD,
            timestamp=datetime.now(),
            data={},
        )
        result = PullResult(
            success=True,
            changes=[change],
        )

        assert len(result.changes) == 1


class TestSyncStatus:
    """Test SyncStatus dataclass."""

    def test_create_status(self):
        """Should create sync status."""
        now = datetime.now()
        status = SyncStatus(
            enabled=True,
            backend="git",
            last_sync=now,
            remote_url="git@github.com:user/repo.git",
            device_id="device-123",
        )

        assert status.enabled is True
        assert status.backend == "git"
        assert status.last_sync == now
        assert status.remote_url == "git@github.com:user/repo.git"
        assert status.device_id == "device-123"

    def test_default_counts(self):
        """Should have zero counts by default."""
        status = SyncStatus(enabled=False, backend="git")

        assert status.pending_push == 0
        assert status.pending_pull == 0
        assert status.unresolved_conflicts == 0


class TestSyncResult:
    """Test SyncResult dataclass."""

    def test_default_values(self):
        """Should have sensible defaults."""
        result = SyncResult(success=True)

        assert result.success is True
        assert result.pushed == 0
        assert result.pulled == 0
        assert result.merged == 0
        assert result.conflicts_pending == 0
        assert result.conflicts_resolved == 0
        assert result.errors == []
        assert result.warnings == []

    def test_add_error(self):
        """Should support adding errors."""
        result = SyncResult(success=True)
        result.add_error("Something went wrong")
        result.add_error("Another error")

        assert len(result.errors) == 2
        assert "Something went wrong" in result.errors

    def test_add_warning(self):
        """Should support adding warnings."""
        result = SyncResult(success=True)
        result.add_warning("Minor issue")

        assert len(result.warnings) == 1
        assert "Minor issue" in result.warnings
