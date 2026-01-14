"""Pytest fixtures for Task-NG tests."""

import pytest
from typer.testing import CliRunner

from taskng.cli.output import set_json_mode
from taskng.config import settings
from taskng.core.context import set_current_context
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository


@pytest.fixture(autouse=True)
def reset_json_mode():
    """Reset JSON mode before each test."""
    set_json_mode(False)
    yield
    set_json_mode(False)


@pytest.fixture(autouse=True)
def reset_context(isolate_test_data):
    """Clear context before each test.

    Depends on isolate_test_data to ensure config paths are set first.
    """
    from taskng.core.context import clear_temporary_context

    # Clear context state and temporary filters
    set_current_context(None)
    clear_temporary_context()
    yield
    # Clean up after test - be thorough to prevent leakage
    set_current_context(None)
    clear_temporary_context()
    # Reset config to clear any custom paths set during test
    settings.reset_config()


@pytest.fixture(autouse=True)
def isolate_test_data(tmp_path):
    """Isolate each test with its own data and config directories.

    This ensures tests never pollute the production database.
    """
    # Reset any previous settings
    settings.reset_config()

    # Set up isolated directories
    data_dir = tmp_path / "data"
    config_dir = tmp_path / "config"
    data_dir.mkdir()
    config_dir.mkdir()

    settings.set_data_dir(data_dir)
    settings.set_config_path(config_dir / "config.toml")

    yield data_dir

    # Clean up
    settings.reset_config()


@pytest.fixture
def cli_runner():
    """Create a CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_db_path(isolate_test_data):
    """Get the temporary database path."""
    return isolate_test_data / "task.db"


@pytest.fixture
def temp_db(temp_db_path):
    """Create and initialize a temporary database."""
    db = Database(temp_db_path)
    db.initialize()
    return db


@pytest.fixture
def task_repo(temp_db):
    """Create a repository with temp database."""
    return TaskRepository(temp_db)
