"""Unit tests for calendar view."""

from datetime import datetime, timedelta
from unittest.mock import patch

from rich.style import Style

from taskng.cli.commands.calendar import (
    _parse_style,
    format_day_cell,
    format_week_cell,
    get_day_names,
    get_tasks_by_date,
    get_tasks_for_week,
    get_week_dates,
    get_weekstart,
    render_calendar,
    render_week,
    show_calendar,
)
from taskng.core.models import Priority, Task, TaskStatus


class TestGetTasksByDate:
    """Tests for get_tasks_by_date function."""

    def test_empty_tasks_returns_empty_dict(self) -> None:
        result = get_tasks_by_date([], 2024, 1)
        assert result == {}

    def test_groups_tasks_by_day(self) -> None:
        tasks = [
            Task(description="Task 1", due=datetime(2024, 1, 15, 10, 0)),
            Task(description="Task 2", due=datetime(2024, 1, 15, 14, 0)),
            Task(description="Task 3", due=datetime(2024, 1, 20, 9, 0)),
        ]
        result = get_tasks_by_date(tasks, 2024, 1)

        assert 15 in result
        assert len(result[15]) == 2
        assert 20 in result
        assert len(result[20]) == 1

    def test_excludes_tasks_from_other_months(self) -> None:
        tasks = [
            Task(description="January task", due=datetime(2024, 1, 15)),
            Task(description="February task", due=datetime(2024, 2, 15)),
        ]
        result = get_tasks_by_date(tasks, 2024, 1)

        assert 15 in result
        assert len(result[15]) == 1
        assert result[15][0].description == "January task"

    def test_excludes_tasks_from_other_years(self) -> None:
        tasks = [
            Task(description="2024 task", due=datetime(2024, 1, 15)),
            Task(description="2023 task", due=datetime(2023, 1, 15)),
        ]
        result = get_tasks_by_date(tasks, 2024, 1)

        assert 15 in result
        assert len(result[15]) == 1
        assert result[15][0].description == "2024 task"

    def test_excludes_tasks_without_due_date(self) -> None:
        tasks = [
            Task(description="With due", due=datetime(2024, 1, 15)),
            Task(description="Without due"),
        ]
        result = get_tasks_by_date(tasks, 2024, 1)

        assert len(result) == 1
        assert 15 in result


class TestFormatDayCell:
    """Tests for format_day_cell function."""

    def test_empty_day_returns_padded_text(self) -> None:
        now = datetime.now()
        result = format_day_cell(0, [], False, now)
        # Empty cells have minimum height padding
        assert result.plain.strip() == ""
        assert "\n" in result.plain

    def test_day_without_tasks_shows_number(self) -> None:
        now = datetime.now()
        result = format_day_cell(15, [], False, now)
        assert "15" in result.plain

    def test_today_has_special_styling(self) -> None:
        now = datetime.now()
        result = format_day_cell(15, [], True, now)
        assert "15" in result.plain
        # Check that it has styling (bgcolor)
        spans = list(result.spans)
        assert len(spans) > 0

    def test_shows_task_descriptions(self) -> None:
        now = datetime.now()
        tasks = [Task(description="Test task")]
        result = format_day_cell(15, tasks, False, now)
        assert "Test" in result.plain

    def test_wraps_long_descriptions_with_ellipsis(self) -> None:
        now = datetime.now()
        tasks = [
            Task(
                description="Very long task description that exceeds the available width"
            )
        ]
        tasks[0].id = 1
        result = format_day_cell(15, tasks, False, now)
        # Description should wrap and truncate with ellipsis
        assert "…" in result.plain
        assert "1:" in result.plain

    def test_shows_overdue_task(self) -> None:
        now = datetime.now()
        # Task due in the past
        tasks = [Task(description="Overdue", due=now - timedelta(days=1))]
        tasks[0].id = 1
        result = format_day_cell(15, tasks, False, now)
        assert "1:" in result.plain
        assert "Overdue" in result.plain

    def test_shows_high_priority_task(self) -> None:
        now = datetime.now()
        # Task with high priority, not overdue
        tasks = [
            Task(
                description="Important",
                priority=Priority("H"),
                due=now + timedelta(days=1),
            )
        ]
        tasks[0].id = 2
        result = format_day_cell(15, tasks, False, now)
        assert "2:" in result.plain
        assert "Important" in result.plain

    def test_shows_normal_task(self) -> None:
        now = datetime.now()
        # Normal task, not overdue
        tasks = [Task(description="Normal", due=now + timedelta(days=1))]
        result = format_day_cell(15, tasks, False, now)
        assert "Normal" in result.plain

    def test_limits_tasks_shown(self) -> None:
        now = datetime.now()
        tasks = [
            Task(description="Task 1"),
            Task(description="Task 2"),
            Task(description="Task 3"),
            Task(description="Task 4"),
            Task(description="Task 5"),
        ]
        result = format_day_cell(15, tasks, False, now)
        # Default max_tasks is 2, so should show +3 more
        assert "+3 more" in result.plain

    def test_multiple_tasks_shown(self) -> None:
        now = datetime.now()
        tasks = [
            Task(description="Task A"),
            Task(description="Task B"),
        ]
        result = format_day_cell(15, tasks, False, now)
        assert "Task A" in result.plain or "Task" in result.plain


