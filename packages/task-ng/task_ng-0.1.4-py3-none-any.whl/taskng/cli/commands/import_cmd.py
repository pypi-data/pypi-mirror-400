"""Import command implementation."""

from pathlib import Path

from rich.console import Console

from taskng.storage.database import Database
from taskng.storage.import_tw import TaskwarriorImporter
from taskng.storage.repository import TaskRepository

console = Console()


def import_tasks(file: Path, dry_run: bool = False) -> None:
    """Import tasks from JSON export file.

    Supports Taskwarrior export and Task-NG export/backup formats.

    Args:
        file: Path to JSON file.
        dry_run: If True, show what would be imported without importing.
    """
    if not file.exists():
        console.print(f"[red]File not found: {file}[/red]")
        return

    db = Database()
    db.initialize()
    repo = TaskRepository(db)

    importer = TaskwarriorImporter(repo)

    if dry_run:
        console.print("[dim]Dry run - no changes will be made[/dim]")

    result = importer.import_file(file, dry_run=dry_run)

    # Show detected format
    format_names = {
        "taskwarrior": "Taskwarrior",
        "taskwarrior-ndjson": "Taskwarrior (NDJSON)",
        "task-ng": "Task-NG",
        "task-ng-backup": "Task-NG backup",
        "unknown": "Unknown",
    }
    format_name = format_names.get(result.format_detected, result.format_detected)
    console.print(f"[dim]Format: {format_name}[/dim]")

    # Show results
    if result.imported > 0:
        action = "Would import" if dry_run else "Imported"
        console.print(f"[green]{action}: {result.imported} task(s)[/green]")

    if result.skipped > 0:
        console.print(f"[yellow]Skipped (duplicate): {result.skipped} task(s)[/yellow]")

    if result.failed > 0:
        console.print(f"[red]Failed: {result.failed} task(s)[/red]")
        for error in result.errors[:5]:
            console.print(f"  [dim]{error}[/dim]")
        if len(result.errors) > 5:
            console.print(f"  [dim]... and {len(result.errors) - 5} more errors[/dim]")

    if result.imported == 0 and result.skipped == 0 and result.failed == 0:
        console.print("[yellow]No tasks found in file[/yellow]")
