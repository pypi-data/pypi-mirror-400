"""Calendar view command implementation."""

import calendar
from datetime import datetime, timedelta

from rich import box
from rich.console import Console
from rich.style import Style
from rich.table import Table
from rich.text import Text

from taskng.cli.output import is_json_mode, output_json
from taskng.config.settings import get_config
from taskng.core.context import get_context_filter, get_current_context
from taskng.core.filters import Filter, FilterParser
from taskng.core.models import Task, TaskStatus
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()

# Day name to calendar module value mapping
DAY_NAME_TO_NUM = {
    "monday": 0,
    "tuesday": 1,
    "wednesday": 2,
    "thursday": 3,
    "friday": 4,
    "saturday": 5,
    "sunday": 6,
}

# Day names in order starting from Monday
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def get_weekstart() -> int:
    """Get the configured first day of week.

    Returns:
        Calendar module day value (0=Monday, 6=Sunday).
    """
    config = get_config()
    weekstart = config.get("calendar.weekstart", "monday")
    return DAY_NAME_TO_NUM.get(weekstart.lower(), 0)


def get_day_names(firstweekday: int) -> list[str]:
    """Get day names in order starting from the given first day.

    Args:
        firstweekday: Calendar module day value (0=Monday, 6=Sunday).

    Returns:
        List of 7 day name abbreviations.
    """
    return DAY_NAMES[firstweekday:] + DAY_NAMES[:firstweekday]


def get_tasks_by_date(
    tasks: list[Task], year: int, month: int
) -> dict[int, list[Task]]:
    """Group tasks by their due date day.

    Args:
        tasks: List of tasks to group.
        year: Year to filter by.
        month: Month to filter by.

    Returns:
        Dictionary mapping day number to list of tasks.
    """
    by_date: dict[int, list[Task]] = {}

    for task in tasks:
        if task.due and task.due.year == year and task.due.month == month:
            day = task.due.day
            if day not in by_date:
                by_date[day] = []
            by_date[day].append(task)

    return by_date


def _parse_style(style_string: str) -> Style:
    """Parse style string into Rich Style.

    Args:
        style_string: Style like "black on white" or "red bold".

    Returns:
        Rich Style object.
    """
    if not style_string or style_string == "default":
        return Style()

    parts = style_string.split()
    color = None
    bgcolor = None
    bold = True  # Always bold for today

    i = 0
    while i < len(parts):
        if parts[i] == "on" and i + 1 < len(parts):
            bgcolor = parts[i + 1]
            i += 2
        elif parts[i] == "bold":
            bold = True
            i += 1
        else:
            color = parts[i]
            i += 1

    return Style(color=color, bgcolor=bgcolor, bold=bold)


def format_day_cell(
    day: int,
    tasks: list[Task],
    is_today: bool,
    now: datetime,
    max_tasks: int = 2,
    title_width: int = 18,
) -> Text:
    """Format a calendar day cell.

    Args:
        day: Day number (0 for empty cell).
        tasks: Tasks due on this day.
        is_today: Whether this is today.
        now: Current datetime.
        max_tasks: Maximum tasks to show per cell.
        title_width: Width for task titles.

    Returns:
        Formatted Rich Text for the cell.
    """
    if day == 0:
        # Empty cell - maintain minimum height
        return Text("\n\n\n\n")

    # Build cell content
    text = Text()

    # Day number with appropriate styling
    day_str = str(day).rjust(2)
    if is_today:
        config = get_config()
        today_style = config.get("color.calendar.today", "black on white")
        text.append(day_str, style=_parse_style(today_style))
    else:
        text.append(day_str, style=Style(bold=True))

    # Add task entries
    lines_used = 1
    if tasks:
        for task in tasks[:max_tasks]:
            # Determine task style based on status
            if task.due and task.due < now:
                style = Style(color="red")
            elif task.priority and task.priority.value == "H":
                style = Style(color="yellow")
            else:
                style = Style(color="cyan")

            # Task ID as indicator
            task_id = str(task.id) if task.id else "?"
            prefix = f"{task_id}:"
            indent = " " * len(prefix)

            # Calculate available width for description
            first_width = title_width - len(prefix)
            second_width = title_width - len(indent)

            desc = task.description
            if len(desc) <= first_width:
                # Fits on one line
                text.append(f"\n{prefix}{desc}", style=style)
                lines_used += 1
            else:
                # Split across two lines
                first_part = desc[:first_width]
                remaining = desc[first_width:]
                if len(remaining) > second_width:
                    remaining = remaining[: second_width - 1] + "…"
                text.append(f"\n{prefix}{first_part}\n{indent}{remaining}", style=style)
                lines_used += 2

        # Show overflow count
        if len(tasks) > max_tasks:
            text.append(f"\n+{len(tasks) - max_tasks} more", style=Style(dim=True))
            lines_used += 1

    # Pad to minimum height (5 lines: day + 2 tasks + overflow + padding)
    while lines_used < 4:
        text.append("\n")
        lines_used += 1

    return text


