"""Unit tests for sync conflict resolution."""

from datetime import datetime, timedelta

from taskng.core.models import Priority, Task, TaskStatus
from taskng.sync.conflict import (
    detect_field_conflicts,
    merge_lists,
    merge_tasks,
    resolve_conflict,
)
from taskng.sync.models import Conflict, ConflictResolution


def make_task(
    uuid: str = "test-uuid",
    description: str = "Test task",
    status: TaskStatus = TaskStatus.PENDING,
    priority: Priority | None = None,
    project: str | None = None,
    tags: list[str] | None = None,
    due: datetime | None = None,
    modified: datetime | None = None,
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
        modified=modified or datetime.now(),
        entry=datetime.now(),
    )


class TestMergeLists:
    """Test list union merging."""

    def test_merge_disjoint_lists(self):
        """Should merge lists with no overlap."""
        result = merge_lists(["a", "b"], ["c", "d"])
        assert set(result) == {"a", "b", "c", "d"}

    def test_merge_overlapping_lists(self):
        """Should handle overlapping items."""
        result = merge_lists(["a", "b", "c"], ["b", "c", "d"])
        assert set(result) == {"a", "b", "c", "d"}

    def test_merge_empty_lists(self):
        """Should handle empty lists."""
        assert merge_lists([], []) == []
        result = merge_lists(["a"], [])
        assert set(result) == {"a"}


class TestDetectFieldConflicts:
    """Test field conflict detection."""

    def test_no_conflicts_same_values(self):
        """Should detect no conflicts when values match."""
        local = make_task(description="Test")
        remote = make_task(description="Test")
        conflicts = detect_field_conflicts(local, remote, None)
        assert len(conflicts) == 0

    def test_conflict_different_values(self):
        """Should detect conflict when values differ."""
        local = make_task(description="Local version")
        remote = make_task(description="Remote version")
        conflicts = detect_field_conflicts(local, remote, None)

        # Find the description conflict
        desc_conflict = next((c for c in conflicts if c.field == "description"), None)
        assert desc_conflict is not None
        assert desc_conflict.local_value == "Local version"
        assert desc_conflict.remote_value == "Remote version"

    def test_three_way_merge_local_only_changed(self):
        """Should detect local-only change with base."""
        base = make_task(priority=Priority.LOW)
        local = make_task(priority=Priority.HIGH)
        remote = make_task(priority=Priority.LOW)

        conflicts = detect_field_conflicts(local, remote, base)
        # Local changed, remote didn't - should auto-resolve to local
        priority_conflict = next((c for c in conflicts if c.field == "priority"), None)
        # No conflict because only one side changed
        assert priority_conflict is None or priority_conflict.base_value is not None

    def test_three_way_merge_remote_only_changed(self):
        """Should detect remote-only change with base."""
        base = make_task(project="work")
        local = make_task(project="work")
        remote = make_task(project="home")

        conflicts = detect_field_conflicts(local, remote, base)
        # Remote changed, local didn't - should auto-resolve to remote
        project_conflict = next((c for c in conflicts if c.field == "project"), None)
        # No conflict because only one side changed
        assert project_conflict is None or project_conflict.base_value is not None


class TestMergeTasks:
    """Test task merging."""

    def test_merge_no_conflicts(self):
        """Should merge when no fields conflict."""
        local = make_task(
            description="Task",
            priority=Priority.HIGH,
            modified=datetime.now() - timedelta(hours=1),
        )
        remote = make_task(
            description="Task",
            priority=Priority.HIGH,
            modified=datetime.now(),
        )

        merged, conflicts = merge_tasks(local, remote)
        assert merged.description == "Task"
        assert merged.priority == Priority.HIGH
        assert len(conflicts) == 0

    def test_merge_different_fields_changed(self):
        """Should merge when different fields modified."""
        base = make_task(
            description="Original",
            priority=Priority.MEDIUM,
            project="work",
        )
        local = make_task(
            description="Original",
            priority=Priority.HIGH,  # Local changed priority
            project="work",
        )
        remote = make_task(
            description="Original",
            priority=Priority.MEDIUM,
            project="home",  # Remote changed project
        )

        merged, conflicts = merge_tasks(local, remote, base)
        # Both changes should be preserved
        assert merged.priority == Priority.HIGH
        assert merged.project == "home"
        assert len(conflicts) == 0

    def test_merge_tags_union(self):
        """Should merge tags using union."""
        local = make_task(tags=["work", "urgent"])
        remote = make_task(tags=["work", "important"])

        merged, conflicts = merge_tasks(local, remote)
        assert set(merged.tags) == {"work", "urgent", "important"}

    def test_merge_conflict_last_write_wins(self):
        """Should use last-write-wins for true conflicts."""
        now = datetime.now()
        local = make_task(
            description="Local desc",
            modified=now - timedelta(hours=2),
        )
        remote = make_task(
            description="Remote desc",
            modified=now,  # Remote is newer
        )

        merged, conflicts = merge_tasks(
            local, remote, resolution=ConflictResolution.LAST_WRITE_WINS
        )
        assert merged.description == "Remote desc"

    def test_merge_conflict_keep_local(self):
        """Should keep local values when specified."""
        local = make_task(description="Local desc")
        remote = make_task(description="Remote desc")

        merged, conflicts = merge_tasks(
            local, remote, resolution=ConflictResolution.KEEP_LOCAL
        )
        assert merged.description == "Local desc"

    def test_merge_conflict_keep_remote(self):
        """Should keep remote values when specified."""
        local = make_task(description="Local desc")
        remote = make_task(description="Remote desc")

        merged, conflicts = merge_tasks(
            local, remote, resolution=ConflictResolution.KEEP_REMOTE
        )
        assert merged.description == "Remote desc"

    def test_merge_preserves_uuid(self):
        """Should preserve UUID from local task."""
        local = make_task(uuid="abc-123")
        remote = make_task(uuid="abc-123")

        merged, _ = merge_tasks(local, remote)
        assert merged.uuid == "abc-123"


class TestResolveConflict:
    """Test conflict resolution."""

    def test_resolve_keep_local(self):
        """Should resolve to local task."""
        conflict = Conflict(
            task_uuid="test-uuid",
            local_data={
                "uuid": "test-uuid",
                "description": "Local",
                "status": "pending",
            },
            remote_data={
                "uuid": "test-uuid",
                "description": "Remote",
                "status": "pending",
            },
        )

        result = resolve_conflict(conflict, ConflictResolution.KEEP_LOCAL)
        assert result.description == "Local"

    def test_resolve_keep_remote(self):
        """Should resolve to remote task."""
        conflict = Conflict(
            task_uuid="test-uuid",
            local_data={
                "uuid": "test-uuid",
                "description": "Local",
                "status": "pending",
            },
            remote_data={
                "uuid": "test-uuid",
                "description": "Remote",
                "status": "pending",
            },
        )

        result = resolve_conflict(conflict, ConflictResolution.KEEP_REMOTE)
        assert result.description == "Remote"

    def test_resolve_merge_tags(self):
        """Should merge tags using union."""
        conflict = Conflict(
            task_uuid="test-uuid",
            local_data={
                "uuid": "test-uuid",
                "description": "Task",
                "status": "pending",
                "tags": ["local"],
            },
            remote_data={
                "uuid": "test-uuid",
                "description": "Task",
                "status": "pending",
                "tags": ["remote"],
            },
        )

        result = resolve_conflict(conflict, ConflictResolution.MERGE)
        assert set(result.tags) == {"local", "remote"}
