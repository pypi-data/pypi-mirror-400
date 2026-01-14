"""Show task command implementation."""

from datetime import datetime, timedelta

import typer
from rich.console import Console, Group
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from taskng.cli.output import is_json_mode, output_json
from taskng.core.urgency import calculate_urgency
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def format_datetime(dt: datetime) -> str:
    """Format datetime for display."""
    now = datetime.now()
    delta = now - dt

    if delta.days == 0:
        return dt.strftime("%H:%M")
    elif delta.days == 1:
        return f"yesterday {dt.strftime('%H:%M')}"
    elif delta.days < 7:
        return dt.strftime("%A %H:%M")
    else:
        return dt.strftime("%Y-%m-%d %H:%M")


def show_task(task_id: int) -> None:
    """Show detailed task information."""
    db = Database()
    if not db.exists:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    repo = TaskRepository(db)
    task = repo.get_by_id(task_id)

    if not task:
        console.print(f"[red]Task {task_id} not found[/red]")
        raise typer.Exit(1)

    # JSON output mode
    if is_json_mode():
        output_json(task)
        return

    # Build info table
    table = Table(show_header=False, box=None, padding=(0, 1, 0, 0))
    table.add_column("Field", style="bold")
    table.add_column("Value")

    table.add_row("ID", f"[cyan]{task.id}[/cyan]")
    table.add_row("UUID", f"[dim]{task.uuid}[/dim]")
    table.add_row("Description", task.description)
    status_color = {"pending": "yellow", "completed": "green", "deleted": "red"}.get(
        task.status.value, "white"
    )
    table.add_row("Status", f"[{status_color}]{task.status.value}[/{status_color}]")

    # Calculate and show urgency
    urgency = calculate_urgency(task)
    table.add_row("Urgency", f"[yellow]{urgency:.2f}[/yellow]")

    if task.priority:
        color = {"H": "red", "M": "yellow", "L": "green"}[task.priority.value]
        table.add_row("Priority", f"[{color}]{task.priority.value}[/{color}]")

    if task.project:
        table.add_row("Project", f"[blue]{task.project}[/blue]")

    if task.tags:
        tags = " ".join(f"[magenta]+{t}[/magenta]" for t in task.tags)
        table.add_row("Tags", tags)

    # Dates
    table.add_row("Created", f"[cyan]{format_datetime(task.entry)}[/cyan]")
    table.add_row("Modified", f"[cyan]{format_datetime(task.modified)}[/cyan]")

    if task.due:
        table.add_row("Due", f"[cyan]{format_datetime(task.due)}[/cyan]")
    if task.scheduled:
        table.add_row("Scheduled", f"[cyan]{format_datetime(task.scheduled)}[/cyan]")
    if task.start:
        table.add_row("Started", f"[cyan]{format_datetime(task.start)}[/cyan]")
        # Show elapsed time for active task
        elapsed = datetime.now() - task.start
        elapsed_str = _format_duration(elapsed)
        table.add_row("Elapsed", f"[green]{elapsed_str}[/green]")

    # Recurrence
    if task.recur:
        table.add_row("Recur", f"[cyan]{task.recur}[/cyan]")
    if task.until:
        table.add_row("Until", f"[cyan]{format_datetime(task.until)}[/cyan]")

    # Build panel content with sections below table
    sections: list[Text] = []

    # Add annotations
    if task.annotations:
        sections.append(Text(""))
        sections.append(Text("Annotations", style="bold"))
        for i, ann in enumerate(task.annotations, 1):
            sections.append(Text(f"  [{i}] {ann['entry']}: {ann['description']}"))

    # Add dependencies
    if task.depends:
        deps = []
        for dep_uuid in task.depends:
            dep = repo.get_by_uuid(dep_uuid)
            if dep:
                deps.append(f"  [{dep.id}] {dep.description[:40]}")
        if deps:
            sections.append(Text(""))
            sections.append(Text("Dependencies", style="bold"))
            for dep_line in deps:
                sections.append(Text(dep_line))

    # Add UDAs
    if task.uda:
        sections.append(Text(""))
        sections.append(Text("Custom Attributes", style="bold"))
        for key, value in task.uda.items():
            sections.append(Text(f"  {key}: {value}"))

    # Add notes
    if task.notes:
        sections.append(Text(""))
        sections.append(Text("Notes", style="bold"))
        sections.append(Text(task.notes, style="italic"))

    # Build panel content
    if sections:
        panel_content: Group | Table = Group(table, *sections)
    else:
        panel_content = table

    # Wrap in panel
    panel = Panel(panel_content, title=f"Task {task.id}", border_style="blue")
    console.print(panel)


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
