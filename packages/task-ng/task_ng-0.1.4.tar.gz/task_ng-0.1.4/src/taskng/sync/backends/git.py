"""Git-based sync backend.

This backend stores tasks as individual JSON files in a git repository,
using git as the transport mechanism for synchronization.
"""

import json
import socket
import subprocess
from contextlib import suppress
from datetime import datetime
from pathlib import Path
from typing import Any
from uuid import uuid4

from taskng.sync.backend import (
    SyncBackend,
    SyncError,
    SyncNotInitializedError,
)
from taskng.sync.export import task_to_sync_dict, write_task_file, write_tombstone
from taskng.sync.import_ import (
    get_file_modified_time,
    read_task_file,
    scan_changes_since,
)
from taskng.sync.models import (
    Conflict,
    PullResult,
    PushResult,
    RemoteChange,
    SyncChange,
    SyncOperation,
    SyncStatus,
)


class GitBackend(SyncBackend):
    """Git-based sync backend.

    Tasks are stored as individual JSON files in a git repository:
    - sync_dir/tasks/{uuid}.json - one file per task
    - sync_dir/metadata/device.json - device identity
    - sync_dir/metadata/state.json - sync state

    Sync workflow:
    1. Export changed tasks to JSON files
    2. Git add, commit
    3. Git pull --rebase
    4. Resolve any conflicts
    5. Git push
    6. Import any pulled changes
    """

    def __init__(self, sync_dir: Path | None = None):
        """Initialize the git backend.

        Args:
            sync_dir: Directory for sync repository.
                     Defaults to ~/.local/share/taskng/sync
        """
        if sync_dir is None:
            sync_dir = Path.home() / ".local" / "share" / "taskng" / "sync"
        self._sync_dir = sync_dir
        self._device_id: str | None = None
        self._device_name: str | None = None

    @property
    def name(self) -> str:
        """Return the backend name."""
        return "git"

    def get_sync_dir(self) -> Path:
        """Get the sync directory path."""
        return self._sync_dir

    def is_initialized(self) -> bool:
        """Check if the git repository is initialized."""
        git_dir = self._sync_dir / ".git"
        device_file = self._sync_dir / "metadata" / "device.json"
        return git_dir.exists() and device_file.exists()

    def initialize(self, remote: str | None = None) -> None:
        """Initialize the git repository for sync.

        Args:
            remote: Optional git remote URL.

        Raises:
            SyncError: If initialization fails.
        """
        # Create directory structure
        self._sync_dir.mkdir(parents=True, exist_ok=True)
        (self._sync_dir / "tasks").mkdir(exist_ok=True)
        (self._sync_dir / "metadata").mkdir(exist_ok=True)

        # Initialize git repo
        if not (self._sync_dir / ".git").exists():
            result = subprocess.run(
                ["git", "init"],
                cwd=self._sync_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise SyncError(f"Failed to initialize git repository: {result.stderr}")

        # Create device identity
        self._device_id = str(uuid4())
        self._device_name = socket.gethostname()
        device_data = {
            "device_id": self._device_id,
            "device_name": self._device_name,
            "created": datetime.now().isoformat(),
        }
        (self._sync_dir / "metadata" / "device.json").write_text(
            json.dumps(device_data, indent=2)
        )

        # Create sync state file
        state_data = {
            "last_sync": None,
            "last_push": None,
            "last_pull": None,
        }
        (self._sync_dir / "metadata" / "state.json").write_text(
            json.dumps(state_data, indent=2)
        )

        # Create .gitignore
        gitignore = "*.lock\n*.tmp\n"
        (self._sync_dir / ".gitignore").write_text(gitignore)

        # Add remote if provided
        if remote:
            # Remove existing origin if present
            subprocess.run(
                ["git", "remote", "remove", "origin"],
                cwd=self._sync_dir,
                capture_output=True,
            )
            result = subprocess.run(
                ["git", "remote", "add", "origin", remote],
                cwd=self._sync_dir,
                capture_output=True,
                text=True,
            )
            if result.returncode != 0:
                raise SyncError(f"Failed to add remote: {result.stderr}")

        # Initial commit
        subprocess.run(
            ["git", "add", "-A"],
            cwd=self._sync_dir,
            capture_output=True,
        )
        result = subprocess.run(
            ["git", "commit", "-m", f"Initialize sync from {self._device_name}"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        # Commit may fail if already initialized, that's okay

    def push(self, changes: list[SyncChange]) -> PushResult:
        """Push local changes to the remote.

        Args:
            changes: List of changes to push.

        Returns:
            PushResult with success status and any conflicts.
        """
        if not self.is_initialized():
            raise SyncNotInitializedError("Git backend not initialized")

        result = PushResult(success=True)
        conflicts: list[Conflict] = []

        # Export changes to files
        for change in changes:
            if change.operation == SyncOperation.DELETE:
                write_tombstone(change.task_uuid, self._sync_dir)
            else:
                # Write task data to file
                from taskng.core.models import Task

                task = Task(**change.data)
                write_task_file(task, self._sync_dir)

        # Git add all changes
        add_result = subprocess.run(
            ["git", "add", "-A"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if add_result.returncode != 0:
            result.success = False
            result.errors.append(f"Git add failed: {add_result.stderr}")
            return result

        # Check if there are changes to commit
        status_result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if not status_result.stdout.strip():
            # No changes to commit
            result.pushed_count = 0
            return result

        # Commit changes
        device_name = self._get_device_name()
        commit_msg = f"Sync from {device_name} at {datetime.now().isoformat()}"
        commit_result = subprocess.run(
            ["git", "commit", "-m", commit_msg],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if commit_result.returncode != 0:
            result.success = False
            result.errors.append(f"Git commit failed: {commit_result.stderr}")
            return result

        # Check if remote is configured
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if remote_result.returncode != 0:
            # No remote configured - local only
            result.pushed_count = len(changes)
            self._update_state(last_push=datetime.now())
            return result

        # Pull with rebase to get remote changes
        pull_result = subprocess.run(
            ["git", "pull", "--rebase", "origin", "main"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )

        if pull_result.returncode != 0:
            if "CONFLICT" in pull_result.stderr or "CONFLICT" in pull_result.stdout:
                # Handle git conflicts
                conflicts = self._detect_git_conflicts()
                if conflicts:
                    result.conflicts = conflicts
                    # Abort rebase to leave repo clean
                    subprocess.run(
                        ["git", "rebase", "--abort"],
                        cwd=self._sync_dir,
                        capture_output=True,
                    )
                    result.success = False
                    return result
            elif "couldn't find remote ref" not in pull_result.stderr:
                # Real error (not just empty remote)
                result.errors.append(f"Git pull failed: {pull_result.stderr}")
                result.success = False
                return result

        # Push to remote
        push_git_result = subprocess.run(
            ["git", "push", "-u", "origin", "main"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if push_git_result.returncode != 0:
            # Try creating main branch
            subprocess.run(
                ["git", "branch", "-M", "main"],
                cwd=self._sync_dir,
                capture_output=True,
            )
            push_git_result = subprocess.run(
                ["git", "push", "-u", "origin", "main"],
                cwd=self._sync_dir,
                capture_output=True,
                text=True,
            )
            if push_git_result.returncode != 0:
                result.errors.append(f"Git push failed: {push_git_result.stderr}")
                result.success = False
                return result

        result.pushed_count = len(changes)
        self._update_state(last_push=datetime.now())
        return result

    def pull(self, since: datetime | None = None) -> PullResult:
        """Pull changes from the remote.

        Args:
            since: Only pull changes after this timestamp.

        Returns:
            PullResult with changes and status.
        """
        if not self.is_initialized():
            raise SyncNotInitializedError("Git backend not initialized")

        result = PullResult(success=True)

        # Check if remote is configured
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        if remote_result.returncode != 0:
            # No remote configured - nothing to pull
            return result

        # Get current HEAD before pull
        head_before = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        ).stdout.strip()

        # Pull from remote
        pull_git_result = subprocess.run(
            ["git", "pull", "origin", "main"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )

        if pull_git_result.returncode != 0:
            if "couldn't find remote ref" in pull_git_result.stderr:
                # Remote is empty - nothing to pull
                return result
            result.success = False
            result.errors.append(f"Git pull failed: {pull_git_result.stderr}")
            return result

        # Get HEAD after pull
        head_after = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        ).stdout.strip()

        if head_before == head_after:
            # No new commits
            return result

        # Find changed files
        if since is None:
            since = self._get_last_pull()

        changed_files = scan_changes_since(self._sync_dir, since)

        # Convert to RemoteChange objects
        for file_path in changed_files:
            try:
                task, is_deleted = read_task_file(file_path)
                if is_deleted:
                    result.changes.append(
                        RemoteChange(
                            task_uuid=file_path.stem,
                            operation=SyncOperation.DELETE,
                            timestamp=get_file_modified_time(file_path),
                            data={},
                        )
                    )
                elif task:
                    # Determine if this is add or modify
                    operation = SyncOperation.ADD  # Will be updated by engine
                    result.changes.append(
                        RemoteChange(
                            task_uuid=task.uuid,
                            operation=operation,
                            timestamp=task.modified,
                            data=task_to_sync_dict(task),
                        )
                    )
            except Exception as e:
                result.errors.append(f"Failed to read {file_path}: {e}")

        result.last_sync = datetime.now()
        self._update_state(last_pull=datetime.now())
        return result

    def status(self) -> SyncStatus:
        """Get current sync status."""
        if not self.is_initialized():
            return SyncStatus(
                enabled=False,
                backend=self.name,
            )

        state = self._load_state()
        device_info = self._load_device_info()

        # Get remote URL
        remote_result = subprocess.run(
            ["git", "remote", "get-url", "origin"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )
        remote_url = (
            remote_result.stdout.strip() if remote_result.returncode == 0 else None
        )

        # Parse last_sync from ISO string
        last_sync_str = state.get("last_sync")
        last_sync: datetime | None = None
        if last_sync_str:
            with suppress(ValueError):
                last_sync = datetime.fromisoformat(last_sync_str)

        return SyncStatus(
            enabled=True,
            backend=self.name,
            last_sync=last_sync,
            remote_url=remote_url,
            device_id=device_info.get("device_id"),
        )

    def validate_config(self, config: dict[str, Any]) -> list[str]:
        """Validate git backend configuration."""
        errors: list[str] = []

        if "directory" in config:
            path = Path(str(config["directory"])).expanduser()
            if path.exists() and not path.is_dir():
                errors.append(f"Sync directory '{path}' exists but is not a directory")

        return errors

    def _get_device_name(self) -> str:
        """Get the device name for commits."""
        if self._device_name:
            return self._device_name
        device_info = self._load_device_info()
        return str(device_info.get("device_name", socket.gethostname()))

    def _load_device_info(self) -> dict[str, Any]:
        """Load device information from file."""
        device_file = self._sync_dir / "metadata" / "device.json"
        if device_file.exists():
            result: dict[str, Any] = json.loads(device_file.read_text())
            return result
        return {}

    def _load_state(self) -> dict[str, Any]:
        """Load sync state from file."""
        state_file = self._sync_dir / "metadata" / "state.json"
        if state_file.exists():
            result: dict[str, Any] = json.loads(state_file.read_text())
            return result
        return {}

    def _update_state(
        self,
        last_sync: datetime | None = None,
        last_push: datetime | None = None,
        last_pull: datetime | None = None,
    ) -> None:
        """Update sync state file."""
        state = self._load_state()

        if last_sync:
            state["last_sync"] = last_sync.isoformat()
        if last_push:
            state["last_push"] = last_push.isoformat()
            state["last_sync"] = last_push.isoformat()
        if last_pull:
            state["last_pull"] = last_pull.isoformat()
            state["last_sync"] = last_pull.isoformat()

        state_file = self._sync_dir / "metadata" / "state.json"
        state_file.write_text(json.dumps(state, indent=2))

    def _get_last_pull(self) -> datetime | None:
        """Get timestamp of last pull."""
        state = self._load_state()
        last_pull = state.get("last_pull")
        if last_pull:
            return datetime.fromisoformat(last_pull)
        return None

    def _detect_git_conflicts(self) -> list[Conflict]:
        """Detect git merge conflicts in the repository.

        Returns:
            List of Conflict objects for conflicting files.
        """
        conflicts: list[Conflict] = []

        # Get list of conflicting files
        result = subprocess.run(
            ["git", "diff", "--name-only", "--diff-filter=U"],
            cwd=self._sync_dir,
            capture_output=True,
            text=True,
        )

        for line in result.stdout.strip().split("\n"):
            if not line or not line.endswith(".json"):
                continue

            file_path = self._sync_dir / line
            if not file_path.exists():
                continue

            # For now, create a basic conflict - full resolution would parse
            # the git conflict markers
            uuid = file_path.stem
            conflicts.append(
                Conflict(
                    task_uuid=uuid,
                    local_data={},
                    remote_data={},
                )
            )

        return conflicts
