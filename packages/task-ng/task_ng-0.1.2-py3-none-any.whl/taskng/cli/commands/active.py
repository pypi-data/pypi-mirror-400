"""Active task command implementation."""

from datetime import datetime, timedelta

from rich.console import Console

from taskng.cli.output import is_json_mode, output_json
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def show_active(filter_args: list[str] | None = None) -> None:
    """Show currently active tasks.

    Args:
        filter_args: Optional filter expressions to limit which active tasks are shown.
    """
    db = Database()
    if not db.exists:
        console.print("[yellow]No active task[/yellow]")
        return

    repo = TaskRepository(db)

    # Build filters
    filters: list[Filter] = []
    parser = FilterParser()

    # Always include +ACTIVE filter
    filters.extend(parser.parse(["+ACTIVE"]))

    # Apply context filters
    current_context = get_current_context()
    if current_context:
        context_filters = get_context_filter(current_context)
        if context_filters:
            filters.extend(parser.parse(context_filters))

    # Apply user filters
    if filter_args:
        filters.extend(parser.parse(filter_args))

    # Get filtered tasks
    active_tasks = repo.list_filtered(filters)

    # Apply virtual tag filters if any
    if parser.has_virtual_filters(filters):
        all_tasks = repo.list_all()
        active_tasks = parser.apply_virtual_filters(active_tasks, filters, all_tasks)

    if not active_tasks:
        if is_json_mode():
            output_json([])
        else:
            console.print("[yellow]No active task[/yellow]")
        return

    # JSON output mode
    if is_json_mode():
        output_json([task.model_dump(mode="json") for task in active_tasks])
        return

    now = datetime.now()

    for task in active_tasks:
        # task.start is guaranteed non-None by the +ACTIVE filter
        start_time = task.start
        assert start_time is not None
        elapsed = now - start_time
        elapsed_str = _format_duration(elapsed)

        console.print(f"[cyan]{task.id}[/cyan]: {task.description}")

        if task.project:
            console.print(f"  Project: [blue]{task.project}[/blue]")

        started = start_time.strftime("%Y-%m-%d %H:%M")
        console.print(f"  Started: {started}")
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
