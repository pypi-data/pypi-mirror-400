"""Display utilities for Task-NG."""

from datetime import datetime

from rich.style import Style
from rich.text import Text

from taskng.config.settings import get_config
from taskng.core.dependencies import is_blocked
from taskng.core.models import Task


def get_due_style(due: datetime | None) -> Style:
    """Get style for due date based on urgency.

    Args:
        due: Due datetime.

    Returns:
        Rich Style for the due date.
    """
    if not due:
        return Style()

    config = get_config()
    now = datetime.now()
    delta = due - now

    if delta.total_seconds() < 0:
        # Overdue - red
        color = config.get("color.due.overdue", "red bold")
        return _parse_style(color)
    elif delta.days == 0:
        # Due today - yellow
        color = config.get("color.due.today", "yellow bold")
        return _parse_style(color)
    elif delta.days < 7:
        # Due this week - cyan
        color = config.get("color.due.week", "cyan")
        return _parse_style(color)
    else:
        # Future - green
        color = config.get("color.due.future", "green")
        return _parse_style(color)


def get_priority_style(priority: str | None) -> Style:
    """Get style for priority.

    Args:
        priority: Priority letter (H/M/L).

    Returns:
        Rich Style for the priority.
    """
    if not priority:
        return Style()

    config = get_config()
    styles = {
        "H": config.get("color.priority.H", "red bold"),
        "M": config.get("color.priority.M", "yellow"),
        "L": config.get("color.priority.L", "blue"),
    }
    return _parse_style(styles.get(priority, ""))


def get_urgency_style(urgency: float) -> Style:
    """Get style based on urgency score.

    Args:
        urgency: Urgency score.

    Returns:
        Rich Style for the urgency display.
    """
    config = get_config()

    if urgency >= 10:
        color = config.get("color.urgency.high", "red bold")
    elif urgency >= 5:
        color = config.get("color.urgency.medium", "yellow")
    else:
        color = config.get("color.urgency.low", "default")

    return _parse_style(color)


def format_due(due: datetime | None) -> Text:
    """Format due date with color.

    Args:
        due: Due datetime.

    Returns:
        Rich Text with styling.
    """
    if not due:
        return Text("")

    now = datetime.now()
    delta = due - now

    # Format relative
    if delta.total_seconds() < 0:
        days = abs(delta.days)
        if days == 0:
            text = "today"
        elif days == 1:
            text = "1d ago"
        else:
            text = f"{days}d ago"
    elif delta.days == 0:
        text = "today"
    elif delta.days == 1:
        text = "tomorrow"
    elif delta.days < 7:
        text = f"in {delta.days}d"
    else:
        text = due.strftime("%Y-%m-%d")

    style = get_due_style(due)
    return Text(text, style=style)


def format_priority(priority: str | None) -> Text:
    """Format priority with color.

    Args:
        priority: Priority letter.

    Returns:
        Rich Text with styling.
    """
    if not priority:
        return Text("")

    style = get_priority_style(priority)
    return Text(priority, style=style)


def format_urgency(urgency: float) -> Text:
    """Format urgency score with color.

    Args:
        urgency: Urgency score.

    Returns:
        Rich Text with styling.
    """
    style = get_urgency_style(urgency)
    return Text(f"{urgency:.1f}", style=style)


def format_description(
    task: Task,
    all_tasks: list[Task] | None = None,
    max_length: int | None = None,
) -> Text:
    """Format task description with indicators.

    Args:
        task: Task to format.
        all_tasks: All tasks for dependency check.
        max_length: Maximum description length (None for no limit).

    Returns:
        Rich Text with description and indicators.
    """
    config = get_config()
    desc = task.description
    if max_length and len(desc) > max_length:
        desc = desc[: max_length - 3] + "..."

    text = Text(desc)

    # Add blocked indicator
    if all_tasks and task.depends and is_blocked(task, all_tasks):
        blocked_style = config.get("color.blocked", "magenta")
        text.append(" ")
        text.append("[B]", style=_parse_style(blocked_style))

    # Add annotation indicator
    if task.annotations:
        annotation_style = config.get("color.annotation", "cyan")
        text.append(" ")
        text.append(f"[{len(task.annotations)}]", style=_parse_style(annotation_style))

    return text


def get_row_style(index: int) -> str:
    """Get style for table row based on index.

    Args:
        index: Row index (0-based).

    Returns:
        Style string for alternating rows.
    """
    if index % 2 == 1:
        config = get_config()
        return str(config.get("color.row.alternate", "on grey11"))
    return ""


def is_color_enabled() -> bool:
    """Check if color output is enabled.

    Returns:
        True if colors should be used.
    """
    config = get_config()
    return bool(config.get("color.enabled", True))


def _parse_style(style_string: str) -> Style:
    """Parse style string into Rich Style.

    Args:
        style_string: Style like "red bold" or "yellow".

    Returns:
        Rich Style object.
    """
    if not style_string or style_string == "default":
        return Style()

    parts = style_string.split()
    color = None
    bold = False
    italic = False

    for part in parts:
        if part == "bold":
            bold = True
        elif part == "italic":
            italic = True
        else:
            color = part

    return Style(color=color, bold=bold, italic=italic)
