"""Import tasks from Taskwarrior or Task-NG JSON export."""

import contextlib
import json
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from taskng.core.models import Priority, Task, TaskStatus
from taskng.storage.repository import TaskRepository


@dataclass
class ImportResult:
    """Result of import operation."""

    imported: int = 0
    skipped: int = 0
    failed: int = 0
    errors: list[str] = field(default_factory=list)
    format_detected: str = ""


class TaskwarriorImporter:
    """Import tasks from Taskwarrior or Task-NG JSON export."""

    def __init__(self, repository: TaskRepository):
        """Initialize importer.

        Args:
            repository: Task repository for storing imported tasks.
        """
        self.repo = repository

    def import_file(self, path: Path, dry_run: bool = False) -> ImportResult:
        """Import tasks from JSON file.

        Supports multiple formats:
        - Taskwarrior export (array or newline-delimited)
        - Task-NG export (plain array)
        - Task-NG backup (object with version and tasks array)

        Args:
            path: Path to JSON file.
            dry_run: If True, don't actually import.

        Returns:
            Import result with statistics.
        """
        with open(path) as f:
            content = f.read().strip()

        result = ImportResult()

        # Parse JSON and detect format
        if content.startswith("["):
            # Array format - could be Taskwarrior or Task-NG
            data = json.loads(content)
            # Detect by date format in first task
            if data and self._is_taskwarrior_format(data[0]):
                result.format_detected = "taskwarrior"
            else:
                result.format_detected = "task-ng"
        elif content.startswith("{"):
            # Could be Task-NG backup object or newline-delimited JSON
            # Try to parse as single object first
            try:
                parsed = json.loads(content)
                if "tasks" in parsed and "version" in parsed:
                    result.format_detected = "task-ng-backup"
                    data = parsed["tasks"]
                else:
                    # Single task object? Wrap in array
                    result.format_detected = "unknown"
                    data = [parsed]
            except json.JSONDecodeError:
                # Not a single object, try newline-delimited
                result.format_detected = "taskwarrior-ndjson"
                data = [
                    json.loads(line) for line in content.splitlines() if line.strip()
                ]
        else:
            # Newline-delimited JSON (Taskwarrior)
            result.format_detected = "taskwarrior-ndjson"
            data = [json.loads(line) for line in content.splitlines() if line.strip()]

        existing_uuids = self._get_existing_uuids()

        for item in data:
            try:
                uuid = item.get("uuid", "")
                if uuid in existing_uuids:
                    result.skipped += 1
                    continue

                task = self._convert_task(item)
                if not dry_run:
                    self.repo.add(task)
                result.imported += 1
            except Exception as e:
                result.errors.append(f"{item.get('uuid', '?')}: {e}")
                result.failed += 1

        return result

    def _is_taskwarrior_format(self, item: dict[str, Any]) -> bool:
        """Check if task data is in Taskwarrior format.

        Taskwarrior uses date format like 20240115T093000Z.
        Task-NG uses ISO format like 2024-01-15T09:30:00.

        Args:
            item: Task data dictionary.

        Returns:
            True if Taskwarrior format detected.
        """
        # Check entry date format
        entry = item.get("entry", "")
        # Taskwarrior format: no dashes, has T and Z
        return bool(
            entry
            and isinstance(entry, str)
            and "T" in entry
            and "Z" in entry
            and "-" not in entry
        )

    def _get_existing_uuids(self) -> set[str]:
        """Get set of existing task UUIDs."""
        # Query all tasks to get their UUIDs
        tasks = self.repo.list_all()
        return {task.uuid for task in tasks}

    def _convert_task(self, data: dict[str, Any]) -> Task:
        """Convert Taskwarrior JSON to Task model.

        Args:
            data: Taskwarrior task data.

        Returns:
            Task model instance.
        """
        # Map status
        status_map = {
            "pending": TaskStatus.PENDING,
            "completed": TaskStatus.COMPLETED,
            "deleted": TaskStatus.DELETED,
            "waiting": TaskStatus.WAITING,
            "recurring": TaskStatus.RECURRING,
        }
        status = status_map.get(data.get("status", "pending"), TaskStatus.PENDING)

        # Map priority
        priority = None
        if data.get("priority"):
            with contextlib.suppress(ValueError):
                priority = Priority(data["priority"])

        # Parse annotations
        annotations = []
        for ann in data.get("annotations", []):
            entry_dt = self._parse_date(ann.get("entry"))
            annotations.append(
                {
                    "entry": entry_dt.isoformat() if entry_dt else "",
                    "description": ann.get("description", ""),
                }
            )

        # Extract UDAs (user-defined attributes)
        known_attrs = {
            "id",
            "uuid",
            "description",
            "status",
            "priority",
            "project",
            "entry",
            "modified",
            "start",
            "end",
            "due",
            "scheduled",
            "until",
            "wait",
            "recur",
            "rtype",
            "parent",
            "tags",
            "depends",
            "annotations",
            "urgency",
            "mask",
            "imask",
        }
        uda = {k: str(v) for k, v in data.items() if k not in known_attrs}

        return Task(
            uuid=data["uuid"],
            description=data["description"],
            status=status,
            priority=priority,
            project=data.get("project"),
            entry=self._parse_date(data.get("entry")) or datetime.now(),
            modified=self._parse_date(data.get("modified")) or datetime.now(),
            start=self._parse_date(data.get("start")),
            end=self._parse_date(data.get("end")),
            due=self._parse_date(data.get("due")),
            scheduled=self._parse_date(data.get("scheduled")),
            until=self._parse_date(data.get("until")),
            wait=self._parse_date(data.get("wait")),
            recur=data.get("recur"),
            parent_uuid=data.get("parent"),
            tags=data.get("tags", []),
            depends=data.get("depends", []),
            annotations=annotations,
            uda=uda,
        )

    def _parse_date(self, date_str: str | None) -> datetime | None:
        """Parse Taskwarrior date format.

        Args:
            date_str: Date string in Taskwarrior format (YYYYMMDDTHHMMSSz).

        Returns:
            Parsed datetime or None.
        """
        if not date_str:
            return None

        # Taskwarrior uses: 20240115T093000Z
        try:
            return datetime.strptime(date_str, "%Y%m%dT%H%M%SZ")
        except ValueError:
            # Try ISO format as fallback
            try:
                return datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            except ValueError:
                return None
