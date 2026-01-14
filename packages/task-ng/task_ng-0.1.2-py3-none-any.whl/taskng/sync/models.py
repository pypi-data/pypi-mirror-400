"""Data models for sync operations."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any


class SyncOperation(str, Enum):
    """Types of sync operations."""

    ADD = "add"
    MODIFY = "modify"
    DELETE = "delete"


class ConflictResolution(str, Enum):
    """Conflict resolution strategies."""

    LAST_WRITE_WINS = "last_write_wins"
    KEEP_LOCAL = "keep_local"
    KEEP_REMOTE = "keep_remote"
    MERGE = "merge"


@dataclass
class SyncChange:
    """Represents a single change to sync."""

    task_uuid: str
    operation: SyncOperation
    timestamp: datetime
    data: dict[str, Any]  # Full task JSON
    base_version: int | None = None  # Version this change was based on


@dataclass
class RemoteChange:
    """Change received from remote."""

    task_uuid: str
    operation: SyncOperation
    timestamp: datetime
    data: dict[str, Any]
    source_device: str | None = None


@dataclass
class FieldConflict:
    """Conflict on a specific field."""

    field: str
    local_value: object
    remote_value: object
    base_value: object | None = None


@dataclass
class Conflict:
    """Full conflict information for a task."""

    task_uuid: str
    local_data: dict[str, Any]
    remote_data: dict[str, Any]
    base_data: dict[str, Any] | None = None
    field_conflicts: list[FieldConflict] = field(default_factory=list)
    resolved: bool = False
    resolution: ConflictResolution | None = None


@dataclass
class PushResult:
    """Result of pushing changes to remote."""

    success: bool
    pushed_count: int = 0
    conflicts: list[Conflict] = field(default_factory=list)
    errors: list[str] = field(default_factory=list)


@dataclass
class PullResult:
    """Result of pulling changes from remote."""

    success: bool
    changes: list[RemoteChange] = field(default_factory=list)
    last_sync: datetime | None = None
    has_more: bool = False
    errors: list[str] = field(default_factory=list)


@dataclass
class SyncStatus:
    """Current sync status."""

    enabled: bool
    backend: str
    last_sync: datetime | None = None
    pending_push: int = 0
    pending_pull: int = 0
    unresolved_conflicts: int = 0
    remote_url: str | None = None
    device_id: str | None = None


@dataclass
class SyncResult:
    """Overall result of a sync operation."""

    success: bool
    pushed: int = 0
    pulled: int = 0
    merged: int = 0
    conflicts_resolved: int = 0
    conflicts_pending: int = 0
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)

    @property
    def has_conflicts(self) -> bool:
        """Check if there are unresolved conflicts."""
        return self.conflicts_pending > 0

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)


@dataclass
class SyncState:
    """Persistent sync state for a device."""

    device_id: str
    device_name: str
    last_sync: datetime | None = None
    last_push: datetime | None = None
    last_pull: datetime | None = None
    remote_url: str | None = None
    backend: str = "git"
