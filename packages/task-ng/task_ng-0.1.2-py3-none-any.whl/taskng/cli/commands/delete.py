"""Delete task command implementation."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from taskng.core.filters import Filter, FilterParser
from taskng.core.models import TaskStatus
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def delete_tasks_by_filter(
    filter_args: list[str],
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Delete tasks matching filter.

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

    # Only non-deleted tasks can be deleted
    filters.append(Filter("status", "ne", "deleted"))

    # Get matching tasks
    all_tasks = repo.list_all()
    tasks = repo.list_filtered(filters)

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

    if not tasks:
        console.print("[yellow]No matching tasks[/yellow]")
        return

    # Show tasks that will be affected
    console.print(f"\n[yellow]Tasks to delete ({len(tasks)}):[/yellow]")
    for task in tasks:
        desc = task.description[:50]
        console.print(f"  {task.id}: {desc}")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return

    # Confirm unless forced
    if not force:
        console.print("")
        if not Confirm.ask(f"Delete {len(tasks)} task(s)?", default=False):
            console.print("[dim]Cancelled[/dim]")
            return

    # Delete tasks
    for task in tasks:
        task.status = TaskStatus.DELETED
        repo.update(task)

    console.print(f"[green]Deleted {len(tasks)} task(s)[/green]")


def delete_tasks(task_ids: list[int], force: bool = False) -> None:
    """Soft delete tasks."""
    db = Database()
    if not db.exists:
        console.print("[red]No tasks found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)

    # Validate all tasks exist first
    tasks = []
    errors = []

    for task_id in task_ids:
        task = repo.get_by_id(task_id)
        if not task:
            errors.append(f"Task {task_id} not found")
            continue
        if task.status == TaskStatus.DELETED:
            errors.append(f"Task {task_id} already deleted")
            continue
        tasks.append(task)

    # Show errors
    for error in errors:
        console.print(f"[yellow]{error}[/yellow]")

    if not tasks:
        if errors:
            raise typer.Exit(1)
        return

    # Show tasks to be deleted
    console.print("[yellow]The following task(s) will be deleted:[/yellow]")
    for task in tasks:
        desc = task.description[:50]
        console.print(f"  {task.id}: {desc}")

    # Confirm unless forced
    if not force and not Confirm.ask("Delete these tasks?", default=False):
        console.print("[dim]Cancelled[/dim]")
        return

    # Delete tasks
    for task in tasks:
        task.status = TaskStatus.DELETED
        repo.update(task)

    console.print(f"[green]Deleted {len(tasks)} task(s)[/green]")
