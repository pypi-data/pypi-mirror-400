"""Output formatting utilities for Task-NG CLI."""

import json
from typing import Any

# Global state for output mode
_json_mode = False


def set_json_mode(enabled: bool) -> None:
    """Set JSON output mode.

    Args:
        enabled: Whether to enable JSON mode.
    """
    global _json_mode
    _json_mode = enabled


def is_json_mode() -> bool:
    """Check if JSON output mode is enabled.

    Returns:
        True if JSON mode is enabled.
    """
    return _json_mode


def output_json(data: Any) -> None:
    """Output data as JSON.

    Args:
        data: Data to output (Pydantic model, list, or dict).
    """
    if hasattr(data, "model_dump"):
        # Pydantic model
        print(json.dumps(data.model_dump(), default=str, indent=2))
    elif isinstance(data, list):
        items = [
            item.model_dump() if hasattr(item, "model_dump") else item for item in data
        ]
        print(json.dumps(items, default=str, indent=2))
    else:
        print(json.dumps(data, default=str, indent=2))
