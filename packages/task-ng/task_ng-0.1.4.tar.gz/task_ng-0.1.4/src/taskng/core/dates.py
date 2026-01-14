"""Natural language date parsing for Task-NG."""

import re
from datetime import datetime, timedelta
from typing import Any, cast

import dateparser  # type: ignore[import-untyped]


def parse_date(date_string: str) -> datetime | None:
    """Parse natural language date string.

    Args:
        date_string: Natural language date like "tomorrow" or "next friday"

    Returns:
        Parsed datetime or None if parsing failed.
    """
    if not date_string:
        return None

    settings: dict[str, Any] = {
        "PREFER_DATES_FROM": "future",
        "RETURN_AS_TIMEZONE_AWARE": False,
    }

    result = dateparser.parse(date_string, settings=settings)
    if result is None:
        return None
    return cast(datetime, result)


def format_date(dt: datetime) -> str:
    """Format datetime for display.

    Args:
        dt: Datetime to format.

    Returns:
        Formatted date string.
    """
    return dt.strftime("%Y-%m-%d %H:%M")


def format_relative(dt: datetime) -> str:
    """Format datetime as relative string (e.g., "in 2 days").

    Args:
        dt: Datetime to format.

    Returns:
        Relative date string.
    """
    today = datetime.now().date()
    dt_date = dt.date()
    delta_days = (dt_date - today).days

    if delta_days == 0:
        return "today"
    elif delta_days == 1:
        return "tomorrow"
    elif delta_days == -1:
        return "yesterday"
    elif delta_days > 0:
        return f"in {delta_days} days"
    else:
        return f"{abs(delta_days)} days ago"


def parse_duration(duration_string: str) -> timedelta | None:
    """Parse duration string like '1h', '2d', '1w'.

    Args:
        duration_string: Duration like "1h", "2d", "1w"

    Returns:
        Timedelta or None if parsing failed.
    """
    if not duration_string:
        return None

    pattern = r"^(\d+)([hdwmyHDWMY])$"
    match = re.match(pattern, duration_string.strip())

    if not match:
        return None

    value = int(match.group(1))
    unit = match.group(2).lower()

    units = {
        "h": timedelta(hours=value),
        "d": timedelta(days=value),
        "w": timedelta(weeks=value),
        "m": timedelta(days=value * 30),
        "y": timedelta(days=value * 365),
    }

    return units.get(unit)


def is_duration(string: str) -> bool:
    """Check if string is a duration format.

    Args:
        string: String to check.

    Returns:
        True if string matches duration pattern.
    """
    return parse_duration(string) is not None


def parse_date_or_duration(string: str) -> datetime | None:
    """Parse string as either duration or natural language date.

    Args:
        string: Duration like "3d" or date like "tomorrow"

    Returns:
        Datetime or None if parsing failed.
    """
    if not string:
        return None

    # Try duration first
    delta = parse_duration(string)
    if delta:
        return datetime.now() + delta

    # Fall back to natural language date
    return parse_date(string)