class TestRenderCalendar:
    """Tests for render_calendar function."""

    def test_returns_table(self) -> None:
        result = render_calendar(2024, 1, [])
        # Rich Table has title attribute
        assert hasattr(result, "title")

    def test_table_has_correct_title(self) -> None:
        result = render_calendar(2024, 1, [])
        assert result.title is not None
        # Title contains month name and year
        title_str = str(result.title)
        assert "January" in title_str
        assert "2024" in title_str

    def test_table_has_seven_columns(self) -> None:
        result = render_calendar(2024, 1, [])
        assert len(result.columns) == 7

    def test_renders_february_correctly(self) -> None:
        result = render_calendar(2024, 2, [])
        title_str = str(result.title)
        assert "February" in title_str

    def test_renders_december_correctly(self) -> None:
        result = render_calendar(2024, 12, [])
        title_str = str(result.title)
        assert "December" in title_str

    def test_includes_tasks_in_render(self) -> None:
        tasks = [
            Task(description="Test task", due=datetime(2024, 1, 15, 10, 0)),
        ]
        result = render_calendar(2024, 1, tasks)
        # Table should have rows with the task
        assert len(result.rows) > 0


class TestParseStyle:
    """Tests for _parse_style function."""

    def test_empty_string_returns_default_style(self) -> None:
        result = _parse_style("")
        assert result == Style()

    def test_default_string_returns_default_style(self) -> None:
        result = _parse_style("default")
        assert result == Style()

    def test_parses_color_only(self) -> None:
        result = _parse_style("red")
        assert result.color is not None
        assert result.bold is True

    def test_parses_color_on_bgcolor(self) -> None:
        result = _parse_style("black on white")
        assert result.color is not None
        assert result.bgcolor is not None

    def test_parses_bold_keyword(self) -> None:
        result = _parse_style("bold")
        assert result.bold is True

    def test_parses_color_bold(self) -> None:
        result = _parse_style("red bold")
        assert result.color is not None
        assert result.bold is True


class TestGetWeekstart:
    """Tests for get_weekstart function."""

    def test_default_is_monday(self) -> None:
        result = get_weekstart()
        assert result == 0

    def test_with_config_sunday(self) -> None:
        with patch("taskng.cli.commands.calendar.get_config") as mock_config:
            mock_config.return_value.get.return_value = "sunday"
            result = get_weekstart()
            assert result == 6


class TestGetDayNames:
    """Tests for get_day_names function."""

    def test_monday_first(self) -> None:
        result = get_day_names(0)
        assert result[0] == "Mon"
        assert result[6] == "Sun"

    def test_sunday_first(self) -> None:
        result = get_day_names(6)
        assert result[0] == "Sun"
        assert result[6] == "Sat"


class TestGetWeekDates:
    """Tests for get_week_dates function."""

    def test_returns_seven_dates(self) -> None:
        result = get_week_dates(2024, 1)
        assert len(result) == 7

    def test_week_1_2024(self) -> None:
        result = get_week_dates(2024, 1)
        # Week 1 of 2024 starts on Monday Jan 1
        assert result[0].year == 2024
        assert result[0].month == 1
        assert result[0].day == 1

    def test_week_52_2023(self) -> None:
        result = get_week_dates(2023, 52)
        assert len(result) == 7

    def test_week_with_sunday_start(self) -> None:
        with patch("taskng.cli.commands.calendar.get_weekstart") as mock_start:
            mock_start.return_value = 6  # Sunday
            result = get_week_dates(2024, 1)
            assert len(result) == 7
            # Should start on Sunday before Monday
            assert result[0].weekday() == 6  # Sunday

    def test_consecutive_days(self) -> None:
        result = get_week_dates(2024, 10)
        for i in range(6):
            diff = result[i + 1] - result[i]
            assert diff.days == 1


