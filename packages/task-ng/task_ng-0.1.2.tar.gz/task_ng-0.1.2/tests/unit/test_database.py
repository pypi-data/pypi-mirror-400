"""Tests for database module."""

import sqlite3

import pytest

from taskng.storage.database import Database


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database."""
    db_path = tmp_path / "test.db"
    db = Database(db_path)
    db.initialize()
    return db


class TestDatabase:
    """Tests for Database class."""

    def test_database_creation(self, tmp_path):
        """Database file should be created."""
        db_path = tmp_path / "test.db"
        db = Database(db_path)
        db.initialize()
        assert db.exists
        assert db_path.exists()

    def test_directory_creation(self, tmp_path):
        """Parent directories should be created."""
        db_path = tmp_path / "subdir" / "test.db"
        db = Database(db_path)
        assert db_path.parent.exists()
        assert db.db_path == db_path

    def test_connection_context(self, temp_db):
        """Connection context manager should work."""
        with temp_db.connection() as conn:
            result = conn.execute("SELECT 1").fetchone()
            assert result[0] == 1

    def test_cursor_context(self, temp_db):
        """Cursor context manager should work."""
        with temp_db.cursor() as cur:
            cur.execute("SELECT 1")
            result = cur.fetchone()
            assert result[0] == 1

    def test_foreign_keys_enabled(self, temp_db):
        """Foreign keys should be enabled."""
        with temp_db.connection() as conn:
            result = conn.execute("PRAGMA foreign_keys").fetchone()
            assert result[0] == 1

    def test_wal_mode_enabled(self, temp_db):
        """WAL journal mode should be enabled."""
        with temp_db.connection() as conn:
            result = conn.execute("PRAGMA journal_mode").fetchone()
            assert result[0] == "wal"

    def test_row_factory(self, temp_db):
        """Row factory should return dict-like objects."""
        with temp_db.cursor() as cur:
            cur.execute("SELECT 1 as num, 'test' as str")
            row = cur.fetchone()
            assert row["num"] == 1
            assert row["str"] == "test"

    def test_rollback_on_error(self, temp_db):
        """Transaction should rollback on error."""
        try:
            with temp_db.connection() as conn:
                conn.execute(
                    "INSERT INTO tasks (uuid, description, entry, modified) "
                    "VALUES ('test', 'Test', '2024-01-01', '2024-01-01')"
                )
                raise ValueError("Intentional error")
        except ValueError:
            pass

        # Should have rolled back
        with temp_db.cursor() as cur:
            cur.execute("SELECT COUNT(*) FROM tasks")
            assert cur.fetchone()[0] == 0

    def test_exists_false_before_init(self, tmp_path):
        """exists should return False before initialization."""
        db_path = tmp_path / "new.db"
        db = Database(db_path)
        assert not db.exists


class TestSchema:
    """Tests for database schema."""

    def test_tables_created(self, temp_db):
        """All tables should be created."""
        with temp_db.cursor() as cur:
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
            )
            tables = {row[0] for row in cur.fetchall()}

        expected = {
            "tasks",
            "tags",
            "dependencies",
            "annotations",
            "uda_values",
            "task_history",
        }
        assert expected.issubset(tables)

    def test_indexes_created(self, temp_db):
        """Indexes should be created."""
        with temp_db.cursor() as cur:
            cur.execute(
                "SELECT name FROM sqlite_master WHERE type='index' "
                "AND name LIKE 'idx_%'"
            )
            indexes = {row[0] for row in cur.fetchall()}

        assert "idx_tasks_status" in indexes
        assert "idx_tasks_due" in indexes
        assert "idx_tags_tag" in indexes

    def test_foreign_key_constraint(self, temp_db):
        """Foreign key constraints should work."""
        with temp_db.cursor() as cur, pytest.raises(sqlite3.IntegrityError):
            cur.execute(
                "INSERT INTO tags (task_uuid, tag) VALUES (?, ?)",
                ("nonexistent-uuid", "test"),
            )

    def test_schema_idempotent(self, temp_db):
        """Schema can be applied multiple times."""
        # Should not raise
        temp_db.initialize()
        temp_db.initialize()
