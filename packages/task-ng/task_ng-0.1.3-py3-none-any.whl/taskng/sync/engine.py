"""Sync engine orchestrator.

This module provides the main SyncEngine class that coordinates sync operations
using a pluggable backend. It handles the common sync workflow regardless of
the specific backend being used.
"""

from datetime import datetime
from typing import Any, cast

from taskng.core.models import Task
from taskng.storage.repository import TaskRepository
from taskng.sync.backend import SyncBackend, SyncError, SyncNotInitializedError
from taskng.sync.conflict import merge_tasks
from taskng.sync.import_ import sync_dict_to_task
from taskng.sync.models import (
    Conflict,
    ConflictResolution,
    RemoteChange,
    SyncChange,
    SyncOperation,
    SyncResult,
    SyncStatus,
)


class SyncEngine:
    """Orchestrates sync operations using a configured backend.

    The SyncEngine handles:
    - Collecting local changes from task_history
    - Pushing changes via the backend
    - Pulling remote changes
    - Applying field-level merge for conflicts
    - Updating local database with merged changes
    """

    def __init__(
        self,
        backend: SyncBackend,
        repo: TaskRepository,
        conflict_resolution: ConflictResolution = ConflictResolution.LAST_WRITE_WINS,
    ):
        """Initialize the sync engine.

        Args:
            backend: Sync backend to use.
            repo: Task repository for database operations.
            conflict_resolution: Default conflict resolution strategy.
        """
        self.backend = backend
        self.repo = repo
        self.conflict_resolution = conflict_resolution
        self._pending_conflicts: list[Conflict] = []

    def sync(self) -> SyncResult:
        """Perform a full bidirectional sync.

        This is the main sync method that:
        1. Pushes local changes to remote
        2. Pulls remote changes
        3. Handles conflicts with field-level merge
        4. Updates local database

        Returns:
            SyncResult with statistics and any errors.

        Raises:
            SyncNotInitializedError: If backend not initialized.
            SyncError: If sync fails.
        """
        if not self.backend.is_initialized():
            raise SyncNotInitializedError(
                f"Sync backend '{self.backend.name}' not initialized. "
                "Run 'task-ng sync init' first."
            )

        result = SyncResult(success=True)

        # Phase 1: Push local changes
        try:
            push_result = self.push()
            result.pushed = push_result.pushed
            result.errors.extend(push_result.errors)
            result.warnings.extend(push_result.warnings)
            result.conflicts_pending += push_result.conflicts_pending
        except SyncError as e:
            result.success = False
            result.add_error(f"Push failed: {e}")
            return result

        # Phase 2: Pull remote changes
        try:
            pull_result = self.pull()
            result.pulled = pull_result.pulled
            result.merged = pull_result.merged
            result.errors.extend(pull_result.errors)
            result.warnings.extend(pull_result.warnings)
        except SyncError as e:
            result.success = False
            result.add_error(f"Pull failed: {e}")
            return result

        # Phase 3: Report pending conflicts
        result.conflicts_pending = len(self._pending_conflicts)
        result.conflicts_resolved = (
            result.merged  # Merged = auto-resolved conflicts
        )

        return result

    def push(self) -> SyncResult:
        """Push local changes to remote.

        Returns:
            SyncResult with push statistics.
        """
        if not self.backend.is_initialized():
            raise SyncNotInitializedError(
                f"Sync backend '{self.backend.name}' not initialized."
            )

        result = SyncResult(success=True)

        # Get unsynced changes from repository
        changes = self._get_local_changes()

        if not changes:
            return result

        # Push via backend
        push_result = self.backend.push(changes)

        result.pushed = push_result.pushed_count
        result.errors.extend(push_result.errors)

        # Handle conflicts
        for conflict in push_result.conflicts:
            self._pending_conflicts.append(conflict)
            result.conflicts_pending += 1

        # Mark synced changes in task_history
        if push_result.success:
            synced_uuids = [
                c.task_uuid
                for c in changes
                if c.task_uuid not in [conf.task_uuid for conf in push_result.conflicts]
            ]
            self.repo.mark_synced(synced_uuids)

        result.success = push_result.success
        return result

    def pull(self) -> SyncResult:
        """Pull and apply remote changes.

        Returns:
            SyncResult with pull statistics.
        """
        if not self.backend.is_initialized():
            raise SyncNotInitializedError(
                f"Sync backend '{self.backend.name}' not initialized."
            )

        result = SyncResult(success=True)

        # Get last sync timestamp
        status = self.backend.status()
        since = status.last_sync

        # Pull from backend
        pull_result = self.backend.pull(since)

        if not pull_result.success:
            result.success = False
            result.errors.extend(pull_result.errors)
            return result

        # Apply each remote change
        for remote_change in pull_result.changes:
            try:
                action = self._apply_remote_change(remote_change)
                if action == "imported":
                    result.pulled += 1
                elif action == "merged":
                    result.merged += 1
                elif action == "conflict":
                    result.conflicts_pending += 1
            except Exception as e:
                result.add_error(
                    f"Failed to apply change for {remote_change.task_uuid}: {e}"
                )

        result.success = True
        return result

    def status(self) -> SyncStatus:
        """Get current sync status.

        Returns:
            SyncStatus with current state.
        """
        backend_status = self.backend.status()

        # Count unsynced local changes
        changes = self._get_local_changes()
        backend_status.pending_push = len(changes)

        # Count pending conflicts
        backend_status.unresolved_conflicts = len(self._pending_conflicts)

        return backend_status

    def get_pending_conflicts(self) -> list[Conflict]:
        """Get list of unresolved conflicts.

        Returns:
            List of Conflict objects.
        """
        return self._pending_conflicts.copy()

    def resolve_conflict(
        self,
        conflict: Conflict,
        resolution: ConflictResolution,
    ) -> Task:
        """Resolve a specific conflict.

        Args:
            conflict: Conflict to resolve.
            resolution: Resolution strategy.

        Returns:
            Resolved Task.
        """
        from taskng.sync.conflict import resolve_conflict

        task = resolve_conflict(conflict, resolution)

        # Update local database
        existing = self.repo.get_by_uuid(task.uuid)
        if existing:
            task.id = existing.id
            self.repo.update(task)
        else:
            self.repo.add(task)

        # Remove from pending
        self._pending_conflicts = [
            c for c in self._pending_conflicts if c.task_uuid != conflict.task_uuid
        ]

        return task

    def _get_local_changes(self) -> list[SyncChange]:
        """Get local changes that need to be synced.

        Returns:
            List of SyncChange objects from task_history.
        """
        unsynced = self.repo.get_unsynced_history()
        changes: list[SyncChange] = []

        for entry in unsynced:
            operation = SyncOperation(str(entry["operation"]))

            # Get current task data
            if operation == SyncOperation.DELETE:
                data_val = entry.get("old_data", {})
            else:
                data_val = entry.get("new_data", {})

            # Parse JSON data if it's a string
            if isinstance(data_val, str):
                import json

                data: dict[str, Any] = json.loads(data_val) if data_val else {}
            elif isinstance(data_val, dict):
                data = cast(dict[str, Any], data_val)
            else:
                data = {}

            changes.append(
                SyncChange(
                    task_uuid=str(entry["task_uuid"]),
                    operation=operation,
                    timestamp=datetime.fromisoformat(str(entry["timestamp"])),
                    data=data,
                )
            )

        return changes

    def _apply_remote_change(self, change: RemoteChange) -> str:
        """Apply a single remote change to local database.

        Args:
            change: Remote change to apply.

        Returns:
            Action taken: "imported", "merged", "skipped", or "conflict".
        """
        local_task = self.repo.get_by_uuid(change.task_uuid)

        if change.operation == SyncOperation.DELETE:
            if local_task:
                # Check if we have local modifications
                if self._has_local_modifications(change.task_uuid, change.timestamp):
                    # Conflict: local modified, remote deleted
                    self._pending_conflicts.append(
                        Conflict(
                            task_uuid=change.task_uuid,
                            local_data=local_task.model_dump(mode="json"),
                            remote_data={"deleted": True},
                        )
                    )
                    return "conflict"
                # Safe to delete
                self.repo.delete(local_task.id)  # type: ignore
            return "imported"

        # ADD or MODIFY
        remote_task = sync_dict_to_task(change.data)

        if local_task is None:
            # New task - just add it
            self.repo.add(remote_task)
            return "imported"

        # Task exists - check for conflict
        if self._has_local_modifications(change.task_uuid, change.timestamp):
            # Both modified - need to merge
            merged, conflicts = merge_tasks(
                local_task,
                remote_task,
                None,  # No base available
                self.conflict_resolution,
            )

            if conflicts:
                # True conflicts that couldn't be auto-resolved
                self._pending_conflicts.append(
                    Conflict(
                        task_uuid=change.task_uuid,
                        local_data=local_task.model_dump(mode="json"),
                        remote_data=remote_task.model_dump(mode="json"),
                        field_conflicts=conflicts,
                    )
                )
                return "conflict"

            # Auto-merged successfully
            merged.id = local_task.id
            self.repo.update(merged)
            return "merged"

        # No local modifications - take remote
        remote_task.id = local_task.id
        self.repo.update(remote_task)
        return "imported"

    def _has_local_modifications(self, task_uuid: str, since: datetime) -> bool:
        """Check if task has local modifications since a timestamp.

        Args:
            task_uuid: Task UUID to check.
            since: Check for modifications after this time.

        Returns:
            True if task was locally modified.
        """
        unsynced = self.repo.get_unsynced_history()
        for entry in unsynced:
            if str(entry["task_uuid"]) == task_uuid:
                entry_time = datetime.fromisoformat(str(entry["timestamp"]))
                if entry_time > since:
                    return True
        return False