class TestGetTasksForWeek:
    """Tests for get_tasks_for_week function."""

    def test_empty_tasks_returns_empty_lists(self) -> None:
        week_dates = get_week_dates(2024, 1)
        result = get_tasks_for_week([], week_dates)
        assert len(result) == 7
        for i in range(7):
            assert result[i] == []

    def test_groups_tasks_by_weekday(self) -> None:
        week_dates = get_week_dates(2024, 1)
        tasks = [
            Task(description="Monday task", due=week_dates[0]),
            Task(description="Friday task", due=week_dates[4]),
        ]
        result = get_tasks_for_week(tasks, week_dates)
        assert len(result[0]) == 1
        assert result[0][0].description == "Monday task"
        assert len(result[4]) == 1
        assert result[4][0].description == "Friday task"

    def test_multiple_tasks_same_day(self) -> None:
        week_dates = get_week_dates(2024, 1)
        tasks = [
            Task(description="Task 1", due=week_dates[2]),
            Task(description="Task 2", due=week_dates[2]),
        ]
        result = get_tasks_for_week(tasks, week_dates)
        assert len(result[2]) == 2

    def test_excludes_tasks_outside_week(self) -> None:
        week_dates = get_week_dates(2024, 1)
        tasks = [
            Task(description="In week", due=week_dates[0]),
            Task(description="Out of week", due=datetime(2024, 2, 15)),
        ]
        result = get_tasks_for_week(tasks, week_dates)
        total_tasks = sum(len(result[i]) for i in range(7))
        assert total_tasks == 1


class TestRenderWeek:
    """Tests for render_week function."""

    def test_returns_table(self) -> None:
        week_dates = get_week_dates(2024, 1)
        result = render_week(week_dates, [])
        assert hasattr(result, "title")

    def test_table_has_seven_columns(self) -> None:
        week_dates = get_week_dates(2024, 1)
        result = render_week(week_dates, [])
        assert len(result.columns) == 7

    def test_title_contains_week_number(self) -> None:
        week_dates = get_week_dates(2024, 10)
        result = render_week(week_dates, [])
        title_str = str(result.title)
        assert "Week 10" in title_str

    def test_title_same_month(self) -> None:
        # Find a week entirely within one month
        week_dates = get_week_dates(2024, 11)  # Week in March
        result = render_week(week_dates, [])
        title_str = str(result.title)
        assert "Week" in title_str

    def test_title_cross_month(self) -> None:
        # Week that spans two months
        week_dates = get_week_dates(2024, 5)  # Jan 29 - Feb 4
        result = render_week(week_dates, [])
        title_str = str(result.title)
        assert "Week" in title_str

    def test_with_tasks(self) -> None:
        week_dates = get_week_dates(2024, 1)
        tasks = [
            Task(description="Test task", due=week_dates[0]),
        ]
        tasks[0].id = 1
        result = render_week(week_dates, tasks)
        assert len(result.rows) == 1

    def test_today_highlighting(self) -> None:
        now = datetime.now()
        week_num = now.isocalendar()[1]
        week_dates = get_week_dates(now.year, week_num)
        result = render_week(week_dates, [])
        # Should render without error
        assert result is not None


class TestFormatWeekCell:
    """Tests for format_week_cell function."""

    def test_empty_tasks_returns_padded_text(self) -> None:
        now = datetime.now()
        result = format_week_cell([], now)
        # Should have minimum padding
        assert "\n" in result.plain

    def test_single_task(self) -> None:
        now = datetime.now()
        tasks = [Task(description="Test task")]
        tasks[0].id = 1
        result = format_week_cell(tasks, now)
        assert "1:" in result.plain
        assert "Test" in result.plain

    def test_overdue_task_style(self) -> None:
        now = datetime.now()
        tasks = [Task(description="Overdue", due=now - timedelta(days=1))]
        tasks[0].id = 1
        result = format_week_cell(tasks, now)
        assert "Overdue" in result.plain

    def test_high_priority_task_style(self) -> None:
        now = datetime.now()
        tasks = [
            Task(
                description="Important",
                priority=Priority("H"),
                due=now + timedelta(days=1),
            )
        ]
        tasks[0].id = 2
        result = format_week_cell(tasks, now)
        assert "Important" in result.plain

    def test_normal_task_style(self) -> None:
        now = datetime.now()
        tasks = [Task(description="Normal", due=now + timedelta(days=1))]
        tasks[0].id = 3
        result = format_week_cell(tasks, now)
        assert "Normal" in result.plain

    def test_long_description_wraps(self) -> None:
        now = datetime.now()
        tasks = [Task(description="Very long task description that will wrap")]
        tasks[0].id = 1
        result = format_week_cell(tasks, now)
        assert "…" in result.plain or "Very" in result.plain

    def test_multiple_tasks(self) -> None:
        now = datetime.now()
        tasks = [
            Task(description="Task 1"),
            Task(description="Task 2"),
        ]
        for i, t in enumerate(tasks):
            t.id = i + 1
        result = format_week_cell(tasks, now)
        assert "1:" in result.plain
        assert "2:" in result.plain

    def test_overflow_indicator(self) -> None:
        now = datetime.now()
        tasks = [Task(description=f"Task {i}") for i in range(6)]
        for i, t in enumerate(tasks):
            t.id = i + 1
        result = format_week_cell(tasks, now, max_tasks=4)
        assert "+2 more" in result.plain


