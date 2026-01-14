"""Unit tests for Kanban board models and functions."""

import pytest

from taskng.core.boards import (
    BoardDefinition,
    BoardNotFoundError,
    ColumnDefinition,
    get_board,
    list_boards,
)


class TestColumnDefinition:
    """Tests for ColumnDefinition model."""

    def test_basic_column(self):
        col = ColumnDefinition(name="Backlog")
        assert col.name == "Backlog"
        assert col.filter == []
        assert col.limit is None

    def test_column_with_filter(self):
        col = ColumnDefinition(name="Active", filter=["+ACTIVE", "status:pending"])
        assert col.name == "Active"
        assert col.filter == ["+ACTIVE", "status:pending"]

    def test_column_with_limit(self):
        col = ColumnDefinition(name="Done", filter=["status:completed"], limit=5)
        assert col.limit == 5


class TestBoardDefinition:
    """Tests for BoardDefinition model."""

    def test_minimal_board(self):
        board = BoardDefinition(name="test")
        assert board.name == "test"
        assert board.description == ""
        assert board.columns == []
        assert board.card_fields == ["id", "priority", "description", "due"]
        assert board.filter == []
        assert board.sort == ["urgency-"]
        assert board.limit == 10
        assert board.column_width == 30

    def test_full_board(self):
        columns = [
            ColumnDefinition(name="Todo", filter=["status:pending"]),
            ColumnDefinition(name="Done", filter=["status:completed"]),
        ]
        board = BoardDefinition(
            name="sprint",
            description="Sprint board",
            columns=columns,
            card_fields=["id", "description", "tags"],
            filter=["project:Engineering"],
            sort=["due+"],
            limit=8,
            column_width=30,
        )
        assert board.name == "sprint"
        assert board.description == "Sprint board"
        assert len(board.columns) == 2
        assert board.card_fields == ["id", "description", "tags"]
        assert board.filter == ["project:Engineering"]
        assert board.sort == ["due+"]
        assert board.limit == 8
        assert board.column_width == 30


class TestGetBoard:
    """Tests for get_board function."""

    def test_get_default_board(self):
        board = get_board("default")
        assert board.name == "default"
        assert board.description == "Task board by status"
        assert len(board.columns) == 4
        assert board.columns[0].name == "Backlog"
        assert board.columns[1].name == "Blocked"
        assert board.columns[2].name == "Active"
        assert board.columns[3].name == "Done"

    def test_get_priority_board(self):
        board = get_board("priority")
        assert board.name == "priority"
        assert board.description == "Tasks by priority"
        assert len(board.columns) == 4
        assert board.columns[0].name == "High"
        assert board.columns[1].name == "Medium"
        assert board.columns[2].name == "Low"
        assert board.columns[3].name == "None"

    def test_board_not_found(self):
        with pytest.raises(BoardNotFoundError) as exc_info:
            get_board("nonexistent")
        assert "nonexistent" in str(exc_info.value)
        assert exc_info.value.name == "nonexistent"


class TestListBoards:
    """Tests for list_boards function."""

    def test_list_default_boards(self):
        boards = list_boards()
        assert "default" in boards
        assert "priority" in boards
        assert boards == sorted(boards)


class TestBoardNotFoundError:
    """Tests for BoardNotFoundError exception."""

    def test_error_message(self):
        error = BoardNotFoundError("myboard")
        assert str(error) == "Board not found: myboard"
        assert error.name == "myboard"
