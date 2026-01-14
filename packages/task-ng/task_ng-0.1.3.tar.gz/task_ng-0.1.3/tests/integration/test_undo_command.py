"""Integration tests for task undo command."""

from taskng.cli.main import app
from taskng.core.models import TaskStatus
from taskng.storage.repository import TaskRepository


class TestUndoCommand:
    """Integration tests for undo command."""

    def test_undo_nothing(self, temp_db, cli_runner):
        """Should show message when nothing to undo."""
        result = cli_runner.invoke(app, ["undo"])
        assert result.exit_code == 0
        assert "Nothing to undo" in result.output

    def test_undo_no_database(self, temp_db_path, cli_runner):
        """Should show message when no database exists."""
        result = cli_runner.invoke(app, ["undo"])
        assert result.exit_code == 0
        assert "Nothing to undo" in result.output

    def test_undo_add(self, temp_db, cli_runner):
        """Should undo task add by removing task."""
        cli_runner.invoke(app, ["add", "Test task"])

        # Verify task exists
        repo = TaskRepository(temp_db)
        assert repo.get_by_id(1) is not None

        result = cli_runner.invoke(app, ["undo"])

        assert result.exit_code == 0
        assert "Undone: task add" in result.output
        assert "Removed task" in result.output

        # Task should be gone
        assert repo.get_by_id(1) is None

    def test_undo_modify(self, temp_db, cli_runner):
        """Should undo task modify by restoring old values."""
        cli_runner.invoke(app, ["add", "Original"])
        cli_runner.invoke(app, ["modify", "1", "--description", "Modified"])

        # Verify modification
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.description == "Modified"

        result = cli_runner.invoke(app, ["undo"])

        assert result.exit_code == 0
        assert "Undone: task modify" in result.output

        # Should be restored
        task = repo.get_by_id(1)
        assert task.description == "Original"

    def test_undo_modify_project(self, temp_db, cli_runner):
        """Should undo project modification."""
        cli_runner.invoke(app, ["add", "Task", "--project", "Original"])
        cli_runner.invoke(app, ["modify", "1", "--project", "Changed"])

        repo = TaskRepository(temp_db)
        assert repo.get_by_id(1).project == "Changed"

        cli_runner.invoke(app, ["undo"])

        task = repo.get_by_id(1)
        assert task.project == "Original"

    def test_undo_modify_tags(self, temp_db, cli_runner):
        """Should undo tag modifications."""
        cli_runner.invoke(app, ["add", "Task +original"])
        cli_runner.invoke(app, ["modify", "1", "--tag", "added"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert "added" in task.tags

        cli_runner.invoke(app, ["undo"])

        task = repo.get_by_id(1)
        assert "original" in task.tags
        assert "added" not in task.tags

    def test_undo_done(self, temp_db, cli_runner):
        """Should undo task done by restoring pending status."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["done", "1"])

        # Verify completed
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.COMPLETED
        assert task.end is not None

        result = cli_runner.invoke(app, ["undo"])

        assert result.exit_code == 0
        assert "Undone: task modify" in result.output

        # Should be pending again
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.PENDING

    def test_undo_delete(self, temp_db, cli_runner):
        """Should undo task delete by restoring status."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["delete", "1", "--force"])

        # Verify deleted
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.DELETED

        result = cli_runner.invoke(app, ["undo"])

        assert result.exit_code == 0

        # Should be pending again
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.PENDING

    def test_undo_multiple_operations(self, temp_db, cli_runner):
        """Should undo operations in reverse order."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["modify", "1", "--project", "Work"])
        cli_runner.invoke(app, ["modify", "1", "--priority", "H"])

        # First undo - priority
        cli_runner.invoke(app, ["undo"])
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.priority is None

        # Second undo - project
        cli_runner.invoke(app, ["undo"])
        task = repo.get_by_id(1)
        assert task.project is None

        # Third undo - add
        cli_runner.invoke(app, ["undo"])
        assert repo.get_by_id(1) is None

    def test_undo_removes_history_entry(self, temp_db, cli_runner):
        """Should remove history entry after undo."""
        cli_runner.invoke(app, ["add", "Task"])

        # Check history
        with temp_db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM task_history")
            count_before = cur.fetchone()[0]

        cli_runner.invoke(app, ["undo"])

        with temp_db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM task_history")
            count_after = cur.fetchone()[0]

        # All history for this task should be removed (hard delete removes it)
        assert count_after < count_before
