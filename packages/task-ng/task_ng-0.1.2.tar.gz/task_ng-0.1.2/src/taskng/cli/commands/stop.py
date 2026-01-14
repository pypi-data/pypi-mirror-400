"""Stop time tracking command implementation."""

from datetime import datetime, timedelta

import typer
from rich.console import Console

from taskng.core.filters import FilterParser
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def stop_task(task_id: int | None = None) -> None:
    """Stop time tracking for a task.

    Args:
        task_id: ID of task to stop (or None to stop active task).
    """
    db = Database()
    if not db.exists:
        console.print("[red]No tasks found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)

    if task_id:
        task = repo.get_by_id(task_id)
        if not task:
            console.print(f"[red]Task {task_id} not found[/red]")
            raise typer.Exit(1)
    else:
        # Find active task using +ACTIVE filter
        parser = FilterParser()
        filters = parser.parse(["+ACTIVE"])
        active_tasks = repo.list_filtered(filters)

        # Apply virtual tag filter
        if parser.has_virtual_filters(filters):
            all_tasks = repo.list_all()
            active_tasks = parser.apply_virtual_filters(
                active_tasks, filters, all_tasks
            )

        if not active_tasks:
            console.print("[yellow]No active task[/yellow]")
            return

        task = active_tasks[0]

    if not task.start:
        console.print(f"[yellow]Task {task.id} is not active[/yellow]")
        return

    # Calculate elapsed time
    elapsed = datetime.now() - task.start
    elapsed_str = _format_duration(elapsed)

    # Stop the task
    task.start = None
    task.modified = datetime.now()
    repo.update(task)

    console.print(f"Stopped task [cyan]{task.id}[/cyan]")
    console.print(f"  {task.description}")
    console.print(f"  Elapsed: [green]{elapsed_str}[/green]")


def _format_duration(delta: timedelta) -> str:
    """Format timedelta as human-readable string."""
    total_seconds = int(delta.total_seconds())
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if hours > 0:
        return f"{hours}h {minutes}m"
    elif minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"
