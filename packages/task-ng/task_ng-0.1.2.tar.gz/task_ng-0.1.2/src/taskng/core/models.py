"""Core data models for Task-NG."""

from datetime import datetime
from enum import Enum
from uuid import uuid4

from pydantic import BaseModel, ConfigDict, Field


class TaskStatus(str, Enum):
    """Task status values."""

    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    WAITING = "waiting"
    RECURRING = "recurring"


class Priority(str, Enum):
    """Task priority values."""

    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"


class Task(BaseModel):
    """Core task model with full validation."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    # Identity
    id: int | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    # Core attributes
    description: str = Field(..., min_length=1, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority | None = None
    project: str | None = Field(None, max_length=255)

    # Timestamps
    entry: datetime = Field(default_factory=datetime.now)
    modified: datetime = Field(default_factory=datetime.now)
    start: datetime | None = None
    end: datetime | None = None
    due: datetime | None = None
    scheduled: datetime | None = None
    until: datetime | None = None
    wait: datetime | None = None

    # Recurrence
    recur: str | None = None
    parent_uuid: str | None = None

    # Calculated
    urgency: float = 0.0

    # Relations (not stored in main table)
    tags: list[str] = Field(default_factory=list)
    depends: list[str] = Field(default_factory=list)
    annotations: list[dict[str, str]] = Field(default_factory=list)
    uda: dict[str, str] = Field(default_factory=dict)

    # Content
    notes: str | None = None

    def add_annotation(self, text: str) -> None:
        """Add annotation with current timestamp."""
        self.annotations.append(
            {
                "entry": datetime.now().strftime("%Y-%m-%d %H:%M"),
                "description": text,
            }
        )

    def remove_annotation(self, index: int) -> None:
        """Remove annotation by index (0-based)."""
        if 0 <= index < len(self.annotations):
            del self.annotations[index]

    def add_dependency(self, uuid: str) -> None:
        """Add task dependency."""
        if uuid not in self.depends:
            self.depends.append(uuid)

    def remove_dependency(self, uuid: str) -> None:
        """Remove task dependency."""
        if uuid in self.depends:
            self.depends.remove(uuid)

    def set_uda(self, name: str, value: str) -> None:
        """Set user-defined attribute."""
        self.uda[name] = value

    def get_uda(self, name: str, default: str = "") -> str:
        """Get user-defined attribute."""
        return self.uda.get(name, default)
