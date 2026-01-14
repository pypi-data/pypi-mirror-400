"""ID expression parsing for task operations."""

import re


def parse_id_expression(expr: str) -> list[int]:
    """Parse ID expression into list of IDs.

    Examples:
        "5" -> [5]
        "1-5" -> [1, 2, 3, 4, 5]
        "1,3,5" -> [1, 3, 5]
        "1-3,7,10-12" -> [1, 2, 3, 7, 10, 11, 12]

    Args:
        expr: ID expression string.

    Returns:
        Sorted list of unique IDs.
    """
    ids: set[int] = set()

    # Split by comma
    parts = expr.split(",")

    for part in parts:
        part = part.strip()

        if "-" in part:
            # Range: 1-5
            match = re.match(r"(\d+)-(\d+)", part)
            if match:
                start, end = int(match.group(1)), int(match.group(2))
                if start > end:
                    start, end = end, start
                ids.update(range(start, end + 1))
        elif part.isdigit():
            # Single ID
            ids.add(int(part))

    return sorted(ids)


def expand_id_args(args: list[str]) -> list[int]:
    """Expand list of ID arguments into flat list of IDs.

    Args:
        args: List of ID expression strings.

    Returns:
        Sorted list of unique IDs.
    """
    ids: set[int] = set()

    for arg in args:
        ids.update(parse_id_expression(arg))

    return sorted(ids)
