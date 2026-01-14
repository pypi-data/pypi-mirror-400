"""Task repository for database operations."""

import sqlite3
from datetime import datetime

from taskng.core.filters import Filter, FilterParser
from taskng.core.models import Priority, Task, TaskStatus
from taskng.storage.database import Database


class TaskRepository:
    """Repository for task database operations."""

    def __init__(self, database: Database):
        """Initialize repository with database.

        Args:
            database: Database instance to use.
        """
        self.db = database

    def add(self, task: Task) -> Task:
        """Add a new task to the database.

        Args:
            task: Task to add.

        Returns:
            Task with assigned ID.
        """
        with self.db.connection() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (
                    uuid, description, status, priority, project,
                    entry, modified, due, scheduled, wait, until,
                    start, end, recur, parent_uuid, urgency, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    task.uuid,
                    task.description,
                    task.status.value,
                    task.priority.value if task.priority else None,
                    task.project,
                    task.entry.isoformat(),
                    task.modified.isoformat(),
                    task.due.isoformat() if task.due else None,
                    task.scheduled.isoformat() if task.scheduled else None,
                    task.wait.isoformat() if task.wait else None,
                    task.until.isoformat() if task.until else None,
                    task.start.isoformat() if task.start else None,
                    task.end.isoformat() if task.end else None,
                    task.recur,
                    task.parent_uuid,
                    task.urgency,
                    task.notes,
                ),
            )
            task.id = cursor.lastrowid

            # Insert tags
            self._save_tags(conn, task.uuid, task.tags)

            # Insert annotations
            self._save_annotations(conn, task.uuid, task.annotations)

            # Insert dependencies
            self._save_dependencies(conn, task.uuid, task.depends)

            # Insert UDAs
            self._save_uda(conn, task.uuid, task.uda)

            # Record history
            self._record_history(conn, task.uuid, "add", None, task)

        return task

    def get_by_id(self, task_id: int) -> Task | None:
        """Get a task by its ID.

        Args:
            task_id: Task ID.

        Returns:
            Task if found, None otherwise.
        """
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE id = ?", (task_id,))
            row = cur.fetchone()
            if row:
                return self._row_to_task(row, cur)
        return None

    def get_by_uuid(self, uuid: str) -> Task | None:
        """Get a task by its UUID.

        Args:
            uuid: Task UUID.

        Returns:
            Task if found, None otherwise.
        """
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM tasks WHERE uuid = ?", (uuid,))
            row = cur.fetchone()
            if row:
                return self._row_to_task(row, cur)
        return None

    def list_pending(self) -> list[Task]:
        """Get all pending tasks.

        Returns:
            List of pending tasks sorted by urgency.
        """
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT * FROM tasks WHERE status = ? ORDER BY urgency DESC",
                (TaskStatus.PENDING.value,),
            )
            return [self._row_to_task(row, cur) for row in cur.fetchall()]

    def list_filtered(self, filters: list[Filter]) -> list[Task]:
        """List tasks matching filters.

        Args:
            filters: List of Filter objects.

        Returns:
            List of matching tasks sorted by urgency.
        """
        parser = FilterParser()
        where_clause, params = parser.to_sql(filters)

        with self.db.cursor() as cur:
            cur.execute(
                f"SELECT * FROM tasks WHERE {where_clause} ORDER BY urgency DESC",
                params,
            )
            tasks = [self._row_to_task(row, cur) for row in cur.fetchall()]

        # Apply virtual tag filters (can't be done in SQL)
        if parser.has_virtual_filters(filters):
            all_tasks = (
                self.list_all()
                if any(
                    f.value in ("BLOCKED", "READY")
                    for f in filters
                    if f.operator in ("virtual", "not_virtual")
                )
                else None
            )
            tasks = parser.apply_virtual_filters(tasks, filters, all_tasks)

        return tasks

    def list_all(self) -> list[Task]:
        """Get all tasks regardless of status.

        Returns:
            List of all tasks.
        """
        with self.db.cursor() as cur:
            cur.execute("SELECT * FROM tasks ORDER BY id")
            return [self._row_to_task(row, cur) for row in cur.fetchall()]

    def update(self, task: Task) -> Task:
        """Update an existing task.

        Args:
            task: Task with updated values.

        Returns:
            Updated task.
        """
        old_task = self.get_by_id(task.id) if task.id else None
        task.modified = datetime.now()

        with self.db.connection() as conn:
            conn.execute(
                """
                UPDATE tasks SET
                    description = ?, status = ?, priority = ?, project = ?,
                    modified = ?, due = ?, scheduled = ?, wait = ?, until = ?,
                    start = ?, end = ?, recur = ?, parent_uuid = ?, urgency = ?,
                    notes = ?
                WHERE id = ?
                """,
                (
                    task.description,
                    task.status.value,
                    task.priority.value if task.priority else None,
                    task.project,
                    task.modified.isoformat(),
                    task.due.isoformat() if task.due else None,
                    task.scheduled.isoformat() if task.scheduled else None,
                    task.wait.isoformat() if task.wait else None,
                    task.until.isoformat() if task.until else None,
                    task.start.isoformat() if task.start else None,
                    task.end.isoformat() if task.end else None,
                    task.recur,
                    task.parent_uuid,
                    task.urgency,
                    task.notes,
                    task.id,
                ),
            )

            # Update tags
            self._save_tags(conn, task.uuid, task.tags)

            # Update annotations
            self._save_annotations(conn, task.uuid, task.annotations)

            # Update dependencies
            self._save_dependencies(conn, task.uuid, task.depends)

            # Update UDAs
            self._save_uda(conn, task.uuid, task.uda)

            # Record history
            self._record_history(conn, task.uuid, "modify", old_task, task)

        return task

    def delete(self, task_id: int) -> bool:
        """Soft delete a task.

        Args:
            task_id: Task ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        task.status = TaskStatus.DELETED
        self.update(task)
        return True

    def hard_delete(self, task_id: int) -> bool:
        """Permanently delete a task from database.

        Args:
            task_id: Task ID to delete.

        Returns:
            True if deleted, False if not found.
        """
        task = self.get_by_id(task_id)
        if not task:
            return False

        with self.db.connection() as conn:
            # Delete related data first
            conn.execute("DELETE FROM tags WHERE task_uuid = ?", (task.uuid,))
            conn.execute("DELETE FROM annotations WHERE task_uuid = ?", (task.uuid,))
            conn.execute("DELETE FROM dependencies WHERE task_uuid = ?", (task.uuid,))
            conn.execute(
                "DELETE FROM dependencies WHERE depends_on_uuid = ?", (task.uuid,)
            )
            conn.execute("DELETE FROM task_history WHERE task_uuid = ?", (task.uuid,))
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))

        return True

    def get_unique_projects(self) -> list[str]:
        """Get all unique project names.

        Returns:
            Sorted list of project names.
        """
        with self.db.cursor() as cur:
            cur.execute(
                "SELECT DISTINCT project FROM tasks WHERE project IS NOT NULL ORDER BY project"
            )
            return [row[0] for row in cur.fetchall()]

    def get_unique_tags(self) -> list[str]:
        """Get all unique tag names.

        Returns:
            Sorted list of tag names.
        """
        with self.db.cursor() as cur:
            cur.execute("SELECT DISTINCT name FROM tags ORDER BY name")
            return [row[0] for row in cur.fetchall()]

    def _row_to_task(self, row: "sqlite3.Row", cursor: "sqlite3.Cursor") -> Task:
        """Convert a database row to a Task model.

        Args:
            row: Database row.
            cursor: Cursor for loading related data.

        Returns:
            Task model.
        """
        # Load tags
        cursor.execute(
            "SELECT tag FROM tags WHERE task_uuid = ?",
            (row["uuid"],),
        )
        tags = [r["tag"] for r in cursor.fetchall()]

        # Load annotations
        cursor.execute(
            "SELECT entry, description FROM annotations WHERE task_uuid = ? "
            "ORDER BY entry",
            (row["uuid"],),
        )
        annotations = [
            {"entry": r["entry"], "description": r["description"]}
            for r in cursor.fetchall()
        ]

        # Load dependencies
        cursor.execute(
            "SELECT depends_on_uuid FROM dependencies WHERE task_uuid = ?",
            (row["uuid"],),
        )
        depends = [r["depends_on_uuid"] for r in cursor.fetchall()]

        # Load UDAs
        cursor.execute(
            "SELECT attribute, value FROM uda_values WHERE task_uuid = ?",
            (row["uuid"],),
        )
        uda = {r["attribute"]: r["value"] for r in cursor.fetchall()}

        return Task(
            id=row["id"],
            uuid=row["uuid"],
            description=row["description"],
            status=TaskStatus(row["status"]),
            priority=Priority(row["priority"]) if row["priority"] else None,
            project=row["project"],
            entry=datetime.fromisoformat(row["entry"]),
            modified=datetime.fromisoformat(row["modified"]),
            due=datetime.fromisoformat(row["due"]) if row["due"] else None,
            scheduled=(
                datetime.fromisoformat(row["scheduled"]) if row["scheduled"] else None
            ),
            wait=datetime.fromisoformat(row["wait"]) if row["wait"] else None,
            until=datetime.fromisoformat(row["until"]) if row["until"] else None,
            start=datetime.fromisoformat(row["start"]) if row["start"] else None,
            end=datetime.fromisoformat(row["end"]) if row["end"] else None,
            recur=row["recur"],
            parent_uuid=row["parent_uuid"],
            urgency=row["urgency"],
            tags=tags,
            annotations=annotations,
            depends=depends,
            uda=uda,
            notes=dict(row).get("notes"),
        )

    def _save_tags(
        self, conn: "sqlite3.Connection", uuid: str, tags: list[str]
    ) -> None:
        """Save tags for a task.

        Args:
            conn: Database connection.
            uuid: Task UUID.
            tags: List of tags.
        """
        conn.execute("DELETE FROM tags WHERE task_uuid = ?", (uuid,))
        for tag in tags:
            conn.execute(
                "INSERT INTO tags (task_uuid, tag) VALUES (?, ?)",
                (uuid, tag),
            )

    def _save_annotations(
        self, conn: "sqlite3.Connection", uuid: str, annotations: list[dict[str, str]]
    ) -> None:
        """Save annotations for a task.

        Args:
            conn: Database connection.
            uuid: Task UUID.
            annotations: List of annotation dicts with entry and description.
        """
        conn.execute("DELETE FROM annotations WHERE task_uuid = ?", (uuid,))
        for ann in annotations:
            conn.execute(
                "INSERT INTO annotations (task_uuid, entry, description) VALUES (?, ?, ?)",
                (uuid, ann["entry"], ann["description"]),
            )

    def _save_dependencies(
        self, conn: "sqlite3.Connection", uuid: str, depends: list[str]
    ) -> None:
        """Save dependencies for a task.

        Args:
            conn: Database connection.
            uuid: Task UUID.
            depends: List of dependency UUIDs.
        """
        conn.execute("DELETE FROM dependencies WHERE task_uuid = ?", (uuid,))
        for dep_uuid in depends:
            conn.execute(
                "INSERT INTO dependencies (task_uuid, depends_on_uuid) VALUES (?, ?)",
                (uuid, dep_uuid),
            )

    def _save_uda(
        self, conn: "sqlite3.Connection", uuid: str, uda: dict[str, str]
    ) -> None:
        """Save UDAs for a task.

        Args:
            conn: Database connection.
            uuid: Task UUID.
            uda: Dict of attribute names to values.
        """
        conn.execute("DELETE FROM uda_values WHERE task_uuid = ?", (uuid,))
        for attr, value in uda.items():
            conn.execute(
                "INSERT INTO uda_values (task_uuid, attribute, value) VALUES (?, ?, ?)",
                (uuid, attr, value),
            )

    def _record_history(
        self,
        conn: "sqlite3.Connection",
        uuid: str,
        operation: str,
        old: Task | None,
        new: Task | None,
    ) -> None:
        """Record operation in history table.

        Args:
            conn: Database connection.
            uuid: Task UUID.
            operation: Operation type (add, modify, delete).
            old: Old task state.
            new: New task state.
        """
        conn.execute(
            """
            INSERT INTO task_history (task_uuid, timestamp, operation, old_data, new_data)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                uuid,
                datetime.now().isoformat(),
                operation,
                old.model_dump_json() if old else None,
                new.model_dump_json() if new else None,
            ),
        )

    # Sync-related methods

    def get_unsynced_history(self) -> list[dict[str, object]]:
        """Get all unsynced history entries.

        Returns:
            List of history entry dictionaries.
        """
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, task_uuid, timestamp, operation, old_data, new_data
                FROM task_history
                WHERE synced = 0
                ORDER BY timestamp ASC
                """
            )
            rows = cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "task_uuid": row["task_uuid"],
                    "timestamp": row["timestamp"],
                    "operation": row["operation"],
                    "old_data": row["old_data"],
                    "new_data": row["new_data"],
                }
                for row in rows
            ]

    def get_unsynced_uuids(self) -> list[str]:
        """Get UUIDs of tasks with unsynced changes.

        Returns:
            List of unique task UUIDs.
        """
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT DISTINCT task_uuid
                FROM task_history
                WHERE synced = 0
                """
            )
            return [row["task_uuid"] for row in cur.fetchall()]

    def mark_synced(self, task_uuids: list[str]) -> int:
        """Mark history entries as synced for given tasks.

        Args:
            task_uuids: List of task UUIDs to mark as synced.

        Returns:
            Number of history entries marked.
        """
        if not task_uuids:
            return 0

        with self.db.connection() as conn:
            placeholders = ",".join("?" * len(task_uuids))
            cursor = conn.execute(
                f"""
                UPDATE task_history
                SET synced = 1
                WHERE task_uuid IN ({placeholders}) AND synced = 0
                """,
                task_uuids,
            )
            return cursor.rowcount

    def get_sync_history_for_task(self, task_uuid: str) -> list[dict[str, object]]:
        """Get sync history for a specific task.

        Args:
            task_uuid: Task UUID.

        Returns:
            List of history entries for the task.
        """
        with self.db.cursor() as cur:
            cur.execute(
                """
                SELECT id, task_uuid, timestamp, operation, old_data, new_data, synced
                FROM task_history
                WHERE task_uuid = ?
                ORDER BY timestamp DESC
                """,
                (task_uuid,),
            )
            rows = cur.fetchall()
            return [
                {
                    "id": row["id"],
                    "task_uuid": row["task_uuid"],
                    "timestamp": row["timestamp"],
                    "operation": row["operation"],
                    "old_data": row["old_data"],
                    "new_data": row["new_data"],
                    "synced": bool(row["synced"]),
                }
                for row in rows
            ]