def render_calendar(year: int, month: int, tasks: list[Task]) -> Table:
    """Render a calendar table for the given month.

    Args:
        year: Year to display.
        month: Month to display.
        tasks: All tasks to display.

    Returns:
        Rich Table with calendar view.
    """
    now = datetime.now()
    today = now.day if now.year == year and now.month == month else 0

    # Get tasks grouped by day
    tasks_by_day = get_tasks_by_date(tasks, year, month)

    # Create calendar with configured first day
    firstweekday = get_weekstart()
    cal = calendar.Calendar(firstweekday=firstweekday)
    month_name = calendar.month_name[month]

    # Create table with borders
    table = Table(
        title=f"[bold]{month_name} {year}[/bold]",
        show_header=True,
        header_style="bold",
        box=box.SQUARE,
        padding=(0, 1),
        expand=True,
        show_lines=True,
    )

    # Add day headers with fixed width for task titles
    col_width = 20
    for day_name in get_day_names(firstweekday):
        table.add_column(
            day_name, justify="left", width=col_width, no_wrap=True, overflow="ellipsis"
        )

    # Add weeks
    for week in cal.monthdayscalendar(year, month):
        row = []
        for day in week:
            day_tasks = tasks_by_day.get(day, [])
            is_today = day == today
            cell = format_day_cell(day, day_tasks, is_today, now)
            row.append(cell)
        table.add_row(*row)

    return table


def get_week_dates(year: int, week: int) -> list[datetime]:
    """Get the dates for a given ISO week.

    Args:
        year: Year.
        week: ISO week number (1-53).

    Returns:
        List of 7 datetime objects for the week.
    """
    # Get the first day of the ISO week (always Monday)
    jan4 = datetime(year, 1, 4)
    start_of_week1 = jan4 - timedelta(days=jan4.weekday())
    iso_week_start = start_of_week1 + timedelta(weeks=week - 1)

    # Adjust for configured first day of week
    firstweekday = get_weekstart()
    if firstweekday != 0:
        # Shift to configured first day
        # If firstweekday is 6 (Sunday), we go back 1 day from Monday
        offset = -((7 - firstweekday) % 7)
        week_start = iso_week_start + timedelta(days=offset)
    else:
        week_start = iso_week_start

    return [week_start + timedelta(days=i) for i in range(7)]


def get_tasks_for_week(
    tasks: list[Task], week_dates: list[datetime]
) -> dict[int, list[Task]]:
    """Group tasks by their due date for a specific week.

    Args:
        tasks: List of tasks to group.
        week_dates: List of dates in the week.

    Returns:
        Dictionary mapping day index (0-6) to list of tasks.
    """
    by_day: dict[int, list[Task]] = {}

    for i, date in enumerate(week_dates):
        by_day[i] = []
        for task in tasks:
            if (
                task.due
                and task.due.year == date.year
                and task.due.month == date.month
                and task.due.day == date.day
            ):
                by_day[i].append(task)

    return by_day


