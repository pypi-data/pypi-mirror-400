"""Start time tracking command implementation."""

from datetime import datetime, timedelta

import typer
from rich.console import Console

from taskng.core.filters import FilterParser
from taskng.core.models import TaskStatus
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def start_task(task_id: int) -> None:
    """Start time tracking for a task.

    Args:
        task_id: ID of task to start.
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

    if task.status != TaskStatus.PENDING:
        console.print(f"[red]Task {task_id} is not pending[/red]")
        raise typer.Exit(1)

    if task.start:
        console.print(f"[yellow]Task {task_id} is already active[/yellow]")
        started = task.start.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Started: {started}")
        return

    # Check if another task is already active using +ACTIVE filter
    parser = FilterParser()
    filters = parser.parse(["+ACTIVE"])
    active_tasks = repo.list_filtered(filters)

    # Apply virtual tag filter
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        active_tasks = parser.apply_virtual_filters(active_tasks, filters, all_tasks)

    # Exclude the current task
    active_tasks = [t for t in active_tasks if t.id != task_id]

    if active_tasks:
        active = active_tasks[0]
        console.print(f"[yellow]Warning:[/yellow] Task {active.id} is already active")
        console.print(f"  {active.description[:50]}")
        console.print("  Stop it first or use --force to switch")
        raise typer.Exit(1)

    # Start the task
    task.start = datetime.now()
    task.modified = datetime.now()
    repo.update(task)

    console.print(f"Started task [cyan]{task_id}[/cyan]")
    console.print(f"  {task.description}")


def start_task_force(task_id: int) -> None:
    """Start task, stopping any currently active task.

    Args:
        task_id: ID of task to start.
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

    if task.status != TaskStatus.PENDING:
        console.print(f"[red]Task {task_id} is not pending[/red]")
        raise typer.Exit(1)

    # Stop any currently active tasks using +ACTIVE filter
    parser = FilterParser()
    filters = parser.parse(["+ACTIVE"])
    active_tasks = repo.list_filtered(filters)

    # Apply virtual tag filter
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        active_tasks = parser.apply_virtual_filters(active_tasks, filters, all_tasks)

    # Stop all active tasks except the one we're starting
    for t in active_tasks:
        if t.id != task_id:
            # t.start is guaranteed non-None by +ACTIVE filter
            assert t.start is not None
            elapsed = datetime.now() - t.start
            t.start = None
            t.modified = datetime.now()
            repo.update(t)
            console.print(
                f"Stopped task [cyan]{t.id}[/cyan] ({_format_duration(elapsed)})"
            )

    # Start the task
    task.start = datetime.now()
    task.modified = datetime.now()
    repo.update(task)

    console.print(f"Started task [cyan]{task_id}[/cyan]")
    console.print(f"  {task.description}")


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
