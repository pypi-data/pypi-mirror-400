"""Kanban board definitions and loading."""

from pydantic import BaseModel

from taskng.config.defaults import DEFAULTS
from taskng.config.settings import get_config
from taskng.core.exceptions import TaskNGError


class BoardNotFoundError(TaskNGError):
    """Board definition not found."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Board not found: {name}")
        self.name = name


class BoardDisabledError(TaskNGError):
    """Board is disabled."""

    def __init__(self, name: str) -> None:
        super().__init__(f"Board is disabled: {name}")
        self.name = name


class ColumnDefinition(BaseModel):
    """Definition of a Kanban board column."""

    name: str
    filter: list[str] = []
    limit: int | None = None
    wip_limit: int | None = None
    since: str | None = None  # Time window for completed tasks, e.g., "7d"


class BoardDefinition(BaseModel):
    """Definition of a Kanban board."""

    name: str
    description: str = ""
    columns: list[ColumnDefinition] = []
    card_fields: list[str] = ["id", "priority", "description", "due"]
    filter: list[str] = []
    sort: list[str] = ["urgency-"]
    limit: int | None = 10
    column_width: int = 30
    enabled: bool = True


def get_board(name: str) -> BoardDefinition:
    """Load a board definition by name.

    Args:
        name: Board name to load.

    Returns:
        BoardDefinition for the named board.

    Raises:
        BoardNotFoundError: If board not found.
        BoardDisabledError: If board is disabled.
    """
    config = get_config()
    default_boards = DEFAULTS.get("board", {})

    # Get default and user configs
    default_config = default_boards.get(name, {})
    user_config = config.get(f"board.{name}") or {}

    # Check if board exists anywhere
    if not default_config and not user_config:
        raise BoardNotFoundError(name)

    # Check if disabled
    if user_config.get("enabled") is False:
        raise BoardDisabledError(name)

    # Merge configs: start with default, override with user
    merged = {**default_config, **user_config}

    # Parse columns from the merged config
    columns = []
    if "columns" in merged:
        for col in merged["columns"]:
            columns.append(ColumnDefinition(**col))
        merged["columns"] = columns

    return BoardDefinition(name=name, **merged)


def list_boards() -> list[str]:
    """List all available board names.

    Returns:
        List of board names from defaults and user config (excluding disabled).
    """
    config = get_config()

    # Get default board names
    default_boards = set(DEFAULTS.get("board", {}).keys())

    # Get user-defined board names and track disabled ones
    user_boards: set[str] = set()
    disabled_boards: set[str] = set()
    board_config = config.get("board")
    if isinstance(board_config, dict):
        for name, board_def in board_config.items():
            if isinstance(board_def, dict) and board_def.get("enabled") is False:
                disabled_boards.add(name)
            else:
                user_boards.add(name)

    # Combine, remove disabled, and sort
    all_boards = (default_boards | user_boards) - disabled_boards
    return sorted(all_boards)
