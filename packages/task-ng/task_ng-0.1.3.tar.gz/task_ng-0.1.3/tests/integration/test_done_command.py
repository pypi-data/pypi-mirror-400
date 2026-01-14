"""Integration tests for task done command."""

from taskng.cli.main import app
from taskng.core.models import TaskStatus
from taskng.storage.repository import TaskRepository


class TestDoneCommand:
    """Integration tests for done command."""

    def test_done_nonexistent_task(self, temp_db, cli_runner):
        """Should error when task doesn't exist."""
        result = cli_runner.invoke(app, ["done", "999"])
        assert result.exit_code == 1
        assert "not found" in result.output

    def test_done_no_database(self, temp_db_path, cli_runner):
        """Should error when no database exists."""
        result = cli_runner.invoke(app, ["done", "1"])
        assert result.exit_code == 1
        assert "No tasks" in result.output

    def test_done_single_task(self, temp_db, cli_runner):
        """Should complete a single task."""
        cli_runner.invoke(app, ["add", "Test task"])
        result = cli_runner.invoke(app, ["done", "1"])

        assert result.exit_code == 0
        assert "Completed 1 task" in result.output
        assert "Test task" in result.output

        # Verify in database
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.COMPLETED

    def test_done_multiple_tasks(self, temp_db, cli_runner):
        """Should complete multiple tasks."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["add", "Task 3"])

        result = cli_runner.invoke(app, ["done", "1", "2", "3"])

        assert result.exit_code == 0
        assert "Completed 3 task" in result.output

        repo = TaskRepository(temp_db)
        for i in range(1, 4):
            task = repo.get_by_id(i)
            assert task.status == TaskStatus.COMPLETED

    def test_done_sets_end_timestamp(self, temp_db, cli_runner):
        """Should set end timestamp."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["done", "1"])

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.end is not None

    def test_done_already_completed(self, temp_db, cli_runner):
        """Should warn when task already completed."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["done", "1"])
        result = cli_runner.invoke(app, ["done", "1"])

        assert result.exit_code == 1
        assert "already completed" in result.output

    def test_done_partial_success(self, temp_db, cli_runner):
        """Should complete valid tasks and report errors."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])

        result = cli_runner.invoke(app, ["done", "1", "999", "2"])

        assert result.exit_code == 0
        assert "Completed 2 task" in result.output
        assert "not found" in result.output

    def test_done_records_history(self, temp_db, cli_runner):
        """Should record completion in history."""
        cli_runner.invoke(app, ["add", "Task"])
        cli_runner.invoke(app, ["done", "1"])

        with temp_db.cursor() as cur:
            cur.execute(
                "SELECT operation FROM task_history WHERE task_uuid = "
                "(SELECT uuid FROM tasks WHERE id = 1) ORDER BY timestamp"
            )
            operations = [row["operation"] for row in cur.fetchall()]

        assert "add" in operations
        assert "modify" in operations  # done uses update internally

    def test_done_removes_from_pending_list(self, temp_db, cli_runner):
        """Completed task should not appear in pending list."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])
        cli_runner.invoke(app, ["done", "1"])

        repo = TaskRepository(temp_db)
        pending = repo.list_pending()

        assert len(pending) == 1
        assert pending[0].description == "Task 2"

    def test_done_shows_checkmark(self, temp_db, cli_runner):
        """Should show checkmark in output."""
        cli_runner.invoke(app, ["add", "Task"])
        result = cli_runner.invoke(app, ["done", "1"])

        assert "✓" in result.output

    def test_done_truncates_long_description(self, temp_db, cli_runner):
        """Should truncate long descriptions in output."""
        long_desc = "A" * 100
        cli_runner.invoke(app, ["add", long_desc])
        result = cli_runner.invoke(app, ["done", "1"])

        assert result.exit_code == 0
        # Should not show full 100-character description
        assert long_desc not in result.output
        # Should show truncated version (50 chars in done output)
        a_count = result.output.count("A")
        assert a_count == 50, f"Expected 50 A's in truncated output, got {a_count}"

        # Verify task was actually completed despite truncated display
        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)
        assert task.status == TaskStatus.COMPLETED
        assert task.description == long_desc  # Full description preserved in DB
