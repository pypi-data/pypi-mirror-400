"""Export tasks for sync operations.

This module provides serialization of Task objects to JSON for sync.
Unlike the CLI export, this includes all fields for proper merging.
"""

import json
from datetime import datetime
from pathlib import Path

from taskng.core.models import Task


def task_to_sync_dict(task: Task) -> dict[str, object]:
    """Convert a task to a dictionary for sync.

    Unlike CLI export, this includes ALL fields for proper sync/merge.

    Args:
        task: Task to convert.

    Returns:
        Dictionary representation suitable for sync.
    """
    data: dict[str, object] = {
        # Required fields
        "uuid": task.uuid,
        "description": task.description,
        "status": task.status.value,
        "entry": task.entry.isoformat(),
        "modified": task.modified.isoformat(),
        # Optional scalar fields (always include for merge)
        "id": task.id,
        "priority": task.priority.value if task.priority else None,
        "project": task.project,
        "due": task.due.isoformat() if task.due else None,
        "scheduled": task.scheduled.isoformat() if task.scheduled else None,
        "wait": task.wait.isoformat() if task.wait else None,
        "until": task.until.isoformat() if task.until else None,
        "start": task.start.isoformat() if task.start else None,
        "end": task.end.isoformat() if task.end else None,
        "recur": task.recur,
        "parent_uuid": task.parent_uuid,
        "notes": task.notes,
        "urgency": round(task.urgency, 2),
        # List/dict fields (always include for merge)
        "tags": task.tags,
        "depends": task.depends,
        "annotations": [
            {"entry": ann.get("entry", ""), "description": ann.get("description", "")}
            for ann in task.annotations
        ],
        "uda": task.uda,
    }

    return data


def sync_dict_to_json(data: dict[str, object], pretty: bool = True) -> str:
    """Convert sync dictionary to JSON string.

    Args:
        data: Task dictionary.
        pretty: If True, format with indentation for readability.

    Returns:
        JSON string.
    """
    if pretty:
        return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True)
    return json.dumps(data, ensure_ascii=False)


def write_task_file(task: Task, sync_dir: Path) -> Path:
    """Write a task to its sync file.

    Args:
        task: Task to write.
        sync_dir: Base sync directory.

    Returns:
        Path to the written file.
    """
    tasks_dir = sync_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    file_path = tasks_dir / f"{task.uuid}.json"
    data = task_to_sync_dict(task)

    # Add sync metadata
    sync_data = {
        "version": 1,
        "uuid": task.uuid,
        "modified": task.modified.isoformat(),
        "data": data,
    }

    file_path.write_text(sync_dict_to_json(sync_data))
    return file_path


def write_tombstone(uuid: str, sync_dir: Path) -> Path:
    """Write a tombstone file for a deleted task.

    Tombstones mark tasks that have been deleted so the deletion
    propagates to other devices.

    Args:
        uuid: UUID of the deleted task.
        sync_dir: Base sync directory.

    Returns:
        Path to the tombstone file.
    """
    tasks_dir = sync_dir / "tasks"
    tasks_dir.mkdir(parents=True, exist_ok=True)

    file_path = tasks_dir / f"{uuid}.json"
    tombstone = {
        "version": 1,
        "uuid": uuid,
        "modified": datetime.now().isoformat(),
        "deleted": True,
        "data": None,
    }

    file_path.write_text(sync_dict_to_json(tombstone))
    return file_path


def export_tasks_to_sync_dir(
    tasks: list[Task],
    sync_dir: Path,
    deleted_uuids: list[str] | None = None,
) -> tuple[int, int]:
    """Export multiple tasks to the sync directory.

    Args:
        tasks: Tasks to export.
        sync_dir: Base sync directory.
        deleted_uuids: UUIDs of deleted tasks (for tombstones).

    Returns:
        Tuple of (tasks_written, tombstones_written).
    """
    tasks_written = 0
    tombstones_written = 0

    for task in tasks:
        write_task_file(task, sync_dir)
        tasks_written += 1

    if deleted_uuids:
        for uuid in deleted_uuids:
            write_tombstone(uuid, sync_dir)
            tombstones_written += 1

    return tasks_written, tombstones_written
