"""Default configuration values."""

from pathlib import Path
from typing import Any

DEFAULTS: dict[str, Any] = {
    "data": {
        "location": str(Path.home() / ".local" / "share" / "taskng"),
    },
    "default": {
        "command": "next",
        "project": None,
        "priority": None,
    },
    "defaults": {
        "sort": "urgency-",
    },
    "ui": {
        "color": True,
        "unicode": True,
    },
    "color": {
        "enabled": True,
        "due": {
            "overdue": "red bold",
            "today": "yellow bold",
            "week": "cyan",
            "future": "green",
        },
        "priority": {
            "H": "red bold",
            "M": "yellow",
            "L": "blue",
        },
        "urgency": {
            "high": "red bold",
            "medium": "yellow",
            "low": "default",
        },
        "blocked": "magenta",
        "annotation": "cyan",
        "calendar": {
            "today": "black on white",
        },
    },
    "calendar": {
        "weekstart": "monday",  # monday, sunday, saturday, etc.
    },
    "report": {
        "list": {
            "columns": ["id", "priority", "project", "tags", "due", "description"],
            "sort": ["urgency-"],
        },
    },
    "urgency": {
        "priority": 1.0,
        "due": 0.5,
        "due_today": 1.0,
        "due_week": 1.0,
        "overdue": 1.0,
        "project": 1.0,
        "tags": 1.0,
        "blocked": 1.0,
        "age": 1.0,
    },
    "board": {
        "default": {
            "description": "Task board by status",
            "columns": [
                {
                    "name": "Backlog",
                    "filter": ["status:pending", "-ACTIVE", "-BLOCKED"],
                },
                {"name": "Blocked", "filter": ["+BLOCKED"]},
                {"name": "Active", "filter": ["+ACTIVE"]},
                {"name": "Done", "filter": ["status:completed"]},
            ],
            "card_fields": ["id", "priority", "description", "due"],
            "sort": ["urgency-"],
            "limit": 10,
        },
        "priority": {
            "description": "Tasks by priority",
            "columns": [
                {"name": "High", "filter": ["priority:H"]},
                {"name": "Medium", "filter": ["priority:M"]},
                {"name": "Low", "filter": ["priority:L"]},
                {"name": "None", "filter": ["priority.none:"]},
            ],
            "card_fields": ["id", "description", "due", "project"],
            "sort": ["urgency-"],
            "limit": 10,
        },
    },
    "sync": {
        "enabled": True,
        "backend": "git",  # "git", "file", "server" (future)
        "conflict_resolution": "last_write_wins",  # "last_write_wins", "manual"
        "git": {
            "directory": str(Path.home() / ".local" / "share" / "taskng" / "sync"),
            "remote": None,  # Optional git remote URL
        },
        # Future backends:
        # "file": {
        #     "directory": str(Path.home() / "Dropbox" / "taskng-sync"),
        # },
        # "server": {
        #     "url": None,
        # },
    },
}
