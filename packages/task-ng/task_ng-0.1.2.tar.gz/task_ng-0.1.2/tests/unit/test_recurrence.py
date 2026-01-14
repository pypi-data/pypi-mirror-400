"""Unit tests for recurrence module."""

from datetime import datetime

import pytest

from taskng.core.models import Priority, Task
from taskng.core.recurrence import (
    calculate_next_due,
    create_next_occurrence,
    parse_recurrence,
)


class TestParseRecurrence:
    """Tests for parse_recurrence function.

    parse_recurrence converts user-friendly recurrence strings into internal
    representations used by calculate_next_due. The internal format uses:
    - 'type': base time unit (daily/weekly/monthly/yearly)
    - 'interval': multiplier for the base unit

    Named patterns provide convenience aliases:
    - 'biweekly' -> every 2 weeks
    - 'quarterly' -> every 3 months
    - 'annual' -> alias for yearly
    """

    def test_parse_daily_maps_to_one_day_interval(self):
        """'daily' means repeat every 1 day."""
        result = parse_recurrence("daily")
        assert result == {"type": "daily", "interval": 1}

    def test_parse_weekly_maps_to_one_week_interval(self):
        """'weekly' means repeat every 1 week."""
        result = parse_recurrence("weekly")
        assert result == {"type": "weekly", "interval": 1}

    def test_parse_biweekly_maps_to_two_week_interval(self):
        """'biweekly' means repeat every 2 weeks (14 days)."""
        result = parse_recurrence("biweekly")
        assert result == {"type": "weekly", "interval": 2}

    def test_parse_monthly_maps_to_one_month_interval(self):
        """'monthly' means repeat every 1 month."""
        result = parse_recurrence("monthly")
        assert result == {"type": "monthly", "interval": 1}

    def test_parse_quarterly_maps_to_three_month_interval(self):
        """'quarterly' means repeat every 3 months (one quarter)."""
        result = parse_recurrence("quarterly")
        assert result == {"type": "monthly", "interval": 3}

    def test_parse_yearly_maps_to_one_year_interval(self):
        """'yearly' means repeat every 1 year."""
        result = parse_recurrence("yearly")
        assert result == {"type": "yearly", "interval": 1}

    def test_parse_annual_is_alias_for_yearly(self):
        """'annual' is a synonym for 'yearly'."""
        result = parse_recurrence("annual")
        assert result == {"type": "yearly", "interval": 1}

    def test_parse_interval_days_syntax(self):
        """'3d' means repeat every 3 days using interval syntax."""
        result = parse_recurrence("3d")
        assert result == {"type": "daily", "interval": 3}

    def test_parse_interval_weeks_syntax(self):
        """'2w' means repeat every 2 weeks using interval syntax."""
        result = parse_recurrence("2w")
        assert result == {"type": "weekly", "interval": 2}

    def test_parse_interval_months_syntax(self):
        """'6m' means repeat every 6 months using interval syntax."""
        result = parse_recurrence("6m")
        assert result == {"type": "monthly", "interval": 6}

    def test_parse_interval_years_syntax(self):
        """'1y' means repeat every 1 year using interval syntax."""
        result = parse_recurrence("1y")
        assert result == {"type": "yearly", "interval": 1}

    def test_parse_is_case_insensitive(self):
        """Recurrence patterns should be case-insensitive for user convenience."""
        result = parse_recurrence("DAILY")
        assert result == {"type": "daily", "interval": 1}

    def test_parse_strips_whitespace(self):
        """Leading/trailing whitespace should be ignored for user convenience."""
        result = parse_recurrence("  weekly  ")
        assert result == {"type": "weekly", "interval": 1}

    def test_parse_invalid_returns_none(self):
        """Unknown patterns should return None (not raise exception)."""
        result = parse_recurrence("invalid")
        assert result is None

    def test_parse_empty_returns_none(self):
        """Empty string should return None (not raise exception)."""
        result = parse_recurrence("")
        assert result is None

    def test_parse_invalid_interval_unit_returns_none(self):
        """Invalid interval unit (e.g., '3x') should return None."""
        result = parse_recurrence("3x")
        assert result is None


