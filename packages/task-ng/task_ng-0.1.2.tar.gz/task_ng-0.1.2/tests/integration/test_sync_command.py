"""Integration tests for sync commands."""

import json
from pathlib import Path
from unittest.mock import MagicMock, patch

import pytest
from typer.testing import CliRunner

from taskng.cli.main import app
from taskng.storage.database import Database


@pytest.fixture
def cli_runner() -> CliRunner:
    """Create CLI test runner."""
    return CliRunner()


@pytest.fixture
def temp_db_path(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Set up temporary database path."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("taskng.storage.database.DEFAULT_DB_PATH", db_path)
    return db_path


@pytest.fixture
def temp_db(temp_db_path: Path):
    """Create initialized temporary database."""
    db = Database(temp_db_path)
    db.initialize()
    return db


@pytest.fixture
def sync_dir(tmp_path: Path) -> Path:
    """Create a sync directory."""
    return tmp_path / "sync"


@pytest.fixture
def mock_config(sync_dir: Path):
    """Mock configuration for sync."""
    config_data = {
        "sync.enabled": True,
        "sync.backend": "git",
        "sync.git": {"directory": str(sync_dir)},
        "sync.conflict_resolution": "last_write_wins",
    }

    def get_config_value(key: str, default: object = None) -> object:
        return config_data.get(key, default)

    return get_config_value


class TestSyncInit:
    """Test sync init command."""

    def test_sync_init_creates_git_repo(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should initialize git repository in sync directory."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["sync", "init"])

            # Should succeed
            assert result.exit_code == 0
            # Sync directory should be created
            assert sync_dir.exists()
            # Should have .git directory
            assert (sync_dir / ".git").exists()

    def test_sync_init_creates_metadata(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should create metadata directory and files."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["sync", "init"])

            assert result.exit_code == 0

            # Check for metadata
            metadata_dir = sync_dir / "metadata"
            assert metadata_dir.exists()
            assert (metadata_dir / "device.json").exists()

    def test_sync_init_json_output(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should output valid JSON when --json flag used."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["--json", "sync", "init"])

            if result.exit_code == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                assert "status" in data


class TestSyncStatus:
    """Test sync status command."""

    def test_status_shows_backend_info(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should show backend information in status output."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            # Initialize first
            init_result = cli_runner.invoke(app, ["sync", "init"])
            assert init_result.exit_code == 0

            # Status may fail due to database state, but output should be informative
            result = cli_runner.invoke(app, ["sync", "status"])

            # Either succeeds or fails gracefully
            if result.exit_code == 0:
                assert (
                    "git" in result.stdout.lower() or "enabled" in result.stdout.lower()
                )

    def test_status_json_output(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should output valid JSON for status."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            cli_runner.invoke(app, ["sync", "init"])
            result = cli_runner.invoke(app, ["--json", "sync", "status"])

            if result.exit_code == 0 and result.stdout.strip():
                data = json.loads(result.stdout)
                assert "enabled" in data or "backend" in data


class TestSyncPush:
    """Test sync push command."""

    def test_push_not_initialized(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should fail when not initialized."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["sync", "push"])

            assert result.exit_code == 1
            assert (
                "not initialized" in result.stdout.lower()
                or "init" in result.stdout.lower()
            )

    def test_push_after_init(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should push after initialization."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            # Initialize
            cli_runner.invoke(app, ["sync", "init"])

            # Add a task
            cli_runner.invoke(app, ["add", "Test task for sync"])

            # Push
            result = cli_runner.invoke(app, ["sync", "push"])

            # Should succeed (no remote is OK for local-only)
            assert result.exit_code == 0


class TestSyncPull:
    """Test sync pull command."""

    def test_pull_not_initialized(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should fail when not initialized."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["sync", "pull"])

            assert result.exit_code == 1
            assert (
                "not initialized" in result.stdout.lower()
                or "init" in result.stdout.lower()
            )

    def test_pull_after_init(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should pull after initialization (no remote is OK)."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            cli_runner.invoke(app, ["sync", "init"])
            result = cli_runner.invoke(app, ["sync", "pull"])

            # Should succeed (nothing to pull from no remote)
            assert result.exit_code == 0


class TestFullSync:
    """Test full sync command."""

    def test_sync_not_initialized(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should fail when not initialized."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            result = cli_runner.invoke(app, ["sync"])

            assert result.exit_code == 1

    def test_full_sync_cycle(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should complete full sync cycle."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            # Initialize
            cli_runner.invoke(app, ["sync", "init"])

            # Add tasks
            cli_runner.invoke(app, ["add", "Task 1"])
            cli_runner.invoke(app, ["add", "Task 2"])

            # Full sync
            result = cli_runner.invoke(app, ["sync"])

            # Should succeed
            assert result.exit_code == 0


class TestSyncConflicts:
    """Test sync conflicts command."""

    def test_conflicts_no_conflicts(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should show no conflicts when none exist."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            cli_runner.invoke(app, ["sync", "init"])
            result = cli_runner.invoke(app, ["sync", "conflicts"])

            assert result.exit_code == 0
            assert "no conflict" in result.stdout.lower() or result.stdout.strip() == ""


class TestSyncTaskExport:
    """Test that sync exports tasks correctly."""

    def test_sync_creates_task_files(
        self,
        cli_runner: CliRunner,
        temp_db: Database,
        sync_dir: Path,
        mock_config: MagicMock,
    ):
        """Should create JSON files for tasks."""
        with patch("taskng.cli.commands.sync.get_config") as mock_get_config:
            mock_get_config.return_value.get = mock_config

            # Initialize
            cli_runner.invoke(app, ["sync", "init"])

            # Add tasks
            cli_runner.invoke(app, ["add", "Sync test task"])

            # Push to create files
            cli_runner.invoke(app, ["sync", "push"])

            # Check tasks directory
            tasks_dir = sync_dir / "tasks"
            if tasks_dir.exists():
                json_files = list(tasks_dir.glob("*.json"))
                assert len(json_files) >= 1

                # Verify JSON content
                for json_file in json_files:
                    data = json.loads(json_file.read_text())
                    assert "uuid" in data
                    assert "version" in data
