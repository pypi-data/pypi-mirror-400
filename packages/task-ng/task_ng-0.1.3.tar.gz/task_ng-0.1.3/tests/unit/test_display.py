"""Unit tests for display utilities."""

from datetime import datetime, timedelta

from rich.style import Style

from taskng.cli.display import (
    format_description,
    format_due,
    format_priority,
    format_urgency,
    get_due_style,
    get_priority_style,
    get_urgency_style,
    is_color_enabled,
)
from taskng.core.models import Task


class TestGetDueStyle:
    """Tests for get_due_style function."""

    def test_overdue_returns_red_bold(self) -> None:
        due = datetime.now() - timedelta(days=1)
        style = get_due_style(due)
        assert style.color.name == "red"
        assert style.bold is True

    def test_due_today_returns_yellow_bold(self) -> None:
        due = datetime.now() + timedelta(hours=1)
        style = get_due_style(due)
        assert style.color.name == "yellow"
        assert style.bold is True

    def test_due_this_week_returns_cyan(self) -> None:
        due = datetime.now() + timedelta(days=3)
        style = get_due_style(due)
        assert style.color.name == "cyan"

    def test_future_due_returns_green(self) -> None:
        due = datetime.now() + timedelta(days=14)
        style = get_due_style(due)
        assert style.color.name == "green"

    def test_none_returns_empty_style(self) -> None:
        style = get_due_style(None)
        assert style == Style()


class TestGetPriorityStyle:
    """Tests for get_priority_style function."""

    def test_high_priority_returns_red_bold(self) -> None:
        style = get_priority_style("H")
        assert style.color.name == "red"
        assert style.bold is True

    def test_medium_priority_returns_yellow(self) -> None:
        style = get_priority_style("M")
        assert style.color.name == "yellow"

    def test_low_priority_returns_blue(self) -> None:
        style = get_priority_style("L")
        assert style.color.name == "blue"

    def test_none_returns_empty_style(self) -> None:
        style = get_priority_style(None)
        assert style == Style()


class TestGetUrgencyStyle:
    """Tests for get_urgency_style function."""

    def test_high_urgency_returns_red_bold(self) -> None:
        style = get_urgency_style(12.5)
        assert style.color.name == "red"
        assert style.bold is True

    def test_medium_urgency_returns_yellow(self) -> None:
        style = get_urgency_style(7.0)
        assert style.color.name == "yellow"

    def test_low_urgency_returns_default(self) -> None:
        style = get_urgency_style(2.0)
        assert style == Style()


class TestFormatDue:
    """Tests for format_due function."""

    def test_overdue_shows_days_ago(self) -> None:
        due = datetime.now() - timedelta(hours=72)  # 3 days ago
        text = format_due(due)
        assert "d ago" in text.plain

    def test_due_today_shows_today(self) -> None:
        due = datetime.now() + timedelta(hours=1)
        text = format_due(due)
        assert text.plain == "today"

    def test_due_tomorrow_shows_tomorrow(self) -> None:
        due = datetime.now() + timedelta(hours=30)  # ~1.25 days
        text = format_due(due)
        assert text.plain == "tomorrow"

    def test_due_this_week_shows_days(self) -> None:
        due = datetime.now() + timedelta(hours=72)  # 3 days
        text = format_due(due)
        assert "in" in text.plain and "d" in text.plain

    def test_future_shows_date(self) -> None:
        due = datetime.now() + timedelta(days=30)
        text = format_due(due)
        assert "-" in text.plain  # Date format

    def test_none_returns_empty(self) -> None:
        text = format_due(None)
        assert text.plain == ""


class TestFormatPriority:
    """Tests for format_priority function."""

    def test_high_priority_formats(self) -> None:
        text = format_priority("H")
        assert text.plain == "H"

    def test_medium_priority_formats(self) -> None:
        text = format_priority("M")
        assert text.plain == "M"

    def test_low_priority_formats(self) -> None:
        text = format_priority("L")
        assert text.plain == "L"

    def test_none_returns_empty(self) -> None:
        text = format_priority(None)
        assert text.plain == ""


class TestFormatUrgency:
    """Tests for format_urgency function.

    Urgency values are formatted with one decimal place for readability.
    Python's default rounding (round-half-to-even/banker's rounding) is used.
    """

    def test_formats_with_one_decimal_using_standard_rounding(self) -> None:
        """Should format urgency to one decimal using round-half-to-even.

        6.25 rounds to 6.2 (banker's rounding rounds to nearest even).
        This provides consistent, unbiased rounding for display purposes.
        """
        text = format_urgency(6.25)
        assert text.plain == "6.2"

    def test_formats_high_urgency(self) -> None:
        """High urgency (>=10) should display exact value."""
        text = format_urgency(12.5)
        assert "12.5" in text.plain

    def test_formats_low_urgency(self) -> None:
        """Low urgency should display with one decimal."""
        text = format_urgency(1.0)
        assert "1.0" in text.plain


class TestFormatDescription:
    """Tests for format_description function."""

    def test_short_description_not_truncated(self) -> None:
        task = Task(description="Short task")
        text = format_description(task)
        assert text.plain == "Short task"

    def test_long_description_truncated(self) -> None:
        task = Task(description="A" * 100)
        text = format_description(task, max_length=50)
        assert len(text.plain) <= 50
        assert "..." in text.plain

    def test_blocked_task_shows_indicator(self) -> None:
        task1 = Task(description="Blocker", uuid="blocker-uuid")
        task2 = Task(description="Blocked task", depends=["blocker-uuid"])
        all_tasks = [task1, task2]

        text = format_description(task2, all_tasks)
        assert "[B]" in text.plain

    def test_unblocked_task_no_indicator(self) -> None:
        task = Task(description="Normal task")
        text = format_description(task, [task])
        assert "[B]" not in text.plain

    def test_annotated_task_shows_count(self) -> None:
        task = Task(description="Annotated task")
        task.add_annotation("Note 1")
        task.add_annotation("Note 2")

        text = format_description(task)
        assert "[2]" in text.plain

    def test_no_annotations_no_indicator(self) -> None:
        task = Task(description="Normal task")
        text = format_description(task)
        assert "[" not in text.plain or "[B]" in text.plain


class TestIsColorEnabled:
    """Tests for is_color_enabled function."""

    def test_returns_bool(self) -> None:
        result = is_color_enabled()
        assert isinstance(result, bool)
