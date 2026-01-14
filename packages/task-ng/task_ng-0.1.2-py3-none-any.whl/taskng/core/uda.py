"""User Defined Attributes for Task-NG."""

import re
from typing import Any


def parse_udas_from_text(text: str) -> tuple[str, dict[str, str]]:
    """Extract key:value UDAs from text.

    Args:
        text: Text possibly containing key:value pairs.

    Returns:
        Tuple of (cleaned text, dict of UDAs).
    """
    # Pattern matches word:value where value can be quoted or unquoted
    pattern = r"\b([a-zA-Z_][a-zA-Z0-9_]*):([^\s]+)"

    udas: dict[str, str] = {}
    matches = re.findall(pattern, text)

    # Known task attributes that shouldn't be treated as UDAs
    reserved = {
        "project",
        "priority",
        "due",
        "wait",
        "scheduled",
        "recur",
        "until",
        "status",
    }

    for key, value in matches:
        if key.lower() not in reserved:
            udas[key] = value

    # Remove UDA patterns from text
    clean_text = text
    for key in udas:
        clean_text = re.sub(rf"\b{key}:[^\s]+\s*", "", clean_text)

    return clean_text.strip(), udas


def validate_uda_value(value: Any, uda_type: str = "string") -> str:
    """Validate and convert UDA value to string for storage.

    Args:
        value: Value to validate.
        uda_type: Type of UDA (string, numeric, date, duration).

    Returns:
        String value for storage.

    Raises:
        ValueError: If value is invalid for type.
    """
    if value is None:
        return ""

    if uda_type == "numeric":
        try:
            float(value)
        except (TypeError, ValueError):
            raise ValueError(f"Invalid numeric value: {value}") from None

    return str(value)


def format_uda_value(value: str, uda_type: str = "string") -> str:
    """Format UDA value for display.

    Args:
        value: Stored value.
        uda_type: Type of UDA.

    Returns:
        Formatted value for display.
    """
    if not value:
        return ""

    if uda_type == "numeric":
        try:
            num = float(value)
            if num == int(num):
                return str(int(num))
            return str(num)
        except ValueError:
            return value

    return value
