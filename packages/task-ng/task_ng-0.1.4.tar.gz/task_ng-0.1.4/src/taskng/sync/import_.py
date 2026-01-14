"""Import tasks from sync files.

This module provides deserialization of JSON sync files to Task objects.
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Any, cast

from taskng.core.models import Priority, Task, TaskStatus


def parse_datetime(value: str | None) -> datetime | None:
    """Parse an ISO datetime string.

    Args:
        value: ISO format datetime string or None.

    Returns:
        Parsed datetime or None.
    """
    if not value:
        return None
    try:
        return datetime.fromisoformat(value)
    except ValueError:
        return None


def parse_status(value: str | None) -> TaskStatus:
    """Parse a status string to TaskStatus enum.

    Args:
        value: Status string.

    Returns:
        TaskStatus enum value, defaults to PENDING.
    """
    if not value:
        return TaskStatus.PENDING
    try:
        return TaskStatus(value)
    except ValueError:
        return TaskStatus.PENDING


def parse_priority(value: str | None) -> Priority | None:
    """Parse a priority string to Priority enum.

    Args:
        value: Priority string (H, M, L).

    Returns:
        Priority enum value or None.
    """
    if not value:
        return None
    try:
        return Priority(value)
    except ValueError:
        return None


def sync_dict_to_task(data: dict[str, Any]) -> Task:
    """Convert a sync dictionary to a Task object.

    Args:
        data: Task data dictionary from sync file.

    Returns:
        Task object.

    Raises:
        ValueError: If required fields are missing.
    """
    # Handle both flat format and nested 'data' format
    task_data = data.get("data", data)
    if isinstance(task_data, dict) and "description" in task_data:
        data = cast(dict[str, Any], task_data)

    if "uuid" not in data or "description" not in data:
        raise ValueError("Missing required fields: uuid, description")

    # Extract values with proper type handling
    task_id = data.get("id")
    urgency_val = data.get("urgency")
    tags_val = data.get("tags")
    depends_val = data.get("depends")
    annotations_val = data.get("annotations")
    uda_val = data.get("uda")

    return Task(
        uuid=str(data["uuid"]),
        description=str(data["description"]),
        status=parse_status(str(data.get("status", "pending"))),
        id=task_id if isinstance(task_id, int) else None,
        priority=parse_priority(
            str(data["priority"]) if data.get("priority") else None
        ),
        project=str(data["project"]) if data.get("project") else None,
        entry=parse_datetime(str(data["entry"])) or datetime.now(),
        modified=parse_datetime(str(data["modified"])) or datetime.now(),
        due=parse_datetime(str(data["due"]) if data.get("due") else None),
        scheduled=parse_datetime(
            str(data["scheduled"]) if data.get("scheduled") else None
        ),
        wait=parse_datetime(str(data["wait"]) if data.get("wait") else None),
        until=parse_datetime(str(data["until"]) if data.get("until") else None),
        start=parse_datetime(str(data["start"]) if data.get("start") else None),
        end=parse_datetime(str(data["end"]) if data.get("end") else None),
        recur=str(data["recur"]) if data.get("recur") else None,
        parent_uuid=str(data["parent_uuid"]) if data.get("parent_uuid") else None,
        notes=str(data["notes"]) if data.get("notes") else None,
        urgency=float(urgency_val) if urgency_val is not None else 0.0,
        tags=list(tags_val) if isinstance(tags_val, list) else [],
        depends=list(depends_val) if isinstance(depends_val, list) else [],
        annotations=list(annotations_val) if isinstance(annotations_val, list) else [],
        uda=dict(uda_val) if isinstance(uda_val, dict) else {},
    )


def read_task_file(file_path: Path) -> tuple[Task | None, bool]:
    """Read a task from a sync file.

    Args:
        file_path: Path to the sync file.

    Returns:
        Tuple of (Task or None, is_deleted).
        If is_deleted is True, Task is None and the task should be deleted.

    Raises:
        ValueError: If file format is invalid.
    """
    content = file_path.read_text()
    data = json.loads(content)

    # Check for tombstone
    if data.get("deleted"):
        return None, True

    # Parse task from nested or flat format
    task_data = data.get("data", data)
    task = sync_dict_to_task(task_data)

    return task, False


def get_file_modified_time(file_path: Path) -> datetime:
    """Get the modified timestamp from a sync file.

    Reads the 'modified' field from the JSON rather than filesystem mtime.

    Args:
        file_path: Path to the sync file.

    Returns:
        Modified datetime.
    """
    content = file_path.read_text()
    data = json.loads(content)

    modified_str = data.get("modified")
    if modified_str:
        return parse_datetime(modified_str) or datetime.fromtimestamp(
            file_path.stat().st_mtime
        )

    return datetime.fromtimestamp(file_path.stat().st_mtime)


def scan_sync_dir(sync_dir: Path) -> list[Path]:
    """Scan the sync directory for task files.

    Args:
        sync_dir: Base sync directory.

    Returns:
        List of task file paths.
    """
    tasks_dir = sync_dir / "tasks"
    if not tasks_dir.exists():
        return []

    return list(tasks_dir.glob("*.json"))


def scan_changes_since(
    sync_dir: Path,
    since: datetime | None = None,
) -> list[Path]:
    """Find task files modified since a given time.

    Args:
        sync_dir: Base sync directory.
        since: Only return files modified after this time.

    Returns:
        List of modified task file paths.
    """
    all_files = scan_sync_dir(sync_dir)

    if since is None:
        return all_files

    changed: list[Path] = []
    for file_path in all_files:
        file_modified = get_file_modified_time(file_path)
        if file_modified > since:
            changed.append(file_path)

    return changed
