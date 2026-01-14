"""Export command implementation."""

import json
from datetime import datetime
from pathlib import Path

from rich.console import Console

from taskng.cli.output import is_json_mode
from taskng.core.filters import FilterParser
from taskng.core.models import Task
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def task_to_dict(task: Task) -> dict[str, object]:
    """Convert a task to a dictionary for export.

    Args:
        task: Task to convert.

    Returns:
        Dictionary representation of the task.
    """
    data: dict[str, object] = {
        "uuid": task.uuid,
        "description": task.description,
        "status": task.status.value if task.status else None,
        "entry": task.entry.isoformat() if task.entry else None,
        "modified": task.modified.isoformat() if task.modified else None,
    }

    # Optional fields
    if task.id is not None:
        data["id"] = task.id
    if task.priority:
        data["priority"] = task.priority.value
    if task.project:
        data["project"] = task.project
    if task.due:
        data["due"] = task.due.isoformat()
    if task.scheduled:
        data["scheduled"] = task.scheduled.isoformat()
    if task.wait:
        data["wait"] = task.wait.isoformat()
    if task.until:
        data["until"] = task.until.isoformat()
    if task.start:
        data["start"] = task.start.isoformat()
    if task.end:
        data["end"] = task.end.isoformat()
    if task.recur:
        data["recur"] = task.recur
    if task.parent_uuid:
        data["parent"] = task.parent_uuid
    if task.tags:
        data["tags"] = task.tags
    if task.depends:
        data["depends"] = task.depends
    if task.annotations:
        data["annotations"] = [
            {"entry": ann.get("entry", ""), "description": ann.get("description", "")}
            for ann in task.annotations
        ]
    if task.uda:
        data["uda"] = task.uda
    if task.urgency:
        data["urgency"] = round(task.urgency, 2)

    return data


def export_tasks(
    output: Path | None = None,
    filter_args: list[str] | None = None,
    include_completed: bool = False,
    include_deleted: bool = False,
) -> None:
    """Export tasks to JSON format.

    Args:
        output: Output file path (stdout if None).
        filter_args: Filter expressions to select tasks.
        include_completed: Include completed tasks.
        include_deleted: Include deleted tasks.
    """
    db = Database()
    if not db.exists:
        if is_json_mode() or output:
            print("[]")
        else:
            console.print("[yellow]No tasks to export[/yellow]")
        return

    repo = TaskRepository(db)

    # Get tasks based on filters
    if filter_args:
        parser = FilterParser()
        filters = parser.parse(filter_args)
        tasks = repo.list_filtered(filters)
    else:
        tasks = repo.list_all()

    # Filter by status if needed
    if not include_completed:
        tasks = [t for t in tasks if t.status.value != "completed"]
    if not include_deleted:
        tasks = [t for t in tasks if t.status.value != "deleted"]

    # Convert to export format
    export_data = [task_to_dict(task) for task in tasks]

    # Output
    json_output = json.dumps(export_data, indent=2, ensure_ascii=False)

    if output:
        output.write_text(json_output)
        if not is_json_mode():
            console.print(f"[green]✓[/green] Exported {len(tasks)} tasks to {output}")
    else:
        print(json_output)


def export_backup(
    output: Path,
) -> None:
    """Create a full database backup.

    Args:
        output: Output file path.
    """
    db = Database()
    if not db.exists:
        console.print("[yellow]No database to backup[/yellow]")
        return

    repo = TaskRepository(db)

    # Get all tasks including completed and deleted
    tasks = repo.list_all()

    # Convert to export format
    export_data = {
        "version": "1.0",
        "exported": datetime.now().isoformat(),
        "task_count": len(tasks),
        "tasks": [task_to_dict(task) for task in tasks],
    }

    # Write backup
    json_output = json.dumps(export_data, indent=2, ensure_ascii=False)
    output.write_text(json_output)

    console.print(f"[green]✓[/green] Backup created: {output}")
    console.print(f"  Tasks: {len(tasks)}")
