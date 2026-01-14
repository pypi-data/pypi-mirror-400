"""Integration tests for task add command."""

from taskng.cli.main import app
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository


class TestAddCommand:
    """Integration tests for add command."""

    def test_add_simple_task(self, temp_db_path, cli_runner):
        """Should create a task with just a description."""
        result = cli_runner.invoke(app, ["add", "Buy groceries"])
        assert result.exit_code == 0
        assert "Created task 1" in result.output
        assert "Buy groceries" in result.output

        # Verify task was actually created in database
        db = Database(temp_db_path)
        repo = TaskRepository(db)
        tasks = repo.list_pending()
        assert len(tasks) == 1
        assert tasks[0].id == 1
        assert tasks[0].description == "Buy groceries"

    def test_add_with_tags(self, temp_db, cli_runner):
        """Should extract tags from description."""
        result = cli_runner.invoke(app, ["add", "Buy groceries +shopping +urgent"])
        assert result.exit_code == 0
        assert "Created task" in result.output
        assert "+shopping" in result.output
        assert "+urgent" in result.output

        # Verify tags in database
        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        assert len(tasks) == 1
        assert "shopping" in tasks[0].tags
        assert "urgent" in tasks[0].tags
        assert tasks[0].description == "Buy groceries"

    def test_add_with_project(self, temp_db, cli_runner):
        """Should set project from option."""
        result = cli_runner.invoke(app, ["add", "Fix bug", "--project", "Work"])
        assert result.exit_code == 0
        assert "Project:" in result.output
        assert "Work" in result.output

        # Verify in database
        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        assert tasks[0].project == "Work"

    def test_add_with_priority(self, temp_db, cli_runner):
        """Should set priority from option."""
        result = cli_runner.invoke(app, ["add", "Urgent task", "--priority", "H"])
        assert result.exit_code == 0
        assert "Priority:" in result.output

        # Verify in database
        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        assert tasks[0].priority.value == "H"

    def test_add_priority_lowercase(self, temp_db, cli_runner):
        """Should accept lowercase priority."""
        result = cli_runner.invoke(app, ["add", "Task", "--priority", "m"])
        assert result.exit_code == 0

        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        assert tasks[0].priority.value == "M"

    def test_add_invalid_priority(self, temp_db_path, cli_runner):
        """Should reject invalid priority."""
        result = cli_runner.invoke(app, ["add", "Task", "--priority", "X"])
        assert result.exit_code == 1
        assert "Invalid priority" in result.output

    def test_add_with_short_options(self, temp_db, cli_runner):
        """Should accept short option flags."""
        result = cli_runner.invoke(app, ["add", "Task", "-p", "Home", "-P", "L"])
        assert result.exit_code == 0
        assert "Home" in result.output

        repo = TaskRepository(temp_db)
        tasks = repo.list_pending()
        assert tasks[0].project == "Home"
        assert tasks[0].priority.value == "L"

    def test_add_empty_description_with_only_tags(self, temp_db_path, cli_runner):
        """Should reject description that becomes empty after tag extraction."""
        result = cli_runner.invoke(app, ["add", "+tag1 +tag2"])
        assert result.exit_code == 1
        assert "empty" in result.output.lower()

    def test_add_multiple_tasks(self, temp_db, cli_runner):
        """Should assign sequential IDs."""
        cli_runner.invoke(app, ["add", "First task"])
        cli_runner.invoke(app, ["add", "Second task"])
        result = cli_runner.invoke(app, ["add", "Third task"])

        assert result.exit_code == 0
        assert "Created task 3" in result.output

    def test_add_initializes_database(self, temp_db_path, cli_runner):
        """Should auto-initialize database on first run."""
        # Database doesn't exist yet
        assert not temp_db_path.exists()

        result = cli_runner.invoke(app, ["add", "First task"])
        assert result.exit_code == 0

        # Database should now exist
        assert temp_db_path.exists()