def render_week(week_dates: list[datetime], tasks: list[Task]) -> Table:
    """Render a calendar table for a specific week.

    Args:
        week_dates: List of 7 dates for the week.
        tasks: All tasks to display.

    Returns:
        Rich Table with week view.
    """
    now = datetime.now()
    today_date = now.date()

    # Get tasks grouped by day
    tasks_by_day = get_tasks_for_week(tasks, week_dates)

    # Get week number from first date
    week_num = week_dates[0].isocalendar()[1]

    # Format title with week number and date range
    start_date = week_dates[0]
    end_date = week_dates[6]
    if start_date.month == end_date.month:
        title = f"Week {week_num}: {start_date.strftime('%B')} {start_date.day}-{end_date.day}, {start_date.year}"
    else:
        title = f"Week {week_num}: {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"

    # Create table
    table = Table(
        title=f"[bold]{title}[/bold]",
        show_header=True,
        header_style="bold",
        box=box.SQUARE,
        padding=(0, 1),
        expand=True,
        show_lines=True,
    )

    # Add day headers with dates
    col_width = 20
    firstweekday = get_weekstart()
    day_names = get_day_names(firstweekday)
    for i, day_name in enumerate(day_names):
        date = week_dates[i]
        header = f"{day_name} {date.day}"
        table.add_column(
            header, justify="left", width=col_width, no_wrap=True, overflow="ellipsis"
        )

    # Single row with all days
    row = []
    for i in range(7):
        date = week_dates[i]
        day_tasks = tasks_by_day.get(i, [])
        is_today = date.date() == today_date
        # Use day=1 as placeholder since we show date in header
        cell = format_day_cell(
            day=date.day if is_today else 1,  # Show day number only for today
            tasks=day_tasks,
            is_today=is_today,
            now=now,
            max_tasks=4,  # Show more tasks in week view
            title_width=18,
        )
        # For non-today cells, remove the day number from display
        if not is_today:
            cell = format_week_cell(day_tasks, now, max_tasks=4, title_width=18)
        row.append(cell)

    table.add_row(*row)

    return table


def format_week_cell(
    tasks: list[Task],
    now: datetime,
    max_tasks: int = 4,
    title_width: int = 18,
) -> Text:
    """Format a week view cell (without day number).

    Args:
        tasks: Tasks due on this day.
        now: Current datetime.
        max_tasks: Maximum tasks to show per cell.
        title_width: Width for task titles.

    Returns:
        Formatted Rich Text for the cell.
    """
    text = Text()
    lines_used = 0

    if tasks:
        for task in tasks[:max_tasks]:
            # Determine task style
            if task.due and task.due < now:
                style = Style(color="red")
            elif task.priority and task.priority.value == "H":
                style = Style(color="yellow")
            else:
                style = Style(color="cyan")

            task_id = str(task.id) if task.id else "?"
            prefix = f"{task_id}:"
            indent = " " * len(prefix)

            first_width = title_width - len(prefix)
            second_width = title_width - len(indent)

            desc = task.description
            if len(desc) <= first_width:
                if lines_used > 0:
                    text.append("\n")
                text.append(f"{prefix}{desc}", style=style)
                lines_used += 1
            else:
                first_part = desc[:first_width]
                remaining = desc[first_width:]
                if len(remaining) > second_width:
                    remaining = remaining[: second_width - 1] + "…"
                if lines_used > 0:
                    text.append("\n")
                text.append(f"{prefix}{first_part}\n{indent}{remaining}", style=style)
                lines_used += 2

        if len(tasks) > max_tasks:
            text.append(f"\n+{len(tasks) - max_tasks} more", style=Style(dim=True))
            lines_used += 1

    # Pad to minimum height
    while lines_used < 4:
        text.append("\n")
        lines_used += 1

    return text


