"""Edit task command implementation."""

import os
import subprocess
import tempfile
from datetime import datetime
from typing import Any

import typer
import yaml  # type: ignore[import-untyped]
from rich.console import Console

from taskng.config.settings import get_config
from taskng.core.models import Priority, Task
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def get_editor() -> str:
    """Get the editor command from config or environment.

    Returns:
        Editor command string.
    """
    # Check config first
    config = get_config()
    editor = config.get("editor")
    if isinstance(editor, str):
        return editor

    # Fall back to environment variables
    return os.environ.get("VISUAL") or os.environ.get("EDITOR") or "vi"


def task_to_markdown(task: Task, show_info: bool = False) -> str:
    """Convert task to markdown with YAML frontmatter.

    Args:
        task: Task to convert.
        show_info: Whether to include read-only fields in frontmatter.

    Returns:
        Markdown representation for editing.
    """
    # Editable fields for frontmatter
    data: dict[str, Any] = {
        "description": task.description,
        "project": task.project,
        "priority": task.priority.value if task.priority else None,
        "tags": task.tags if task.tags else [],
        "due": task.due.strftime("%Y-%m-%d %H:%M") if task.due else None,
        "scheduled": task.scheduled.strftime("%Y-%m-%d %H:%M")
        if task.scheduled
        else None,
        "wait": task.wait.strftime("%Y-%m-%d %H:%M") if task.wait else None,
        "recur": task.recur,
        "until": task.until.strftime("%Y-%m-%d %H:%M") if task.until else None,
    }

    # Add UDAs
    if task.uda:
        data["uda"] = task.uda

    # Add read-only fields if requested
    if show_info:
        data["_id"] = task.id
        data["_uuid"] = task.uuid
        data["_status"] = task.status.value
        data["_created"] = task.entry.strftime("%Y-%m-%d %H:%M")
        data["_modified"] = task.modified.strftime("%Y-%m-%d %H:%M")
        if task.annotations:
            data["_annotations"] = [
                f"{ann['entry']}: {ann['description']}" for ann in task.annotations
            ]

    # Build markdown
    lines = [
        "---",
        yaml.dump(
            data, default_flow_style=False, allow_unicode=True, sort_keys=False
        ).rstrip(),
        "---",
        "",
    ]

    # Add notes content
    if task.notes:
        lines.append(task.notes)
    else:
        lines.append("<!-- Add notes here -->")

    return "\n".join(lines)


def parse_edited_markdown(text: str, task: Task) -> Task:
    """Parse edited markdown and update task.

    Args:
        text: Edited markdown content.
        task: Original task to update.

    Returns:
        Updated task.
    """
    from taskng.core.dates import parse_date
    from taskng.core.recurrence import parse_recurrence

    # Split frontmatter and content
    if not text.startswith("---"):
        raise ValueError("Invalid format: missing frontmatter")

    parts = text.split("---", 2)
    if len(parts) < 3:
        raise ValueError("Invalid format: incomplete frontmatter")

    frontmatter_text = parts[1].strip()
    notes_text = parts[2].strip()

    # Parse YAML frontmatter
    try:
        data = yaml.safe_load(frontmatter_text)
    except yaml.YAMLError as e:
        raise ValueError(f"Invalid YAML: {e}") from e

    if not data:
        return task

    # Apply updates from frontmatter
    if "description" in data and data["description"]:
        task.description = str(data["description"])

    if "project" in data:
        task.project = str(data["project"]) if data["project"] else None

    if "priority" in data:
        val = str(data["priority"]).upper() if data["priority"] else ""
        if val in ("H", "M", "L"):
            task.priority = Priority(val)
        else:
            task.priority = None

    if "tags" in data:
        if data["tags"]:
            if isinstance(data["tags"], list):
                task.tags = [str(t) for t in data["tags"]]
            else:
                task.tags = str(data["tags"]).split()
        else:
            task.tags = []

    if "due" in data:
        if data["due"]:
            task.due = parse_date(str(data["due"]))
        else:
            task.due = None

    if "scheduled" in data:
        if data["scheduled"]:
            task.scheduled = parse_date(str(data["scheduled"]))
        else:
            task.scheduled = None

    if "wait" in data:
        if data["wait"]:
            task.wait = parse_date(str(data["wait"]))
        else:
            task.wait = None

    # Handle recurrence
    if "recur" in data:
        if data["recur"]:
            recur_value = str(data["recur"])
            # Validate recurrence pattern
            if not parse_recurrence(recur_value):
                raise ValueError(f"Invalid recurrence pattern: {recur_value}")

            # Check that task has due date
            effective_due = (
                task.due
                if "due" not in data
                else (parse_date(str(data["due"])) if data.get("due") else None)
            )
            if not effective_due:
                raise ValueError(
                    "Recurring tasks require a due date. Set due field first."
                )

            task.recur = recur_value

            # Chain breaking: clear parent_uuid if modifying recurrence on child task
            if task.parent_uuid:
                task.parent_uuid = None
        else:
            # Clearing recurrence
            task.recur = None
            # Cascade: also clear until when clearing recur
            if task.until:
                task.until = None

    # Handle until date
    if "until" in data:
        if data["until"]:
            task.until = parse_date(str(data["until"]))
        else:
            task.until = None

    # Apply UDA updates
    if "uda" in data:
        if data["uda"] and isinstance(data["uda"], dict):
            task.uda = {str(k): str(v) for k, v in data["uda"].items() if v}
        else:
            task.uda = {}

    # Update notes (ignore placeholder comment)
    if notes_text and notes_text != "<!-- Add notes here -->":
        task.notes = notes_text
    else:
        task.notes = None

    task.modified = datetime.now()

    return task


def edit_task(task_id: int, show_info: bool = False) -> None:
    """Edit a task in external editor.

    Args:
        task_id: ID of task to edit.
        show_info: Whether to show read-only fields.
    """
    db = Database()
    if not db.exists:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    # Get editor
    editor = get_editor()

    # Create temp file with task content
    with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
        f.write(task_to_markdown(task, show_info))
        temp_path = f.name

    try:
        # Open editor
        result = subprocess.run([editor, temp_path])

        if result.returncode != 0:
            console.print(f"[red]Editor exited with code {result.returncode}[/red]")
            raise typer.Exit(1)

        # Read edited content
        with open(temp_path) as f:
            edited_text = f.read()

        # Parse and update task
        try:
            updated_task = parse_edited_markdown(edited_text, task)
        except ValueError as e:
            console.print(f"[red]Error parsing edit: {e}[/red]")
            raise typer.Exit(1) from e

        # Save changes
        repo.update(updated_task)

        console.print(f"[green]Task {task_id} updated[/green]")

    finally:
        # Clean up temp file
        os.unlink(temp_path)
