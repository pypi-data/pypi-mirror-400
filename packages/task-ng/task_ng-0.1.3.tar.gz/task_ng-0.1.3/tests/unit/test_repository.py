"""Tests for TaskRepository."""

import pytest

from taskng.core.models import Priority, Task, TaskStatus
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.initialize()
    return db


@pytest.fixture
def repo(temp_db):
    """Create a repository with temp database."""
    return TaskRepository(temp_db)


class TestTaskRepository:
    """Tests for TaskRepository."""

    def test_add_task(self, repo):
        """Adding a task should assign ID."""
        task = Task(description="Test task")
        saved = repo.add(task)

        assert saved.id is not None
        assert saved.id > 0

    def test_get_by_id(self, repo):
        """Should retrieve task by ID."""
        task = Task(description="Test task")
        saved = repo.add(task)

        retrieved = repo.get_by_id(saved.id)

        assert retrieved is not None
        assert retrieved.description == "Test task"
        assert retrieved.id == saved.id

    def test_get_by_uuid(self, repo):
        """Should retrieve task by UUID."""
        task = Task(description="Test task")
        saved = repo.add(task)

        retrieved = repo.get_by_uuid(saved.uuid)

        assert retrieved is not None
        assert retrieved.id == saved.id

    def test_get_by_id_not_found(self, repo):
        """Should return None for nonexistent ID."""
        result = repo.get_by_id(9999)
        assert result is None

    def test_tags_saved(self, repo):
        """Tags should be saved and loaded."""
        task = Task(description="Test", tags=["urgent", "work"])
        saved = repo.add(task)

        retrieved = repo.get_by_id(saved.id)

        assert set(retrieved.tags) == {"urgent", "work"}

    def test_list_pending(self, repo):
        """Should list only pending tasks."""
        # Add pending task
        pending = Task(description="Pending")
        repo.add(pending)

        # Add completed task
        completed = Task(description="Completed", status=TaskStatus.COMPLETED)
        repo.add(completed)

        tasks = repo.list_pending()

        assert len(tasks) == 1
        assert tasks[0].description == "Pending"

    def test_update_task(self, repo):
        """Should update task attributes."""
        task = Task(description="Original")
        saved = repo.add(task)

        saved.description = "Updated"
        saved.priority = Priority.HIGH
        repo.update(saved)

        retrieved = repo.get_by_id(saved.id)

        assert retrieved.description == "Updated"
        assert retrieved.priority == Priority.HIGH

    def test_update_tags(self, repo):
        """Should update tags on modification."""
        task = Task(description="Test", tags=["old"])
        saved = repo.add(task)

        saved.tags = ["new", "tags"]
        repo.update(saved)

        retrieved = repo.get_by_id(saved.id)

        assert set(retrieved.tags) == {"new", "tags"}

    def test_delete_task(self, repo):
        """Should soft delete task."""
        task = Task(description="To delete")
        saved = repo.add(task)

        result = repo.delete(saved.id)

        assert result is True
        retrieved = repo.get_by_id(saved.id)
        assert retrieved.status == TaskStatus.DELETED

    def test_delete_nonexistent(self, repo):
        """Should return False for nonexistent task."""
        result = repo.delete(9999)
        assert result is False

    def test_history_recorded_on_add(self, repo, temp_db):
        """History should be recorded on add."""
        task = Task(description="Test")
        repo.add(task)

        with temp_db.cursor() as cur:
            cur.execute("SELECT * FROM task_history")
            history = cur.fetchall()

        assert len(history) == 1
        assert history[0]["operation"] == "add"

    def test_history_recorded_on_modify(self, repo, temp_db):
        """History should be recorded on modify."""
        task = Task(description="Test")
        saved = repo.add(task)

        saved.description = "Modified"
        repo.update(saved)

        with temp_db.cursor() as cur:
            cur.execute("SELECT * FROM task_history ORDER BY id")
            history = cur.fetchall()

        assert len(history) == 2
        assert history[1]["operation"] == "modify"

    def test_multiple_tasks(self, repo):
        """Should handle multiple tasks."""
        for i in range(5):
            repo.add(Task(description=f"Task {i}"))

        tasks = repo.list_pending()
        assert len(tasks) == 5

    def test_task_with_all_fields(self, repo):
        """Should save and load all task fields."""
        task = Task(
            description="Full task",
            priority=Priority.HIGH,
            project="Work.Project",
            tags=["urgent", "important"],
        )
        saved = repo.add(task)

        retrieved = repo.get_by_id(saved.id)

        assert retrieved.description == "Full task"
        assert retrieved.priority == Priority.HIGH
        assert retrieved.project == "Work.Project"
        assert set(retrieved.tags) == {"urgent", "important"}