def show_calendar(
    month: int | None = None,
    year: int | None = None,
    week: int | None = None,
    filter_args: list[str] | None = None,
) -> None:
    """Display calendar view of tasks.

    Args:
        month: Month to display (1-12), defaults to current.
        year: Year to display, defaults to current.
        week: ISO week number (1-53), shows week view if specified.
        filter_args: Optional filter expressions to limit which tasks are shown.
    """
    now = datetime.now()

    # Default to current year
    if year is None:
        year = now.year

    # Get tasks
    db = Database()
    if not db.exists:
        console.print("[yellow]No tasks found[/yellow]")
        if week is not None:
            week_dates = get_week_dates(year, week)
            table = render_week(week_dates, [])
        else:
            if month is None:
                month = now.month
            table = render_calendar(year, month, [])
        console.print(table)
        return

    repo = TaskRepository(db)

    # Build filters
    filters: list[Filter] = []
    parser = FilterParser()

    # Apply context filters first
    current_context = get_current_context()
    if current_context:
        context_filters = get_context_filter(current_context)
        if context_filters:
            filters.extend(parser.parse(context_filters))

    # Apply user filters
    if filter_args:
        filters.extend(parser.parse(filter_args))

    # Get tasks
    if filters:
        # Default to pending tasks if no status filter specified
        has_status_filter = any(f.attribute == "status" for f in filters)
        if not has_status_filter:
            filters.append(Filter("status", "eq", "pending"))

        tasks = repo.list_filtered(filters)

        # Filter out waiting tasks by default
        now_time = datetime.now()
        tasks = [t for t in tasks if t.wait is None or t.wait <= now_time]

        # Apply virtual tag filters if any
        if parser.has_virtual_filters(filters):
            all_tasks = repo.list_all()
            tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)
    else:
        # No filters - use pending tasks (original behavior)
        all_tasks = repo.list_all()
        tasks = [
            t for t in all_tasks if t.status == TaskStatus.PENDING and t.due is not None
        ]

    # Filter to only tasks with due dates (calendar requires this)
    tasks = [t for t in tasks if t.due is not None]

    # JSON output mode
    if is_json_mode():
        output_json({"tasks": [task.model_dump(mode="json") for task in tasks]})
        return

    # Render week or month view
    if week is not None:
        # Validate week
        if week < 1 or week > 53:
            console.print(f"[red]Error:[/red] Invalid week: {week}")
            return

        week_dates = get_week_dates(year, week)
        table = render_week(week_dates, tasks)
        console.print(table)

        # Show legend
        console.print()
        console.print(
            "[dim]Legend:[/dim] "
            "[red]! overdue[/red]  "
            "[yellow]* high priority[/yellow]  "
            "[cyan]- normal[/cyan]  "
            "[black on white] today [/black on white]"
        )

        # Show task count for week
        tasks_in_week = sum(
            1
            for t in tasks
            if t.due
            and any(
                t.due.year == d.year and t.due.month == d.month and t.due.day == d.day
                for d in week_dates
            )
        )
        console.print(f"[dim]{tasks_in_week} task(s) due this week[/dim]")
    else:
        # Month view
        if month is None:
            month = now.month

        # Validate month
        if month < 1 or month > 12:
            console.print(f"[red]Error:[/red] Invalid month: {month}")
            return

        table = render_calendar(year, month, tasks)
        console.print(table)

        # Show legend
        console.print()
        console.print(
            "[dim]Legend:[/dim] "
            "[red]! overdue[/red]  "
            "[yellow]* high priority[/yellow]  "
            "[cyan]- normal[/cyan]  "
            "[black on white] today [/black on white]"
        )

        # Show task count summary
        tasks_in_month = sum(
            1 for t in tasks if t.due and t.due.year == year and t.due.month == month
        )
        console.print(f"[dim]{tasks_in_month} task(s) due this month[/dim]")
