"""Unit tests for init functionality."""

import pytest
import typer

from taskng.cli.commands.init import init_local


class TestInitLocal:
    """Test init_local() function."""

    def test_init_creates_directory(self, tmp_path, monkeypatch):
        """Should create .taskng directory."""
        monkeypatch.chdir(tmp_path)

        init_local()

        local_dir = tmp_path / ".taskng"
        assert local_dir.exists()
        assert local_dir.is_dir()

    def test_init_creates_config_file(self, tmp_path, monkeypatch):
        """Should create config.toml file."""
        monkeypatch.chdir(tmp_path)

        init_local()

        config_file = tmp_path / ".taskng" / "config.toml"
        assert config_file.exists()
        assert config_file.is_file()
        content = config_file.read_text()
        assert "Task-NG Configuration" in content
        assert len(content) > 1000  # Comprehensive config

    def test_init_creates_database(self, tmp_path, monkeypatch):
        """Should create and initialize database."""
        monkeypatch.chdir(tmp_path)

        init_local()

        db_file = tmp_path / ".taskng" / "task.db"
        assert db_file.exists()
        assert db_file.is_file()

    def test_init_fails_when_directory_exists(self, tmp_path, monkeypatch):
        """Should fail when .taskng directory already exists."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()

        with pytest.raises(typer.Exit) as exc_info:
            init_local()

        assert exc_info.value.exit_code == 1

    def test_init_with_force_overwrites_existing(self, tmp_path, monkeypatch):
        """Should overwrite existing directory with --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()
        # Create a file that would be left if not overwriting
        old_file = local_dir / "old_file.txt"
        old_file.write_text("old content")

        init_local(force=True)

        # Directory should still exist
        assert local_dir.exists()
        # New files should be created
        assert (local_dir / "config.toml").exists()
        assert (local_dir / "task.db").exists()
        # Old file should still exist (force doesn't delete, just allows overwrite)
        assert old_file.exists()

    def test_init_creates_valid_database_schema(self, tmp_path, monkeypatch):
        """Should create database with proper schema."""
        monkeypatch.chdir(tmp_path)

        init_local()

        db_file = tmp_path / ".taskng" / "task.db"
        # Verify database has tables by checking file size
        assert db_file.stat().st_size > 0

    def test_init_in_nested_directory(self, tmp_path, monkeypatch):
        """Should work in nested directory structure."""
        nested_dir = tmp_path / "project" / "subdir"
        nested_dir.mkdir(parents=True)
        monkeypatch.chdir(nested_dir)

        init_local()

        local_dir = nested_dir / ".taskng"
        assert local_dir.exists()
        assert (local_dir / "config.toml").exists()
        assert (local_dir / "task.db").exists()

    def test_init_with_existing_config_and_force(self, tmp_path, monkeypatch):
        """Should overwrite config file with --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()
        config_file = local_dir / "config.toml"
        config_file.write_text("old config content")

        init_local(force=True)

        # Config should be overwritten with new comprehensive template
        content = config_file.read_text()
        assert "Task-NG Configuration" in content
        assert "old config content" not in content
        assert len(content) > 1000  # Should be comprehensive

    def test_init_with_existing_database_and_force(self, tmp_path, monkeypatch):
        """Should reinitialize database with --force."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()
        db_file = local_dir / "task.db"
        # Create a simple empty file (simulating old/corrupt database)
        db_file.write_bytes(b"")

        init_local(force=True)

        # Database should be reinitialized with proper schema
        assert db_file.exists()
        assert db_file.stat().st_size > 0

    def test_init_creates_parent_directories(self, tmp_path, monkeypatch):
        """Should create parent directories if needed."""
        monkeypatch.chdir(tmp_path)

        init_local()

        # .taskng directory should be created even if it didn't exist
        local_dir = tmp_path / ".taskng"
        assert local_dir.exists()

    def test_init_success_message(self, tmp_path, monkeypatch, capsys):
        """Should print success message."""
        monkeypatch.chdir(tmp_path)

        init_local()

        captured = capsys.readouterr()
        assert "Initialized task-ng" in captured.out
        assert ".taskng" in captured.out
        assert "Config:" in captured.out
        assert "Database:" in captured.out

    def test_init_error_message_without_force(self, tmp_path, monkeypatch, capsys):
        """Should print error message when directory exists."""
        monkeypatch.chdir(tmp_path)
        local_dir = tmp_path / ".taskng"
        local_dir.mkdir()

        with pytest.raises(typer.Exit):
            init_local()

        captured = capsys.readouterr()
        assert "Error:" in captured.out
        assert "already exists" in captured.out
        assert "--force" in captured.out
