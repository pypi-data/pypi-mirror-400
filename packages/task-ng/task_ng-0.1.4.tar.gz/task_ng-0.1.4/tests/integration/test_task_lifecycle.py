"""Integration tests for complete task lifecycle."""

from taskng.cli.main import app
from taskng.storage.repository import TaskRepository


class TestTaskLifecycle:
    """Test complete task lifecycle through CLI."""

    def test_add_and_verify_in_db(self, temp_db, cli_runner):
        """Task added via CLI appears in database."""
        result = cli_runner.invoke(
            app,
            ["add", "Integration test task", "--project", "Testing", "--priority", "H"],
        )
        assert result.exit_code == 0

        # Verify in database
        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()

        assert len(tasks) == 1
        assert tasks[0].description == "Integration test task"
        assert tasks[0].project == "Testing"
        assert tasks[0].priority.value == "H"

    def test_database_persists(self, temp_db, cli_runner):
        """Database persists between operations."""
        # Add task
        cli_runner.invoke(app, ["add", "Persistent task"])

        # Create new repository instance
        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()

        assert len(tasks) == 1
        assert tasks[0].description == "Persistent task"

    def test_history_recorded(self, temp_db, cli_runner):
        """Task history is recorded on add."""
        cli_runner.invoke(app, ["add", "Tracked task"])

        with temp_db.cursor() as cur:
            cur.execute("SELECT * FROM task_history")
            history = cur.fetchall()

        assert len(history) == 1
        assert history[0]["operation"] == "add"

    def test_task_uuid_generated(self, temp_db, cli_runner):
        """Each task gets a unique UUID."""
        cli_runner.invoke(app, ["add", "Task 1"])
        cli_runner.invoke(app, ["add", "Task 2"])

        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()

        assert len(tasks) == 2
        assert tasks[0].uuid != tasks[1].uuid
        assert len(tasks[0].uuid) == 36  # UUID format

    def test_entry_timestamp_set(self, temp_db, cli_runner):
        """Entry timestamp is set on creation."""
        cli_runner.invoke(app, ["add", "Timestamped task"])

        repo = TaskRepository(temp_db)
        task = repo.list_pending()[0]

        assert task.entry is not None
        assert task.modified is not None

    def test_task_retrieval_by_id(self, temp_db, cli_runner):
        """Task can be retrieved by ID after creation."""
        result = cli_runner.invoke(app, ["add", "Retrievable task"])
        assert "Created task 1" in result.output

        repo = TaskRepository(temp_db)
        task = repo.get_by_id(1)

        assert task is not None
        assert task.description == "Retrievable task"

    def test_task_retrieval_by_uuid(self, temp_db, cli_runner):
        """Task can be retrieved by UUID after creation."""
        cli_runner.invoke(app, ["add", "UUID task"])

        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        uuid = tasks[0].uuid

        task = repo.get_by_uuid(uuid)
        assert task is not None
        assert task.description == "UUID task"