class TestShowCalendar:
    """Tests for show_calendar function."""

    def test_no_database_shows_empty_calendar(self, capsys) -> None:
        show_calendar(month=1, year=2024)
        captured = capsys.readouterr()
        assert "January" in captured.out
        assert "2024" in captured.out

    def test_no_database_week_view(self, capsys) -> None:
        show_calendar(year=2024, week=1)
        captured = capsys.readouterr()
        assert "Week" in captured.out

    def test_default_current_month(self, capsys) -> None:
        show_calendar()
        captured = capsys.readouterr()
        # Should show current month
        now = datetime.now()
        import calendar

        month_name = calendar.month_name[now.month]
        assert month_name in captured.out

    def test_invalid_week_shows_error(self, capsys, temp_db) -> None:
        show_calendar(year=2024, week=54)
        captured = capsys.readouterr()
        assert "Invalid week" in captured.out

    def test_invalid_month_shows_error(self, capsys, temp_db) -> None:
        show_calendar(year=2024, month=13)
        captured = capsys.readouterr()
        assert "Invalid month" in captured.out

    def test_with_tasks_in_database(self, capsys, task_repo) -> None:
        # Add a task with due date
        task = Task(
            description="Test calendar task",
            due=datetime(2024, 6, 15, 10, 0),
            status=TaskStatus.PENDING,
        )
        task_repo.add(task)

        show_calendar(month=6, year=2024)
        captured = capsys.readouterr()
        assert "June" in captured.out
        assert "2024" in captured.out
        assert "task(s) due" in captured.out

    def test_week_view_with_tasks(self, capsys, task_repo) -> None:
        # Add a task for week 1 of 2024
        task = Task(
            description="Week test task",
            due=datetime(2024, 1, 2, 10, 0),
            status=TaskStatus.PENDING,
        )
        task_repo.add(task)

        show_calendar(year=2024, week=1)
        captured = capsys.readouterr()
        assert "Week" in captured.out
        assert "task(s) due" in captured.out

    def test_legend_shown_month_view(self, capsys, temp_db) -> None:
        show_calendar(month=1, year=2024)
        captured = capsys.readouterr()
        assert "Legend" in captured.out
        assert "overdue" in captured.out

    def test_legend_shown_week_view(self, capsys, temp_db) -> None:
        show_calendar(year=2024, week=1)
        captured = capsys.readouterr()
        assert "Legend" in captured.out
        assert "overdue" in captured.out

    def test_filters_completed_tasks(self, capsys, task_repo) -> None:
        # Add completed task - should not show in calendar
        task = Task(
            description="Completed task",
            due=datetime(2024, 6, 15, 10, 0),
            status=TaskStatus.COMPLETED,
        )
        task_repo.add(task)

        show_calendar(month=6, year=2024)
        captured = capsys.readouterr()
        assert "0 task(s) due" in captured.out

    def test_filters_tasks_without_due(self, capsys, task_repo) -> None:
        # Add task without due date - should not show
        task = Task(description="No due date", status=TaskStatus.PENDING)
        task_repo.add(task)

        show_calendar(month=6, year=2024)
        captured = capsys.readouterr()
        assert "0 task(s) due" in captured.out

    def test_year_transition(self, capsys) -> None:
        # December of one year, January of next
        show_calendar(month=12, year=2024)
        captured = capsys.readouterr()
        assert "December" in captured.out

        show_calendar(month=1, year=2025)
        captured = capsys.readouterr()
        assert "January" in captured.out
        assert "2025" in captured.out

    def test_week_53_edge_case(self, capsys) -> None:
        # 2020 had 53 weeks
        show_calendar(year=2020, week=53)
        captured = capsys.readouterr()
        assert "Week" in captured.out

    def test_task_count_accuracy(self, capsys, task_repo) -> None:
        # Add multiple tasks to same month
        for i in range(3):
            task = Task(
                description=f"Task {i}",
                due=datetime(2024, 3, 10 + i, 10, 0),
                status=TaskStatus.PENDING,
            )
            task_repo.add(task)

        show_calendar(month=3, year=2024)
        captured = capsys.readouterr()
        assert "3 task(s) due" in captured.out
