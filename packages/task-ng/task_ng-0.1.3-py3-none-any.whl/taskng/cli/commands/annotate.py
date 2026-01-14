"""Annotate command for Task-NG."""

import typer
from rich.console import Console

from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def annotate_task(task_id: int, text: str) -> None:
    """Add annotation to task.

    Args:
        task_id: Task ID to annotate.
        text: Annotation text.
    """
    db = Database()
    if not db.exists:
        console.print(f"[red]Error:[/red] Task {task_id} not found")
        raise typer.Exit(1)

    repo = TaskRepository(db)

    task = repo.get_by_id(task_id)
    if not task:
        console.print(f"[red]Error:[/red] Task {task_id} not found")
        raise typer.Exit(1)

    task.add_annotation(text)
    repo.update(task)

    console.print(f"[green]Annotated task {task_id}[/green]")
    console.print(f"  {text}")


def denotate_task(task_id: int, index: int) -> None:
    """Remove annotation from task.

    Args:
        task_id: Task ID.
        index: Annotation index to remove (1-based).
    """
    db = Database()
    if not db.exists:
        console.print(f"[red]Error:[/red] Task {task_id} not found")
        raise typer.Exit(1)

    repo = TaskRepository(db)

    task = repo.get_by_id(task_id)
    if not task:
        console.print(f"[red]Error:[/red] Task {task_id} not found")
        raise typer.Exit(1)

    if index < 1 or index > len(task.annotations):
        console.print(f"[red]Error:[/red] Invalid annotation index {index}")
        console.print(f"Task has {len(task.annotations)} annotation(s)")
        raise typer.Exit(1)

    removed = task.annotations[index - 1]
    task.remove_annotation(index - 1)
    repo.update(task)

    console.print(f"[green]Removed annotation from task {task_id}[/green]")
    console.print(f"  {removed['description']}")
