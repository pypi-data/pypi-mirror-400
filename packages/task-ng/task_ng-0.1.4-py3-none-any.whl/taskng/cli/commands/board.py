"""Kanban board view command implementation."""

from datetime import datetime

from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text

from taskng.cli.output import is_json_mode, output_json
from taskng.core.boards import (
    BoardDefinition,
    BoardDisabledError,
    BoardNotFoundError,
    get_board,
    list_boards,
)
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.dates import parse_duration
from taskng.core.filters import FilterParser
from taskng.core.models import Task
from taskng.core.sorting import sort_tasks
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def get_tasks_by_column(
    tasks: list[Task], board: BoardDefinition
) -> dict[str, list[Task]]:
    """Group tasks into columns based on column filters.

    Args:
        tasks: All tasks to distribute.
        board: Board definition with column filters.

    Returns:
        Dictionary mapping column name to list of tasks.
    """
    by_column: dict[str, list[Task]] = {}
    parser = FilterParser()
    now = datetime.now()

    for col in board.columns:
        # Parse column filters
        filters = parser.parse(col.filter)

        # Apply filters to tasks
        column_tasks = [t for t in tasks if parser.matches_task(t, filters, tasks)]

        # Apply time window filter if specified
        if col.since:
            duration = parse_duration(col.since)
            if duration:
                cutoff = now - duration
                column_tasks = [
                    t
                    for t in column_tasks
                    if t.end and t.end >= cutoff  # For completed tasks
                ]

        # Sort tasks
        if board.sort:
            column_tasks = sort_tasks(column_tasks, board.sort)

        # Apply limit
        limit = col.limit if col.limit is not None else board.limit
        if limit is not None:
            by_column[col.name] = column_tasks[:limit]
        else:
            by_column[col.name] = column_tasks

    return by_column


def format_card(
    task: Task,
    fields: list[str],
    now: datetime,
) -> Text:
    """Format a task as a card for the board.

    Args:
        task: Task to format.
        fields: Fields to display on the card.
        now: Current datetime for due date comparison.

    Returns:
        Formatted Rich Text for the card.
    """
    text = Text()

    # Determine card style based on priority and due
    if task.due and task.due < now:
        base_style = Style(color="red")
    elif task.priority and task.priority.value == "H":
        base_style = Style(color="yellow")
    elif task.priority and task.priority.value == "M":
        base_style = Style(color="cyan")
    else:
        base_style = Style()

    # Build first line: ID + priority + description
    task_id = str(task.id) if task.id else "?"

    # Add ID in dim style
    text.append(task_id, style="dim")
    text.append(" ")
    # Add priority if present
    if task.priority:
        text.append(f"[{task.priority.value}] ", style=base_style)
    text.append(task.description, style=base_style)

    # Add additional fields
    for field in fields:
        if field in ("id", "description", "priority"):
            # Already handled above
            continue
        elif field == "due":
            if task.due:
                due_str = task.due.strftime("%b %d")
                text.append(f"\nDue: {due_str}", style=base_style)
        elif field == "tags":
            if task.tags:
                tags_str = " ".join(task.tags)
                text.append(f"\n{tags_str}", style=base_style)
        elif field == "project" and task.project:
            text.append(f"\n{task.project}", style=base_style)

    return text


