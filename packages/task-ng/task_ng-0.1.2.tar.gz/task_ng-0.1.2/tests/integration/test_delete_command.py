"""Integration tests for task delete command."""

from taskng.cli.main import app
from taskng.core.models import TaskStatus
from taskng.storage.repository import TaskRepository


class TestDeleteCommand:
    """Integration tests for delete command."""

    def test_delete_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["delete", "999", "--force"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_delete_no_database(self, temp_db_path, cli_runner):
        """Should error when no database exists."""
        result = cli_runner.invoke(app, ["delete", "1", "--force"])
        assert result.exit_code == 1
        assert "No tasks" in result.output

    def test_delete_single_task(self, temp_db, cli_runner):
        """Should delete a single task."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["delete", "1", "--force"])

        assert result.exit_code == 0
        assert "Deleted 1 task" in result.output

        # Verify in database
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.DELETED

    def test_delete_multiple_tasks(self, temp_db, cli_runner):
        """Should delete multiple tasks."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["add", "Task 3"])

        result = cli_runner.invoke(app, ["delete", "1", "2", "3", "--force"])

        assert result.exit_code == 0
        assert "Deleted 3 task" in result.output

        repo = TaskRepository(temp_db)
        for i in range(1, 4):
            task = repo.get_by_id(i)
            assert task.status == TaskStatus.DELETED

    def test_delete_already_deleted(self, temp_db, cli_runner):
        """Should warn when task already deleted."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["delete", "1", "--force"])
        result = cli_runner.invoke(app, ["delete", "1", "--force"])

        assert result.exit_code == 1
        assert "already deleted" in result.output

    def test_delete_removes_from_pending_list(self, temp_db, cli_runner):
        """Deleted task should not appear in pending list."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["delete", "1", "--force"])

        repo = TaskRepository(temp_db)
        pending = repo.list_pending()

        assert len(pending) == 1
        assert pending[0].description == "Task 2"

    def test_delete_shows_task_list(self, temp_db, cli_runner):
        """Should show tasks to be deleted."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["delete", "1", "--force"])

        assert "will be deleted" in result.output
        assert "Test task" in result.output

    def test_delete_records_history(self, temp_db, cli_runner):
        """Should record deletion in history."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["delete", "1", "--force"])

        with temp_db.cursor() as cur:
            cur.execute(
                "SELECT operation FROM task_history WHERE task_uuid = "
                "(SELECT uuid FROM tasks WHERE id = 1) ORDER BY timestamp"
            )
            operations = [row["operation"] for row in cur.fetchall()]

        assert "add" in operations
        assert "modify" in operations  # delete uses update internally

    def test_delete_partial_success(self, temp_db, cli_runner):
        """Should delete valid tasks and report errors."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["delete", "1", "999", "2", "--force"])

        # Should still succeed for valid tasks
        assert "Deleted 2 task" in result.output
        assert "not found" in result.output

    def test_delete_cancelled_without_force(self, temp_db, cli_runner):
        """Should cancel when not confirmed."""
        cli_runner.invoke(app, ["add", "Task"])
        # Simulate 'n' response
        result = cli_runner.invoke(app, ["delete", "1"], input="n\n")

        assert result.exit_code == 0
        assert "Cancelled" in result.output

        # Task should still exist
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.PENDING

    def test_delete_confirmed_without_force(self, temp_db, cli_runner):
        """Should delete when confirmed."""
        cli_runner.invoke(app, ["add", "Task"])
        # Simulate 'y' response
        result = cli_runner.invoke(app, ["delete", "1"], input="y\n")

        assert result.exit_code == 0
        assert "Deleted 1 task" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.DELETED
