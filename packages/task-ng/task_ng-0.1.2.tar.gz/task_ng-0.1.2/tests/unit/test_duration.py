"""Tests for duration parsing."""

from datetime import datetime, timedelta

from taskng.core.dates import is_duration, parse_date_or_duration, parse_duration


class TestParseDuration:
    """Tests for parse_duration function."""

    def test_parse_hours(self):
        """Should parse hours."""
        result = parse_duration("1h")
        assert result == timedelta(hours=1)

        result = parse_duration("24h")
        assert result == timedelta(hours=24)

    def test_parse_days(self):
        """Should parse days."""
        result = parse_duration("1d")
        assert result == timedelta(days=1)

        result = parse_duration("7d")
        assert result == timedelta(days=7)

    def test_parse_weeks(self):
        """Should parse weeks."""
        result = parse_duration("1w")
        assert result == timedelta(weeks=1)

        result = parse_duration("2w")
        assert result == timedelta(weeks=2)

    def test_parse_months(self):
        """Should parse months (30 days)."""
        result = parse_duration("1m")
        assert result == timedelta(days=30)

        result = parse_duration("3m")
        assert result == timedelta(days=90)

    def test_parse_years(self):
        """Should parse years (365 days)."""
        result = parse_duration("1y")
        assert result == timedelta(days=365)

    def test_parse_uppercase(self):
        """Should parse uppercase units."""
        result = parse_duration("1H")
        assert result == timedelta(hours=1)

        result = parse_duration("1D")
        assert result == timedelta(days=1)

    def test_parse_empty(self):
        """Should return None for empty string."""
        result = parse_duration("")
        assert result is None

    def test_parse_invalid(self):
        """Should return None for invalid duration."""
        assert parse_duration("abc") is None
        assert parse_duration("1") is None
        assert parse_duration("h") is None
        assert parse_duration("1x") is None

    def test_parse_with_spaces(self):
        """Should handle spaces."""
        result = parse_duration("  3d  ")
        assert result == timedelta(days=3)


class TestIsDuration:
    """Tests for is_duration function."""

    def test_valid_durations(self):
        """Should return True for valid durations."""
        assert is_duration("1h")
        assert is_duration("2d")
        assert is_duration("3w")
        assert is_duration("1m")
        assert is_duration("1y")

    def test_invalid_durations(self):
        """Should return False for invalid durations."""
        assert not is_duration("tomorrow")
        assert not is_duration("next week")
        assert not is_duration("2024-01-01")
        assert not is_duration("")


class TestParseDateOrDuration:
    """Tests for parse_date_or_duration function."""

    def test_parse_duration(self):
        """Should parse duration and return datetime."""
        now = datetime.now()
        result = parse_date_or_duration("3d")
        assert result is not None
        # Should be approximately 3 days from now
        expected = now + timedelta(days=3)
        assert abs((result - expected).total_seconds()) < 1

    def test_parse_date(self):
        """Should parse natural language date."""
        result = parse_date_or_duration("tomorrow")
        assert result is not None
        tomorrow = datetime.now() + timedelta(days=1)
        assert result.date() == tomorrow.date()

    def test_parse_empty(self):
        """Should return None for empty string."""
        result = parse_date_or_duration("")
        assert result is None

    def test_duration_takes_precedence(self):
        """Duration format should be tried first."""
        # "1d" could be parsed as a date, but should be parsed as duration
        now = datetime.now()
        result = parse_date_or_duration("1d")
        assert result is not None
        expected = now + timedelta(days=1)
        assert abs((result - expected).total_seconds()) < 1
