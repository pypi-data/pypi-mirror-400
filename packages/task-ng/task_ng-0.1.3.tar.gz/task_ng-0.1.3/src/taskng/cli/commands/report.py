"""Report command for Task-NG."""

from datetime import datetime

import typer
from rich.console import Console
from rich.table import Table

from taskng.cli.display import get_row_style
from taskng.cli.output import is_json_mode, output_json
from taskng.config.settings import get_config
from taskng.core.filters import FilterParser
from taskng.core.models import Task
from taskng.core.reports import ReportDisabledError, get_report, list_reports
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def format_column_value(task: Task, column: str) -> str:
    """Format a task attribute for display.

    Args:
        task: Task to get value from.
        column: Column name.

    Returns:
        Formatted string value.
    """
    if column == "id":
        return str(task.id) if task.id else ""
    elif column == "uuid":
        return task.uuid[:8]
    elif column == "description":
        desc = task.description
        if len(desc) > 50:
            desc = desc[:47] + "..."
        return desc
    elif column == "status":
        return task.status.value
    elif column == "priority":
        if task.priority:
            pri_color = {"H": "red", "M": "yellow", "L": "green"}.get(
                task.priority.value, ""
            )
            return f"[{pri_color}]{task.priority.value}[/{pri_color}]"
        return ""
    elif column == "project":
        return task.project or ""
    elif column == "tags":
        if task.tags:
            tags = " ".join(f"+{t}" for t in task.tags[:3])
            if len(task.tags) > 3:
                tags += f" +{len(task.tags) - 3}"
            return tags
        return ""
    elif column == "due":
        if task.due:
            return format_date_relative(task.due)
        return ""
    elif column == "scheduled":
        if task.scheduled:
            return format_date_relative(task.scheduled)
        return ""
    elif column == "wait":
        if task.wait:
            return format_date_relative(task.wait)
        return ""
    elif column == "end":
        if task.end:
            return task.end.strftime("%Y-%m-%d")
        return ""
    elif column == "entry":
        return task.entry.strftime("%Y-%m-%d")
    elif column == "recur":
        return task.recur or ""
    elif column == "depends":
        if task.depends:
            return ", ".join(d[:8] for d in task.depends)
        return ""
    elif column == "urgency":
        return f"{task.urgency:.1f}"
    else:
        # Check UDAs
        return task.uda.get(column, "")


def format_date_relative(dt: datetime) -> str:
    """Format date with color based on urgency."""
    now = datetime.now()
    delta = dt - now
    days = delta.days

    if days < 0:
        return f"[red]{-days}d ago[/red]"
    elif days == 0:
        return "[red]today[/red]"
    elif days == 1:
        return "[yellow]tomorrow[/yellow]"
    elif days <= 7:
        return f"[yellow]{days}d[/yellow]"
    else:
        return f"{days}d"


def get_column_style(column: str) -> str:
    """Get Rich style for a column."""
    styles = {
        "id": "cyan",
        "project": "blue",
        "tags": "magenta",
        "status": "dim",
    }
    return styles.get(column, "")


def get_column_width(column: str) -> int | None:
    """Get width for a column."""
    widths = {
        "id": 4,
        "priority": 3,
        "due": 10,
        "scheduled": 10,
        "wait": 10,
        "end": 10,
        "entry": 10,
        "urgency": 6,
    }
    return widths.get(column)


def sort_tasks(tasks: list[Task], sort_spec: list[str]) -> list[Task]:
    """Sort tasks by sort specification.

    Args:
        tasks: Tasks to sort.
        sort_spec: List of sort specs like ["urgency-", "due+"].

    Returns:
        Sorted tasks.
    """
    if not sort_spec:
        return tasks

    from typing import Any

    def get_sort_key(task: Task) -> tuple[Any, ...]:
        keys = []
        for spec in sort_spec:
            if spec.endswith("-"):
                field = spec[:-1]
                reverse = True
            elif spec.endswith("+"):
                field = spec[:-1]
                reverse = False
            else:
                field = spec
                reverse = False

            value = getattr(task, field, None)

            # Handle None values
            sort_val: tuple[int, int | float | str]
            if value is None:
                # Put None values at the end
                sort_val = (1, 0)
            elif isinstance(value, datetime):
                sort_val = (0, value.timestamp() if not reverse else -value.timestamp())
            elif isinstance(value, str):
                sort_val = (
                    0,
                    value
                    if not reverse
                    else "".join(chr(255 - ord(c)) for c in value[:20]),
                )
            else:
                sort_val = (0, -value if reverse else value)

            keys.append(sort_val)
        return tuple(keys)

    return sorted(tasks, key=get_sort_key)


def run_report(name: str, extra_filters: list[str] | None = None) -> None:
    """Run a named report.

    Args:
        name: Report name.
        extra_filters: Additional filters to apply.
    """
    config = get_config()

    try:
        report = get_report(name, {"report": config.get("report", {})})
    except ReportDisabledError:
        console.print(f"[red]Error:[/red] Report '{name}' is disabled")
        console.print(
            "Enable it in your config or use 'task-ng reports' to see available reports."
        )
        raise typer.Exit(1) from None

    if not report:
        console.print(f"[red]Error:[/red] Unknown report: {name}")
        console.print("Use 'task-ng reports' to see available reports.")
        raise typer.Exit(1)

    db = Database()
    if not db.exists:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No tasks found.[/yellow]")
        return

    repo = TaskRepository(db)

    # Combine report filter with extra filters
    all_filters = list(report.filter)
    if extra_filters:
        all_filters.extend(extra_filters)

    # Parse and apply filters
    parser = FilterParser()
    filters = parser.parse(all_filters) if all_filters else []

    tasks = repo.list_filtered(filters) if filters else repo.list_all()

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

    # Sort tasks
    tasks = sort_tasks(tasks, report.sort)

    # Apply limit
    if report.limit:
        tasks = tasks[: report.limit]

    # JSON output
    if is_json_mode():
        output_json(tasks)
        return

    if not tasks:
        console.print(f"[yellow]No tasks match report '{name}'[/yellow]")
        return

    # Create table
    table = Table(
        title=f"{report.description} ({len(tasks)})",
        show_header=True,
        header_style="bold blue",
    )

    # Add columns
    for col in report.columns:
        style = get_column_style(col)
        width = get_column_width(col)
        table.add_column(col.capitalize(), style=style, width=width)

    # Add rows
    for i, task in enumerate(tasks):
        row = [format_column_value(task, col) for col in report.columns]
        table.add_row(*row, style=get_row_style(i))

    console.print(table)
    console.print(f"\n[dim]{len(tasks)} tasks[/dim]")


def show_reports() -> None:
    """Show available reports."""
    config = get_config()
    reports = list_reports({"report": config.get("report", {})})

    if is_json_mode():
        output_json([{"name": r.name, "description": r.description} for r in reports])
        return

    table = Table(title="Available Reports")
    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for report in reports:
        table.add_row(report.name, report.description)

    console.print(table)
