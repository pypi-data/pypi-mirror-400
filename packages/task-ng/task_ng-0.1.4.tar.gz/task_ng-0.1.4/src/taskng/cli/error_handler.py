"""Error handling for Task-NG CLI."""

import json
import sys

from rich.console import Console

from taskng.cli.output import is_json_mode
from taskng.core.exceptions import (
    ConfigurationError,
    DatabaseError,
    InvalidFilterError,
    TaskNGError,
    TaskNotFoundError,
)

console = Console(stderr=True)


def handle_error(error: Exception, debug: bool = False) -> None:
    """Handle exception with appropriate output.

    Args:
        error: The exception to handle.
        debug: Whether to show debug info (stack traces).
    """
    # JSON mode outputs errors as JSON
    if is_json_mode():
        error_data = {
            "error": type(error).__name__,
            "message": str(error),
        }
        print(json.dumps(error_data, indent=2), file=sys.stderr)
        sys.exit(1)

    if isinstance(error, TaskNotFoundError):
        console.print(f"[red]Error:[/red] Task {error.task_id} not found")
        console.print("[dim]Use 'task-ng list' to see available tasks[/dim]")
        sys.exit(1)

    elif isinstance(error, InvalidFilterError):
        console.print(f"[red]Error:[/red] Invalid filter: {error}")
        console.print("[dim]Example filters: project:Work, priority:H, +tag[/dim]")
        sys.exit(1)

    elif isinstance(error, ConfigurationError):
        console.print(f"[red]Error:[/red] Configuration error: {error}")
        console.print("[dim]Check ~/.config/taskng/config.toml[/dim]")
        sys.exit(1)

    elif isinstance(error, DatabaseError):
        console.print(f"[red]Error:[/red] Database error: {error}")
        if debug:
            console.print_exception()
        sys.exit(2)

    elif isinstance(error, TaskNGError):
        console.print(f"[red]Error:[/red] {error}")
        sys.exit(1)

    else:
        # Unexpected error
        console.print(f"[red]Unexpected error:[/red] {error}")
        if debug:
            console.print_exception()
        else:
            console.print("[dim]Run with --debug for details[/dim]")
        sys.exit(2)
