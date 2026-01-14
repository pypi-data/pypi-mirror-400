"""Done task command implementation."""

from datetime import datetime

import typer
from rich.console import Console

from taskng.core.dependencies import get_blocking_tasks
from taskng.core.filters import FilterParser
from taskng.core.hooks import run_on_complete_hooks
from taskng.core.models import TaskStatus
from taskng.core.recurrence import create_next_occurrence
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def complete_tasks_by_filter(
    filter_args: list[str],
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Mark tasks matching filter as completed.

    Args:
        filter_args: Filter expressions to match tasks.
        force: Skip confirmation prompt.
        dry_run: Preview changes without applying.
    """
    db = Database()
    if not db.exists:
        console.print("[red]No tasks found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)
    parser = FilterParser()

    # Parse and apply filters
    filters = parser.parse(filter_args)

    # Only pending tasks can be completed
    from taskng.core.filters import Filter

    filters.append(Filter("status", "eq", "pending"))

    # Get matching tasks
    tasks = repo.list_filtered(filters)

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

    if not tasks:
        console.print("[yellow]No matching tasks[/yellow]")
        return

    # Show tasks that will be affected
    console.print(f"\n[bold]Tasks to complete ({len(tasks)}):[/bold]")
    for task in tasks:
        desc = task.description[:50]
        console.print(f"  {task.id}: {desc}")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return

    # Confirm unless forced
    if not force:
        console.print("")
        confirm = typer.confirm(f"Complete {len(tasks)} task(s)?")
        if not confirm:
            console.print("[yellow]Cancelled[/yellow]")
            raise typer.Exit(0)

    # Complete the tasks
    task_ids = [task.id for task in tasks if task.id]
    complete_tasks(task_ids)


def complete_tasks(task_ids: list[int]) -> None:
    """Mark tasks as completed."""
    db = Database()
    if not db.exists:
        console.print("[red]No tasks found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)

    # Get all tasks for dependency checking
    all_tasks = repo.list_all()

    completed = []
    errors = []

    for task_id in task_ids:
        task = repo.get_by_id(task_id)

        if not task:
            errors.append(f"Task {task_id} not found")
            continue

        if task.status == TaskStatus.COMPLETED:
            errors.append(f"Task {task_id} already completed")
            continue

        # Check for blocking dependencies
        blocking = get_blocking_tasks(task, all_tasks)
        if blocking:
            blocking_ids = [str(t.id) for t in blocking]
            errors.append(f"Task {task_id} blocked by: {', '.join(blocking_ids)}")
            continue

        # Update task
        task.status = TaskStatus.COMPLETED
        task.end = datetime.now()
        repo.update(task)

        # Run on-complete hooks
        success, message = run_on_complete_hooks(task)
        if not success:
            console.print(f"[yellow]Warning:[/yellow] {message}")
        elif message:
            console.print(f"[dim]{message}[/dim]")

        completed.append(task)

        # Handle recurrence
        if task.recur:
            try:
                next_task = create_next_occurrence(task)
                saved_next = repo.add(next_task)
                due_str = saved_next.due.strftime("%Y-%m-%d") if saved_next.due else ""
                console.print(
                    f"  [cyan]Created next occurrence {saved_next.id} due {due_str}[/cyan]"
                )
            except ValueError as e:
                console.print(f"  [dim]{e}[/dim]")

    # Display results
    if completed:
        console.print(f"[green]Completed {len(completed)} task(s)[/green]")
        for task in completed:
            desc = task.description[:50]
            console.print(f"  [dim]✓[/dim] {task.id}: {desc}")

    for error in errors:
        console.print(f"[yellow]{error}[/yellow]")

    if not completed and errors:
        raise typer.Exit(1)