def render_board(board: BoardDefinition, tasks: list[Task]) -> Table:
    """Render a Kanban board as a Rich table.

    Args:
        board: Board definition.
        tasks: All tasks to display.

    Returns:
        Rich Table with board view.
    """
    now = datetime.now()

    # Get tasks grouped by column
    tasks_by_column = get_tasks_by_column(tasks, board)

    # Count total tasks per column (before limit)
    total_counts: dict[str, int] = {}
    parser = FilterParser()
    for col in board.columns:
        filters = parser.parse(col.filter)
        column_tasks = [t for t in tasks if parser.matches_task(t, filters, tasks)]
        total_counts[col.name] = len(column_tasks)

    # Create table
    title = board.description if board.description else f"{board.name} Board"
    table = Table(
        title=f"[bold cyan]{title}[/bold cyan]",
        show_header=True,
        header_style="bold",
        box=box.SIMPLE_HEAD,
        padding=(0, 1),
        expand=True,
    )

    # Calculate dynamic column width based on terminal size
    terminal_width = console.width or 80
    num_columns = len(board.columns)
    # Account for padding (2 chars per column) and borders
    available_width = terminal_width - (num_columns * 3)
    col_width = max(available_width // num_columns, board.column_width)

    # Alternating subtle background colors for columns
    column_backgrounds = ["", "on grey15"]

    # Add columns
    for i, col in enumerate(board.columns):
        count = len(tasks_by_column.get(col.name, []))
        total = total_counts.get(col.name, 0)
        if total > count:
            header = f"{col.name} ({count}/{total})"
        else:
            header = f"{col.name} ({count})"

        # Add WIP limit warning
        bg_style = column_backgrounds[i % len(column_backgrounds)]
        header_style = f"bold {bg_style}"
        if col.wip_limit and total > col.wip_limit:
            header = f"{header} [WIP:{col.wip_limit}]"
            header_style = f"bold yellow {bg_style}"

        table.add_column(
            header,
            justify="left",
            width=col_width,
            no_wrap=False,
            overflow="fold",
            header_style=header_style,
            style=bg_style,
        )

    # Build single row with all tasks per column
    row = []
    for col in board.columns:
        col_tasks = tasks_by_column.get(col.name, [])
        if col_tasks:
            # Format all cards for this column
            cell_content = Text()
            for i, task in enumerate(col_tasks):
                if i > 0:
                    cell_content.append("\n\n")  # Empty line between tasks
                card = format_card(task, board.card_fields, now)
                cell_content.append_text(card)
            row.append(cell_content)
        else:
            row.append(Text(""))
    table.add_row(*row)

    return table


def show_board(
    name: str = "default",
    filter_args: list[str] | None = None,
) -> None:
    """Display a Kanban board.

    Args:
        name: Board name to display.
        filter_args: Additional filter expressions.
    """
    # Load board definition
    try:
        board = get_board(name)
    except (BoardNotFoundError, BoardDisabledError) as e:
        console.print(f"[red]Error:[/red] {e}")
        return

    # Get tasks
    db = Database()
    if not db.exists:
        console.print("[yellow]No tasks found[/yellow]")
        table = render_board(board, [])
        console.print(table)
        return

    repo = TaskRepository(db)
    all_tasks = repo.list_all()
    parser = FilterParser()

    # Apply context filters first
    tasks = all_tasks
    current_context = get_current_context()
    if current_context:
        context_filters = get_context_filter(current_context)
        if context_filters:
            filters = parser.parse(context_filters)
            tasks = [t for t in tasks if parser.matches_task(t, filters, all_tasks)]

    # Apply global board filter
    if board.filter:
        filters = parser.parse(board.filter)
        tasks = [t for t in tasks if parser.matches_task(t, filters, all_tasks)]

    # Apply additional filters from command line
    if filter_args:
        filters = parser.parse(filter_args)
        tasks = [t for t in tasks if parser.matches_task(t, filters, all_tasks)]

    # JSON output mode
    if is_json_mode():
        tasks_by_column = get_tasks_by_column(tasks, board)
        json_data = {
            "board": board.name,
            "description": board.description,
            "columns": [
                {
                    "name": col.name,
                    "count": len(tasks_by_column.get(col.name, [])),
                    "wip_limit": col.wip_limit,
                    "tasks": [
                        {
                            "id": t.id,
                            "uuid": t.uuid,
                            "description": t.description,
                            "status": t.status.value if t.status else None,
                            "priority": t.priority.value if t.priority else None,
                            "project": t.project,
                            "tags": t.tags,
                            "due": t.due.isoformat() if t.due else None,
                        }
                        for t in tasks_by_column.get(col.name, [])
                    ],
                }
                for col in board.columns
            ],
        }
        output_json(json_data)
        return

    # Render and display
    table = render_board(board, tasks)
    console.print(table)

    # Show legend
    console.print()
    console.print(
        "[dim]Legend:[/dim] "
        "[red]overdue[/red]  "
        "[yellow]high priority[/yellow]  "
        "[cyan]medium priority[/cyan]"
    )


def show_boards() -> None:
    """Display list of available boards."""
    boards = list_boards()

    if not boards:
        console.print("[yellow]No boards defined[/yellow]")
        return

    table = Table(
        title="[bold]Available Boards[/bold]",
        show_header=True,
        header_style="bold",
        box=box.SIMPLE,
    )

    table.add_column("Name", style="cyan")
    table.add_column("Description")

    for name in boards:
        try:
            board = get_board(name)
            table.add_row(name, board.description or "")
        except BoardNotFoundError:
            table.add_row(name, "[dim]Error loading[/dim]")

    console.print(table)
