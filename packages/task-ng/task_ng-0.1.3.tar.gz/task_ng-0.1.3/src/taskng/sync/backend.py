"""Abstract base class for sync backends."""

from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Any

from taskng.sync.models import Conflict, PullResult, PushResult, SyncChange, SyncStatus


class SyncBackend(ABC):
    """Abstract base class for sync backends.

    All sync backends must implement this interface to enable
    pluggable sync mechanisms (git, file-based, server, etc.).
    """

    @property
    @abstractmethod
    def name(self) -> str:
        """Return the backend name (e.g., 'git', 'file', 'server')."""
        pass

    @abstractmethod
    def initialize(self, remote: str | None = None) -> None:
        """Initialize the backend for first-time use.

        Args:
            remote: Optional remote URL/path for the sync destination.

        Raises:
            SyncError: If initialization fails.
        """
        pass

    @abstractmethod
    def is_initialized(self) -> bool:
        """Check if the backend has been initialized."""
        pass

    @abstractmethod
    def push(self, changes: list[SyncChange]) -> PushResult:
        """Push local changes to the remote.

        Args:
            changes: List of changes to push.

        Returns:
            PushResult with success status and any conflicts.

        Raises:
            SyncError: If push fails due to network or other errors.
        """
        pass

    @abstractmethod
    def pull(self, since: datetime | None = None) -> PullResult:
        """Pull changes from the remote.

        Args:
            since: Only pull changes after this timestamp. If None,
                   pull all changes since last recorded sync.

        Returns:
            PullResult with changes and status.

        Raises:
            SyncError: If pull fails due to network or other errors.
        """
        pass

    @abstractmethod
    def status(self) -> SyncStatus:
        """Get current sync status without making changes.

        Returns:
            SyncStatus with current state information.
        """
        pass

    @abstractmethod
    def get_sync_dir(self) -> Path:
        """Get the directory used for sync data.

        Returns:
            Path to the sync directory.
        """
        pass

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate backend configuration.

        Args:
            config: Configuration dictionary for this backend.

        Returns:
            List of validation error messages (empty if valid).
        """
        return []


class SyncError(Exception):
    """Base exception for sync errors."""

    pass


class SyncConflictError(SyncError):
    """Exception raised when sync conflicts cannot be auto-resolved."""

    def __init__(self, message: str, conflicts: list[Conflict] | None = None):
        super().__init__(message)
        self.conflicts = conflicts or []


class SyncNotInitializedError(SyncError):
    """Exception raised when sync is used before initialization."""

    pass


class SyncNetworkError(SyncError):
    """Exception raised for network-related sync failures."""

    pass
