"""Undo command implementation."""

import json

from rich.console import Console

from taskng.core.models import TaskStatus
from taskng.storage.database import Database
from taskng.storage.repository import TaskRepository

console = Console()


def undo_last_operation() -> None:
    """Undo the most recent operation."""
    db = Database()
    if not db.exists:
        console.print("[yellow]Nothing to undo[/yellow]")
        return

    repo = TaskRepository(db)

    # Get last operation (non-synced)
    with db.cursor() as cur:
        cur.execute(
            """
            SELECT * FROM task_history
            WHERE synced = 0
            ORDER BY timestamp DESC
            LIMIT 1
            """
        )
        row = cur.fetchone()

    if not row:
        console.print("[yellow]Nothing to undo[/yellow]")
        return

    operation = row["operation"]
    task_uuid = row["task_uuid"]
    old_data = json.loads(row["old_data"]) if row["old_data"] else None
    new_data = json.loads(row["new_data"]) if row["new_data"] else None

    # Apply inverse operation
    if operation == "add":
        # Undo add = hard delete task
        task = repo.get_by_uuid(task_uuid)
        if task and task.id:
            repo.hard_delete(task.id)
        console.print("[green]Undone: task add[/green]")
        if new_data:
            desc = new_data.get("description", "")[:50]
            console.print(f"  Removed task: {desc}")

    elif operation == "modify":
        # Undo modify = restore old values
        if old_data:
            # Restore the old task state
            task = repo.get_by_uuid(task_uuid)
            if task:
                # Update with old data
                task.description = old_data.get("description", task.description)
                task.status = TaskStatus(old_data.get("status", task.status.value))
                task.priority = None
                if old_data.get("priority"):
                    from taskng.core.models import Priority

                    task.priority = Priority(old_data["priority"])
                task.project = old_data.get("project")
                task.tags = old_data.get("tags", [])
                task.end = None
                if old_data.get("end"):
                    from datetime import datetime

                    task.end = datetime.fromisoformat(old_data["end"])

                # Save without recording new history
                with db.connection() as conn:
                    conn.execute(
                        """
                        UPDATE tasks SET
                            description = ?, status = ?, priority = ?, project = ?,
                            modified = ?, end = ?
                        WHERE id = ?
                        """,
                        (
                            task.description,
                            task.status.value,
                            task.priority.value if task.priority else None,
                            task.project,
                            task.modified.isoformat(),
                            task.end.isoformat() if task.end else None,
                            task.id,
                        ),
                    )
                    repo._save_tags(conn, task.uuid, task.tags)

            console.print("[green]Undone: task modify[/green]")
            console.print(f"  Restored task {task.id if task else task_uuid}")
        else:
            console.print("[yellow]Cannot undo: no old data[/yellow]")
            return

    # Remove the history entry
    with db.connection() as conn:
        conn.execute("DELETE FROM task_history WHERE id = ?", (row["id"],))
