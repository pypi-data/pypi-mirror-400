"""Sync module for multi-device task synchronization.

This module provides a pluggable sync architecture with multiple backend options:
- Git-based sync (default)
- File-based sync (future)
- Server-based sync (future)

Usage:
    from taskng.sync import SyncEngine, get_backend
    from taskng.storage.repository import TaskRepository
    from taskng.storage.database import Database

    # Get configured backend
    backend = get_backend()

    # Create engine
    db = Database()
    repo = TaskRepository(db)
    engine = SyncEngine(backend, repo)

    # Sync
    result = engine.sync()
"""

from pathlib import Path
from typing import Any

from taskng.sync.backend import (
    SyncBackend,
    SyncConflictError,
    SyncError,
    SyncNetworkError,
    SyncNotInitializedError,
)
from taskng.sync.backends.git import GitBackend
from taskng.sync.conflict import (
    detect_field_conflicts,
    merge_tasks,
)
from taskng.sync.engine import SyncEngine
from taskng.sync.models import (
    Conflict,
    ConflictResolution,
    PullResult,
    PushResult,
    RemoteChange,
    SyncChange,
    SyncOperation,
    SyncResult,
    SyncState,
    SyncStatus,
)


def get_backend(
    backend_type: str = "git",
    config: dict[str, Any] | None = None,
) -> SyncBackend:
    """Get a sync backend instance.

    Args:
        backend_type: Type of backend ("git", "file", "server").
        config: Backend-specific configuration.

    Returns:
        SyncBackend instance.

    Raises:
        ValueError: If backend type is unknown.
    """
    config = config or {}

    if backend_type == "git":
        sync_dir = config.get("directory")
        if sync_dir:
            sync_dir = Path(sync_dir).expanduser()
        return GitBackend(sync_dir)
    # Future backends:
    # elif backend_type == "file":
    #     return FileBackend(config)
    # elif backend_type == "server":
    #     return ServerBackend(config)
    else:
        raise ValueError(f"Unknown backend type: {backend_type}")


__all__ = [
    # Backend
    "SyncBackend",
    "SyncError",
    "SyncConflictError",
    "SyncNetworkError",
    "SyncNotInitializedError",
    # Backends
    "GitBackend",
    "get_backend",
    # Engine
    "SyncEngine",
    # Models
    "Conflict",
    "ConflictResolution",
    "PullResult",
    "PushResult",
    "RemoteChange",
    "SyncChange",
    "SyncOperation",
    "SyncResult",
    "SyncState",
    "SyncStatus",
    # Functions
    "detect_field_conflicts",
    "merge_tasks",
]