class TestCalculateNextDue:
    """Tests for calculate_next_due function."""

    def test_daily(self):
        current = datetime(2024, 1, 1, 9, 0)
        recurrence = {"type": "daily", "interval": 1}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 1, 2, 9, 0)

    def test_daily_interval(self):
        current = datetime(2024, 1, 1, 9, 0)
        recurrence = {"type": "daily", "interval": 3}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 1, 4, 9, 0)

    def test_weekly(self):
        current = datetime(2024, 1, 1, 9, 0)
        recurrence = {"type": "weekly", "interval": 1}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 1, 8, 9, 0)

    def test_weekly_interval(self):
        current = datetime(2024, 1, 1, 9, 0)
        recurrence = {"type": "weekly", "interval": 2}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 1, 15, 9, 0)

    def test_monthly(self):
        current = datetime(2024, 1, 15, 9, 0)
        recurrence = {"type": "monthly", "interval": 1}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 2, 15, 9, 0)

    def test_monthly_interval(self):
        current = datetime(2024, 1, 15, 9, 0)
        recurrence = {"type": "monthly", "interval": 3}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2024, 4, 15, 9, 0)

    def test_monthly_end_of_month(self):
        current = datetime(2024, 1, 31, 9, 0)
        recurrence = {"type": "monthly", "interval": 1}
        result = calculate_next_due(current, recurrence)
        # February doesn't have 31 days, so it adjusts
        assert result == datetime(2024, 2, 29, 9, 0)  # 2024 is leap year

    def test_yearly(self):
        current = datetime(2024, 3, 15, 9, 0)
        recurrence = {"type": "yearly", "interval": 1}
        result = calculate_next_due(current, recurrence)
        assert result == datetime(2025, 3, 15, 9, 0)

    def test_yearly_leap_day(self):
        current = datetime(2024, 2, 29, 9, 0)
        recurrence = {"type": "yearly", "interval": 1}
        result = calculate_next_due(current, recurrence)
        # Feb 29 2025 doesn't exist, so it adjusts to Feb 28
        assert result == datetime(2025, 2, 28, 9, 0)


class TestCreateNextOccurrence:
    """Tests for create_next_occurrence function."""

    def test_basic_recurrence(self):
        task = Task(
            description="Daily standup",
            due=datetime(2024, 1, 1, 9, 0),
            recur="daily",
            uuid="test-uuid",
        )
        next_task = create_next_occurrence(task)

        assert next_task.description == "Daily standup"
        assert next_task.due == datetime(2024, 1, 2, 9, 0)
        assert next_task.recur == "daily"
        assert next_task.parent_uuid == "test-uuid"

    def test_inherits_project(self):
        task = Task(
            description="Weekly review",
            project="Work",
            due=datetime(2024, 1, 1, 9, 0),
            recur="weekly",
        )
        next_task = create_next_occurrence(task)

        assert next_task.project == "Work"

    def test_inherits_priority(self):
        task = Task(
            description="Important task",
            priority=Priority.HIGH,
            due=datetime(2024, 1, 1, 9, 0),
            recur="daily",
        )
        next_task = create_next_occurrence(task)

        assert next_task.priority == Priority.HIGH

    def test_inherits_tags(self):
        task = Task(
            description="Tagged task",
            tags=["urgent", "work"],
            due=datetime(2024, 1, 1, 9, 0),
            recur="daily",
        )
        next_task = create_next_occurrence(task)

        assert next_task.tags == ["urgent", "work"]
        # Ensure it's a copy
        assert next_task.tags is not task.tags

    def test_inherits_until(self):
        task = Task(
            description="Limited task",
            due=datetime(2024, 1, 1, 9, 0),
            recur="daily",
            until=datetime(2024, 12, 31),
        )
        next_task = create_next_occurrence(task)

        assert next_task.until == datetime(2024, 12, 31)

    def test_raises_without_recur(self):
        task = Task(
            description="No recurrence",
            due=datetime(2024, 1, 1, 9, 0),
        )
        with pytest.raises(ValueError, match="must have recur"):
            create_next_occurrence(task)

    def test_raises_without_due(self):
        task = Task(
            description="No due date",
            recur="daily",
        )
        with pytest.raises(ValueError, match="must have recur and due"):
            create_next_occurrence(task)

    def test_raises_past_until(self):
        task = Task(
            description="Past until",
            due=datetime(2024, 12, 31, 9, 0),
            recur="daily",
            until=datetime(2024, 12, 31),
        )
        with pytest.raises(ValueError, match="past until date"):
            create_next_occurrence(task)

    def test_raises_invalid_recurrence(self):
        task = Task(
            description="Invalid recurrence",
            due=datetime(2024, 1, 1, 9, 0),
            recur="invalid",
        )
        with pytest.raises(ValueError, match="Invalid recurrence pattern"):
            create_next_occurrence(task)
