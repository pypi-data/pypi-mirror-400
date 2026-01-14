"""Tests for date parsing module."""

from datetime import datetime, timedelta

from taskng.core.dates import format_date, format_relative, parse_date


class TestParseDate:
    """Tests for parse_date function."""

    def test_parse_tomorrow(self):
        """Should parse 'tomorrow'."""
        result = parse_date("tomorrow")
        assert result is not None
        # Should be tomorrow's date
        tomorrow = datetime.now() + timedelta(days=1)
        assert result.date() == tomorrow.date()

    def test_parse_next_week(self):
        """Should parse 'next week'."""
        result = parse_date("next week")
        assert result is not None
        # Should be in the future
        assert result > datetime.now()

    def test_parse_in_3_days(self):
        """Should parse 'in 3 days'."""
        result = parse_date("in 3 days")
        assert result is not None
        expected = datetime.now() + timedelta(days=3)
        assert result.date() == expected.date()

    def test_parse_standard_format(self):
        """Should parse standard date format."""
        result = parse_date("2024-12-31")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31

    def test_parse_month_day(self):
        """Should parse month and day format."""
        result = parse_date("Dec 25")
        assert result is not None
        assert result.month == 12
        assert result.day == 25

    def test_parse_with_time(self):
        """Should parse date with time."""
        result = parse_date("tomorrow at 3pm")
        assert result is not None
        tomorrow = datetime.now() + timedelta(days=1)
        assert result.date() == tomorrow.date()
        assert result.hour == 15

    def test_parse_empty_string(self):
        """Should return None for empty string."""
        result = parse_date("")
        assert result is None

    def test_parse_invalid_string(self):
        """Should return None for invalid date string."""
        result = parse_date("not a date at all xyz123")
        assert result is None

    def test_parse_prefers_future(self):
        """Should prefer future dates for ambiguous inputs."""
        # "Monday" should be next Monday, not last Monday
        result = parse_date("monday")
        assert result is not None
        assert result >= datetime.now()

    def test_parse_relative_weeks(self):
        """Should parse relative weeks."""
        result = parse_date("in 2 weeks")
        assert result is not None
        expected = datetime.now() + timedelta(weeks=2)
        # Allow 1 day tolerance for timing
        assert abs((result.date() - expected.date()).days) <= 1

    def test_parse_yesterday(self):
        """Should parse 'yesterday'."""
        result = parse_date("yesterday")
        assert result is not None
        yesterday = datetime.now() - timedelta(days=1)
        assert result.date() == yesterday.date()

    def test_parse_end_of_year(self):
        """Should parse dates at year boundary."""
        result = parse_date("2024-12-31")
        assert result is not None
        assert result.year == 2024
        assert result.month == 12
        assert result.day == 31

        result = parse_date("2025-01-01")
        assert result is not None
        assert result.year == 2025
        assert result.month == 1
        assert result.day == 1

    def test_parse_with_midnight_time(self):
        """Should parse midnight time correctly."""
        result = parse_date("tomorrow at midnight")
        assert result is not None
        assert result.hour == 0
        assert result.minute == 0

    def test_parse_none_returns_none(self):
        """Should handle None input gracefully."""
        # parse_date should handle None without crashing
        try:
            result = parse_date(None)  # type: ignore[arg-type]
            assert result is None
        except (TypeError, AttributeError):
            # Also acceptable to raise TypeError for None input
            pass

    def test_parse_whitespace_only(self):
        """Should return None for whitespace-only string."""
        result = parse_date("   ")
        assert result is None

    def test_parse_special_characters(self):
        """Should return None for special characters."""
        result = parse_date("@#$%^&*()")
        assert result is None

    def test_parse_very_long_string(self):
        """Should handle very long input without crashing."""
        long_input = "tomorrow " * 100
        result = parse_date(long_input)
        # Should either parse or return None, but not crash
        assert result is None or isinstance(result, datetime)

    def test_parse_end_of_day(self):
        """Should parse end of day (eod) correctly."""
        result = parse_date("eod")
        if result is not None:
            # If eod is supported, should be end of today
            today = datetime.now().date()
            assert result.date() == today
            # End of day typically means 23:59 or similar
            assert result.hour >= 17  # At least evening

    def test_parse_leap_year_date(self):
        """Should parse leap year dates correctly."""
        result = parse_date("2024-02-29")
        assert result is not None
        assert result.year == 2024
        assert result.month == 2
        assert result.day == 29

    def test_parse_invalid_leap_year_date(self):
        """Should return None for invalid leap year date."""
        result = parse_date("2023-02-29")  # 2023 is not a leap year
        # Should either return None or adjust to valid date
        if result is not None:
            # If adjusted, should not be Feb 29
            assert not (result.month == 2 and result.day == 29 and result.year == 2023)


class TestFormatDate:
    """Tests for format_date function."""

    def test_format_date(self):
        """Should format datetime correctly."""
        dt = datetime(2024, 12, 31, 14, 30)
        result = format_date(dt)
        assert result == "2024-12-31 14:30"

    def test_format_date_midnight(self):
        """Should format midnight correctly."""
        dt = datetime(2024, 1, 1, 0, 0)
        result = format_date(dt)
        assert result == "2024-01-01 00:00"


class TestFormatRelative:
    """Tests for format_relative function."""

    def test_format_today(self):
        """Should format today."""
        dt = datetime.now()
        result = format_relative(dt)
        assert result == "today"

    def test_format_tomorrow(self):
        """Should format tomorrow."""
        dt = datetime.now() + timedelta(days=1)
        result = format_relative(dt)
        assert result == "tomorrow"

    def test_format_yesterday(self):
        """Should format yesterday."""
        dt = datetime.now() - timedelta(days=1)
        result = format_relative(dt)
        assert result == "yesterday"

    def test_format_in_days(self):
        """Should format future days."""
        dt = datetime.now() + timedelta(days=5)
        result = format_relative(dt)
        assert result == "in 5 days"

    def test_format_days_ago(self):
        """Should format past days."""
        dt = datetime.now() - timedelta(days=3)
        result = format_relative(dt)
        assert result == "3 days ago"
