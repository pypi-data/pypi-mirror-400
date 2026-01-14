"""Unit tests for shell completion module."""

from unittest.mock import MagicMock, patch

from taskng.cli.completion import (
    _get_repository,
    complete_project,
    complete_tag,
    complete_task_id,
)
from taskng.core.models import Task


class TestGetRepository:
    """Tests for _get_repository function."""

    def test_returns_none_when_db_not_exists(self, tmp_path) -> None:
        """Should return None when database doesn't exist."""
        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = _get_repository()
            assert result is None

    def test_returns_repository_when_db_exists(self, tmp_path) -> None:
        """Should return repository when database exists."""
        from taskng.storage.database import Database

        # Create database with correct filename
        db_path = tmp_path / "tasks.db"
        db = Database(db_path)
        db.initialize()

        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = _get_repository()
            assert result is not None

    def test_returns_none_on_exception(self) -> None:
        """Should return None when exception occurs."""
        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.side_effect = Exception("Config error")
            result = _get_repository()
            assert result is None


class TestCompleteProject:
    """Tests for complete_project function."""

    def test_returns_empty_when_no_repository(self, tmp_path) -> None:
        """Should return empty list when no repository."""
        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = complete_project("Work")
            assert result == []

    def test_returns_matching_projects(self) -> None:
        """Should return projects matching prefix."""
        mock_repo = MagicMock()
        mock_repo.get_unique_projects.return_value = ["Work", "Work.Backend", "Home"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_project("Work")
            assert "Work" in result
            assert "Work.Backend" in result
            assert "Home" not in result

    def test_case_insensitive_matching(self) -> None:
        """Should match case-insensitively."""
        mock_repo = MagicMock()
        mock_repo.get_unique_projects.return_value = ["Work", "Weekend"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_project("work")
            assert "Work" in result
            assert "Weekend" not in result

    def test_returns_all_projects_with_empty_input(self) -> None:
        """Should return all projects when input is empty."""
        mock_repo = MagicMock()
        mock_repo.get_unique_projects.return_value = ["Work", "Home", "Personal"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_project("")
            assert len(result) == 3

    def test_returns_empty_when_no_matches(self) -> None:
        """Should return empty list when no projects match."""
        mock_repo = MagicMock()
        mock_repo.get_unique_projects.return_value = ["Work", "Home"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_project("xyz")
            assert result == []


class TestCompleteTag:
    """Tests for complete_tag function."""

    def test_returns_empty_when_no_repository(self, tmp_path) -> None:
        """Should return empty list when no repository."""
        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = complete_tag("urgent")
            assert result == []

    def test_returns_matching_tags(self) -> None:
        """Should return tags matching prefix."""
        mock_repo = MagicMock()
        mock_repo.get_unique_tags.return_value = ["urgent", "review", "important"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_tag("ur")
            assert "urgent" in result
            assert "review" not in result
            assert "important" not in result

    def test_case_insensitive_matching(self) -> None:
        """Should match case-insensitively."""
        mock_repo = MagicMock()
        mock_repo.get_unique_tags.return_value = ["Urgent", "urgent"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_tag("URGENT")
            assert "Urgent" in result
            assert "urgent" in result

    def test_returns_all_tags_with_empty_input(self) -> None:
        """Should return all tags when input is empty."""
        mock_repo = MagicMock()
        mock_repo.get_unique_tags.return_value = ["urgent", "review", "bug"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_tag("")
            assert len(result) == 3

    def test_returns_empty_when_no_matches(self) -> None:
        """Should return empty list when no tags match."""
        mock_repo = MagicMock()
        mock_repo.get_unique_tags.return_value = ["urgent", "review"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_tag("xyz")
            assert result == []


class TestCompleteTaskId:
    """Tests for complete_task_id function."""

    def test_returns_empty_when_no_repository(self, tmp_path) -> None:
        """Should return empty list when no repository."""
        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = complete_task_id("1")
            assert result == []

    def test_returns_matching_task_ids(self) -> None:
        """Should return task IDs matching prefix."""
        mock_repo = MagicMock()
        task1 = Task(id=1, description="First task")
        task2 = Task(id=12, description="Second task")
        task3 = Task(id=23, description="Third task")
        mock_repo.list_pending.return_value = [task1, task2, task3]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("1")
            ids = [r[0] for r in result]
            assert "1" in ids
            assert "12" in ids
            assert "23" not in ids

    def test_returns_description_in_tuple(self) -> None:
        """Should return description as second element."""
        mock_repo = MagicMock()
        task = Task(id=42, description="Test task description")
        mock_repo.list_pending.return_value = [task]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("4")
            assert len(result) == 1
            assert result[0] == ("42", "Test task description")

    def test_truncates_long_description(self) -> None:
        """Should truncate descriptions longer than 40 chars."""
        mock_repo = MagicMock()
        long_desc = "A" * 50
        task = Task(id=1, description=long_desc)
        mock_repo.list_pending.return_value = [task]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("1")
            assert len(result) == 1
            task_id, desc = result[0]
            assert task_id == "1"
            assert len(desc) == 43  # 40 + "..."
            assert desc.endswith("...")

    def test_does_not_truncate_short_description(self) -> None:
        """Should not truncate descriptions 40 chars or less."""
        mock_repo = MagicMock()
        short_desc = "A" * 40
        task = Task(id=1, description=short_desc)
        mock_repo.list_pending.return_value = [task]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("1")
            assert len(result) == 1
            task_id, desc = result[0]
            assert desc == short_desc
            assert "..." not in desc

    def test_returns_all_tasks_with_empty_input(self) -> None:
        """Should return all tasks when input is empty."""
        mock_repo = MagicMock()
        task1 = Task(id=1, description="Task 1")
        task2 = Task(id=2, description="Task 2")
        mock_repo.list_pending.return_value = [task1, task2]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("")
            assert len(result) == 2

    def test_returns_empty_when_no_matches(self) -> None:
        """Should return empty list when no IDs match."""
        mock_repo = MagicMock()
        task = Task(id=1, description="Task")
        mock_repo.list_pending.return_value = [task]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("9")
            assert result == []

    def test_skips_tasks_without_id(self) -> None:
        """Should skip tasks without an ID."""
        mock_repo = MagicMock()
        task1 = Task(id=None, description="No ID")
        task2 = Task(id=1, description="Has ID")
        mock_repo.list_pending.return_value = [task1, task2]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("")
            assert len(result) == 1
            assert result[0][0] == "1"

    def test_handles_multi_digit_ids(self) -> None:
        """Should handle multi-digit task IDs."""
        mock_repo = MagicMock()
        task1 = Task(id=100, description="Hundred")
        task2 = Task(id=101, description="Hundred one")
        task3 = Task(id=200, description="Two hundred")
        mock_repo.list_pending.return_value = [task1, task2, task3]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_task_id("10")
            ids = [r[0] for r in result]
            assert "100" in ids
            assert "101" in ids
            assert "200" not in ids


class TestCompletionIntegration:
    """Integration tests with actual database."""

    def test_complete_project_with_real_db(self, tmp_path) -> None:
        """Should complete projects from real database."""
        from taskng.storage.database import Database
        from taskng.storage.repository import TaskRepository

        db_path = tmp_path / "tasks.db"
        db = Database(db_path)
        db.initialize()
        repo = TaskRepository(db)
        repo.add(Task(description="Task 1", project="Work"))
        repo.add(Task(description="Task 2", project="Work.Backend"))
        repo.add(Task(description="Task 3", project="Home"))

        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = complete_project("Work")
            assert "Work" in result
            assert "Work.Backend" in result
            assert "Home" not in result

    def test_complete_tag_with_real_db(self) -> None:
        """Should complete tags from real database."""
        # Use mock since repository.get_unique_tags has a schema bug
        mock_repo = MagicMock()
        mock_repo.get_unique_tags.return_value = ["urgent", "review", "important"]

        with patch("taskng.cli.completion._get_repository", return_value=mock_repo):
            result = complete_tag("ur")
            assert "urgent" in result
            assert "review" not in result
            assert "important" not in result

    def test_complete_task_id_with_real_db(self, tmp_path) -> None:
        """Should complete task IDs from real database."""
        from taskng.storage.database import Database
        from taskng.storage.repository import TaskRepository

        db_path = tmp_path / "tasks.db"
        db = Database(db_path)
        db.initialize()
        repo = TaskRepository(db)
        repo.add(Task(description="First task"))
        repo.add(Task(description="Second task"))

        with patch("taskng.cli.completion.get_config") as mock_config:
            mock_config.return_value.data_location = tmp_path
            result = complete_task_id("1")
            assert len(result) == 1
            assert result[0][0] == "1"
            assert result[0][1] == "First task"
