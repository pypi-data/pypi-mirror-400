"""Project rename command implementation."""

import typer
from rich.console import Console
from rich.prompt import Confirm

from taskng.cli.output import is_json_mode, output_json
from taskng.core.models import Task
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def rename_project(
    old_name: str,
    new_name: str,
    force: bool = False,
    dry_run: bool = False,
) -> None:
    """Rename a project and all its subprojects.

    Args:
        old_name: Current project name/prefix to rename.
        new_name: New project name/prefix.
        force: Skip confirmation prompt.
        dry_run: Preview changes without applying.
    """
    # Validate inputs
    if not old_name.strip():
        console.print("[red]Error:[/red] Old project name cannot be empty")
        raise typer.Exit(1)

    if not new_name.strip():
        console.print("[red]Error:[/red] New project name cannot be empty")
        raise typer.Exit(1)

    old_name = old_name.strip()
    new_name = new_name.strip()

    if old_name == new_name:
        console.print("[yellow]Old and new names are the same[/yellow]")
        return

    db = Database()
    if not db.exists:
        console.print("[yellow]No tasks found[/yellow]")
        return

    repo = TaskRepository(db)
    all_tasks = repo.list_all()

    # Find tasks to modify
    tasks_to_modify: list[
        tuple[Task, str, str]
    ] = []  # (task, old_project, new_project)

    for task in all_tasks:
        if task.project:
            if task.project == old_name:
                # Exact match
                new_project = new_name
                tasks_to_modify.append((task, task.project, new_project))
            elif task.project.startswith(f"{old_name}."):
                # Subproject match
                new_project = new_name + task.project[len(old_name) :]
                tasks_to_modify.append((task, task.project, new_project))

    if not tasks_to_modify:
        if is_json_mode():
            output_json({"modified": 0, "tasks": []})
        else:
            console.print(f"[yellow]No tasks found with project '{old_name}'[/yellow]")
        return

    # Show tasks that will be affected
    if is_json_mode():
        result = {
            "modified": len(tasks_to_modify) if not dry_run else 0,
            "tasks": [
                {
                    "id": task.id,
                    "description": task.description,
                    "old_project": old_project,
                    "new_project": new_project,
                }
                for task, old_project, new_project in tasks_to_modify
            ],
        }
        if not dry_run:
            # Apply changes
            for task, _, new_project in tasks_to_modify:
                task.project = new_project
                repo.update(task)
        output_json(result)
        return

    console.print(f"\n[yellow]Tasks to rename ({len(tasks_to_modify)}):[/yellow]")
    for task, old_project, new_project in tasks_to_modify:
        desc = (
            task.description[:40] + "..."
            if len(task.description) > 40
            else task.description
        )
        console.print(f"  {task.id}: {desc}")
        console.print(f"       [dim]{old_project}[/dim] → [cyan]{new_project}[/cyan]")

    if dry_run:
        console.print("\n[yellow]Dry run - no changes made[/yellow]")
        return

    # Confirm unless forced
    if not force:
        console.print("")
        if not Confirm.ask(f"Rename {len(tasks_to_modify)} task(s)?", default=False):
            console.print("[dim]Cancelled[/dim]")
            return

    # Apply changes
    for task, _, new_project in tasks_to_modify:
        task.project = new_project
        repo.update(task)

    console.print(f"\n[green]Renamed {len(tasks_to_modify)} task(s)[/green]")
