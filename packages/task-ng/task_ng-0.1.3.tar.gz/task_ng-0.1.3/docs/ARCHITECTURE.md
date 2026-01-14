# Task-NG Architecture

Technical architecture document for Task-NG, a modern Python reimagining of Taskwarrior.

- [System Overview](#system-overview)
- [CLI Layer](#cli-layer)
- [Core Domain Layer](#core-domain-layer)
- [Storage Layer](#storage-layer)
- [Configuration Layer](#configuration-layer)
- [Project Structure](#project-structure)
- [Performance Characteristics](#performance-characteristics)
- [Testing Strategy](#testing-strategy)
- [Planned Features (Not Yet Implemented)](#planned-features-not-yet-implemented)



---

## System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                      User Interface                          │
├─────────────────────────────────────────────────────────────┤
│                      CLI (Typer)                             │
│   task add/list/done/modify/show/board/calendar/stats        │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Core Domain Layer                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐     │
│  │ Models  │  │ Filters │  │ Urgency │  │ Recurrence  │     │
│  │(Pydantic)│ │ Engine  │  │  Calc   │  │   Engine    │     │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘     │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐  ┌─────────────┐     │
│  │ Virtual │  │  UDAs   │  │ Reports │  │   Boards    │     │
│  │  Tags   │  │         │  │         │  │  (Kanban)   │     │
│  └─────────┘  └─────────┘  └─────────┘  └─────────────┘     │
└─────────────────────────┬───────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
│  ┌─────────────┐  ┌──────────────┐  ┌─────────────────┐     │
│  │   SQLite    │  │  Repository  │  │   TW Import     │     │
│  │  Database   │  │   Pattern    │  │                 │     │
│  └─────────────┘  └──────────────┘  └─────────────────┘     │
└─────────────────────────────────────────────────────────────┘
                          │
                          ▼
┌─────────────────────────────────────────────────────────────┐
│                    Configuration                             │
│         TOML Config • Environment Variables • Defaults       │
└─────────────────────────────────────────────────────────────┘
```

### Data Flow

1. **Command Input** → CLI parses command and arguments
2. **Filter Processing** → Query parsed into structured filters
3. **Database Query** → SQLite executes parameterized query
4. **Domain Logic** → Urgency calculation, validation, hooks
5. **Storage Write** → Transaction committed, history recorded
6. **Output Formatting** → Rich renders response (or JSON mode)

---

## CLI Layer

### Entry Point: `cli/main.py`

The Typer application provides 22+ commands with global options:

```python
app = typer.Typer(
    name="task-ng",
    help="Task-NG: Modern task management",
    no_args_is_help=False,
)

# Global options
--json        # JSON output mode
--debug       # Show stack traces
--config      # Override config file
--data-dir    # Override data directory
```

### Commands

#### Core Task Operations
| Command | Description |
|---------|-------------|
| `add` | Create task with tags, project, due date, recurrence, dependencies |
| `list` | Display pending tasks with filtering and sorting |
| `show` | Display detailed task information |
| `modify` | Modify task(s) by ID or filter |
| `done` | Mark task(s) complete (supports ranges: "1-5,7,10-12") |
| `delete` | Soft delete task(s) |
| `undo` | Revert last operation |
| `edit` | Edit task in external editor |

#### Time Tracking
| Command | Description |
|---------|-------------|
| `start` | Begin time tracking |
| `stop` | Stop time tracking |
| `active` | Show currently active task |

#### Organization
| Command | Description |
|---------|-------------|
| `annotate` | Add timestamped notes |
| `denotate` | Remove annotations by index |
| `tags` / `tag list` | List all tags with counts |
| `projects` / `project list` | List projects in hierarchy |
| `project rename` | Rename project(s) |
| `contexts` / `context list` | List configured contexts |
| `context set/show/clear` | Manage current context |

#### Views & Reports
| Command | Description |
|---------|-------------|
| `report run` | Run named reports |
| `reports` / `report list` | List available reports |
| `stats` | Display task statistics |
| `calendar` | Calendar view (week/month/year) |
| `board show` | Kanban board view |
| `boards` / `board list` | List available boards |
| `import` | Import from JSON (Taskwarrior or Task-NG) |
| `export` | Export tasks to JSON |

### CLI Infrastructure

#### Output Modes (`output.py`)
- **Rich mode**: Colored tables, styled text (default)
- **JSON mode**: Serialize Pydantic models for scripting

#### Display Styling (`display.py`)
- `get_due_style()`: Color by urgency (red=overdue, yellow=today, cyan=week)
- `get_priority_style()`: Color by level (H/M/L)
- `get_urgency_style()`: Color by score
- `get_row_style()`: Overall row styling (blocked=magenta)
- `format_*()`: Formatting functions for all fields

#### Error Handling (`error_handler.py`)
- Specific handlers for each error type
- Helpful messages with suggestions
- JSON error output in JSON mode
- Optional stack traces with `--debug`

---

## Core Domain Layer

### Data Models (`models.py`)

```python
class TaskStatus(str, Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    DELETED = "deleted"
    WAITING = "waiting"
    RECURRING = "recurring"

class Priority(str, Enum):
    HIGH = "H"
    MEDIUM = "M"
    LOW = "L"

class Task(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    # Identity
    id: int | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))

    # Core
    description: str
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority | None = None
    project: str | None = None

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

    # Relations (separate tables)
    tags: list[str] = Field(default_factory=list)
    depends: list[str] = Field(default_factory=list)
    annotations: list[dict[str, str]] = Field(default_factory=list)
    uda: dict[str, str] = Field(default_factory=dict)

    # Calculated
    urgency: float = 0.0

    # Methods
    def add_annotation(self, text: str) -> None: ...
    def remove_annotation(self, index: int) -> None: ...
    def add_dependency(self, uuid: str) -> None: ...
    def remove_dependency(self, uuid: str) -> None: ...
    def set_uda(self, name: str, value: str) -> None: ...
    def get_uda(self, name: str) -> str | None: ...
```

### Filter Engine (`filters.py`)

Parses and executes Taskwarrior-compatible filter syntax:

```python
class Filter:
    attribute: str
    operator: str
    value: str

class FilterParser:
    def parse(self, args: list[str]) -> list[Filter]:
        """Parse filter expressions:
        - Attributes: project:Work, priority:H
        - Modifiers: project.not:Work, due.before:tomorrow
        - Tags: +urgent (include), -waiting (exclude)
        - Virtual tags: +OVERDUE, +BLOCKED
        """

    def to_sql(self, filters: list[Filter]) -> tuple[str, list]:
        """Convert to parameterized SQL WHERE clause."""

    def apply_virtual_filters(self, tasks, filters, all_tasks):
        """Apply computed tag filters in Python."""

    def matches_task(self, task, filters, all_tasks=None) -> bool:
        """Check if task matches all filters (in-memory filtering)."""
```

**Key improvements**:
- Basic filters compile to SQL for database-level execution
- In-memory filtering available via `matches_task()` for multi-pass scenarios (e.g., board columns)

### Date Handling (`dates.py`)

```python
# Natural language parsing
parse_date("tomorrow") → datetime
parse_date("next friday") → datetime
parse_date("in 3 days") → datetime

# Duration parsing
parse_duration("3d") → timedelta(days=3)
parse_duration("2w") → timedelta(weeks=2)
parse_duration("6m") → timedelta(days=180)

# Formatting
format_date(dt) → "2024-01-15 09:30"
format_relative(dt) → "in 2 days"
```

### Urgency Calculation (`urgency.py`)

Configurable scoring system:

```python
def calculate_urgency(task: Task, all_tasks: list[Task]) -> float:
    score = 0.0
    score += priority_urgency(task)      # H=6.0, M=3.9, L=1.8
    score += due_urgency(task)           # overdue=12.0, today=8.0, week=4.0
    score += project_urgency(task)       # 1.0 if has project
    score += tags_urgency(task)          # 0.5 per tag
    score += age_urgency(task)           # 0.01/day, max 2.0
    score *= blocked_multiplier(task)    # 0.5 if blocked
    return score
```

All coefficients configurable via `urgency.*` settings.

### Recurrence Engine (`recurrence.py`)

```python
# Parse patterns
parse_recurrence("daily") → {"type": "daily", "interval": 1}
parse_recurrence("2w") → {"type": "weekly", "interval": 2}
parse_recurrence("monthly") → {"type": "monthly", "interval": 1}

# Calculate next occurrence
calculate_next_due(current_due, recurrence) → datetime

# Generate next instance (called on task completion)
create_next_occurrence(task) → Task
```

Supports `until` date to limit recurrence.

### Dependency Management (`dependencies.py`)

```python
get_blocking_tasks(task, all_tasks)   # Tasks that block this one
is_blocked(task, all_tasks)           # Boolean check
get_dependency_chain(task, all_tasks) # Full chain (DFS)
check_circular(task, dep_uuid, all_tasks) # Cycle detection
```

### Virtual Tags (`virtual_tags.py`)

Computed tags for filtering and display:

| Category | Tags |
|----------|------|
| Time-based | OVERDUE, TODAY, WEEK, MONTH |
| Status | PENDING, COMPLETED, DELETED, WAITING |
| Priority | H, M, L |
| Dependency | BLOCKED, READY |
| Metadata | TAGGED, ANNOTATED, PROJECT, DUE, SCHEDULED, RECURRING, ACTIVE |

```python
get_virtual_tags(task, all_tasks) → set[str]
has_virtual_tag(task, tag_name) → bool
is_virtual_tag(tag_name) → bool
```

### User-Defined Attributes (`uda.py`)

```python
# Parse from description
parse_udas_from_text("Buy milk estimate:30min")
→ ("Buy milk", {"estimate": "30min"})

# Type validation
validate_uda_value(value, uda_type)  # string, numeric, date, duration
```

### Reports (`reports.py`)

Named, configurable task views:

```python
class ReportDefinition:
    name: str
    description: str
    columns: list[str]
    filter: list[str]
    sort: list[str]
    limit: int | None

# Built-in reports
DEFAULT_REPORTS = {
    "list": ReportDefinition(columns=["id", "priority", "project", ...]),
    "next": ReportDefinition(sort=["urgency-"], limit=10),
    "all": ReportDefinition(filter=[]),
    "completed": ReportDefinition(filter=["status:completed"]),
    "overdue": ReportDefinition(filter=["+OVERDUE"]),
    "waiting": ReportDefinition(filter=["status:waiting"]),
    "recurring": ReportDefinition(filter=["+RECURRING"]),
}
```

### Kanban Boards (`boards.py`)

```python
class BoardDefinition:
    name: str
    description: str
    columns: list[ColumnDefinition]
    card_fields: list[str]
    sort: list[str]
    limit: int
    column_width: int

class ColumnDefinition:
    name: str
    filter: list[str]
    limit: int | None
    wip_limit: int | None
    since: str | None  # Time window

# Built-in boards
- default: Pending → Today → Overdue → Blocked
- priority: High → Medium → Low → None
```

### Other Core Modules

- **`sorting.py`**: Multi-key sort with +/- direction
- **`projects.py`**: Hierarchical project tree with counts
- **`context.py`**: Named filter sets for task views
- **`hooks.py`**: Execute scripts on task events
- **`statistics.py`**: Task metrics and analytics
- **`id_parser.py`**: Parse ID expressions ("1-5,7,10")

---

## Storage Layer

### Database: SQLite

**Why SQLite:**
- Single-file, portable (local-first philosophy)
- ACID transactions for data integrity
- Concurrent reads with WAL mode
- No server dependency

**Configuration:**
```python
PRAGMA foreign_keys = ON;
PRAGMA journal_mode = WAL;
```

### Schema (`schema.py`)

```sql
-- Core task table
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY,
    uuid TEXT UNIQUE NOT NULL,
    description TEXT NOT NULL,
    status TEXT NOT NULL DEFAULT 'pending',
    priority TEXT,
    project TEXT,

    -- Timestamps
    entry DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    modified DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    start DATETIME,
    end DATETIME,
    due DATETIME,
    scheduled DATETIME,
    until DATETIME,
    wait DATETIME,

    -- Recurrence
    recur TEXT,
    parent_uuid TEXT,

    -- Calculated
    urgency REAL DEFAULT 0.0,
    notes TEXT
);

-- Normalized tags
CREATE TABLE tags (
    task_uuid TEXT NOT NULL,
    tag TEXT NOT NULL,
    PRIMARY KEY (task_uuid, tag),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Dependencies
CREATE TABLE dependencies (
    task_uuid TEXT NOT NULL,
    depends_on_uuid TEXT NOT NULL,
    PRIMARY KEY (task_uuid, depends_on_uuid),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Annotations
CREATE TABLE annotations (
    id INTEGER PRIMARY KEY,
    task_uuid TEXT NOT NULL,
    entry DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    description TEXT NOT NULL,
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- User Defined Attributes
CREATE TABLE uda_values (
    task_uuid TEXT NOT NULL,
    attribute TEXT NOT NULL,
    value TEXT,
    PRIMARY KEY (task_uuid, attribute),
    FOREIGN KEY (task_uuid) REFERENCES tasks(uuid) ON DELETE CASCADE
);

-- Audit trail
CREATE TABLE task_history (
    id INTEGER PRIMARY KEY,
    task_uuid TEXT NOT NULL,
    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    operation TEXT NOT NULL,
    old_data JSON,
    new_data JSON,
    synced BOOLEAN DEFAULT FALSE
);
```

### Indexes

```sql
-- Primary query patterns
CREATE INDEX idx_tasks_status ON tasks(status);
CREATE INDEX idx_tasks_due ON tasks(due);
CREATE INDEX idx_tasks_project ON tasks(project);
CREATE INDEX idx_tasks_urgency ON tasks(urgency DESC);
CREATE INDEX idx_tasks_modified ON tasks(modified);

-- Tag lookups
CREATE INDEX idx_tags_tag ON tags(tag);

-- Dependency queries
CREATE INDEX idx_deps_depends ON dependencies(depends_on_uuid);

-- History
CREATE INDEX idx_history_timestamp ON task_history(timestamp);
CREATE INDEX idx_history_synced ON task_history(synced);
```

### Repository Pattern (`repository.py`)

Data access layer with parameterized queries:

```python
class TaskRepository:
    # CRUD
    def add(self, task: Task) -> Task: ...
    def get_by_id(self, task_id: int) -> Task | None: ...
    def get_by_uuid(self, uuid: str) -> Task | None: ...
    def update(self, task: Task) -> None: ...
    def delete(self, task_id: int) -> None: ...        # Soft delete
    def hard_delete(self, task_id: int) -> None: ...

    # Queries
    def list_pending(self) -> list[Task]: ...
    def list_filtered(self, filters: list[Filter]) -> list[Task]: ...
    def list_all(self) -> list[Task]: ...
    def get_unique_projects(self) -> list[str]: ...
    def get_unique_tags(self) -> list[str]: ...
```

All operations record history for undo support.

### Import & Export (`import_tw.py`, `export.py`)

```python
class TaskwarriorImporter:
    def import_file(self, path: Path, dry_run: bool) -> ImportResult:
        """Import from JSON export files.

        Supported formats (auto-detected):
        - Taskwarrior array format
        - Taskwarrior newline-delimited JSON (NDJSON)
        - Task-NG export (plain array)
        - Task-NG backup (object with version and tasks)

        Features:
        - Deduplicates by UUID
        - Converts status, priority, annotations, UDAs
        - Returns format_detected for user feedback
        """

def export_tasks(output, filter_args, include_completed, include_deleted):
    """Export tasks to JSON array."""

def export_backup(output):
    """Create full backup with metadata (version, timestamp, count)."""
```

---

## Configuration Layer

### Layered Configuration (`settings.py`)

Priority order (highest wins):
1. Defaults from `defaults.py`
2. Config file (`~/.config/taskng/config.toml`)
3. Environment variables (`TASKNG_*`)
4. CLI overrides (`--config`, `--data-dir`)

```python
class Config:
    def get(self, key: str, default=None):
        """Dot-notation access: config.get('ui.color')"""

    def set(self, key: str, value):
        """Dot-notation set: config.set('urgency.due.coefficient', 15.0)"""

    def save(self):
        """Write to TOML file."""
```

### Key Configuration Options

```toml
# Data locations
data.location = "~/.local/share/taskng"

# Default behavior
default.command = "next"

# UI settings
ui.color = true
ui.unicode = true

# Color scheme
color.due.today = "yellow"
color.due.overdue = "red"
color.priority.H = "red bold"
color.blocked = "magenta"

# Urgency coefficients
urgency.priority.coefficient = 1.0
urgency.due.coefficient = 0.5
urgency.overdue.coefficient = 1.0

# Calendar
calendar.weekstart = "monday"

# Reports (override defaults)
[report.custom]
columns = ["id", "description", "due"]
filter = ["+urgent"]
sort = ["due+"]

# Boards
[board.custom]
columns = [...]

# Contexts
[context.work]
filter = ["project:Work"]
```

---

## Project Structure

```
task-ng/
├── src/taskng/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   ├── main.py              # Entry point, Typer app
│   │   ├── output.py            # JSON output mode
│   │   ├── display.py           # Rich styling/formatting
│   │   ├── error_handler.py     # Centralized error handling
│   │   ├── completion.py        # Shell completion
│   │   └── commands/
│   │       ├── __init__.py
│   │       ├── add.py
│   │       ├── list.py
│   │       ├── show.py
│   │       ├── modify.py
│   │       ├── done.py
│   │       ├── delete.py
│   │       ├── undo.py
│   │       ├── edit.py
│   │       ├── start.py
│   │       ├── stop.py
│   │       ├── active.py
│   │       ├── annotate.py
│   │       ├── tags.py
│   │       ├── projects.py
│   │       ├── project_rename.py
│   │       ├── context.py
│   │       ├── report.py
│   │       ├── stats.py
│   │       ├── calendar.py
│   │       ├── board.py
│   │       ├── import_cmd.py
│   │       └── config.py
│   ├── core/
│   │   ├── __init__.py
│   │   ├── models.py            # Pydantic models
│   │   ├── filters.py           # Filter engine
│   │   ├── dates.py             # Date parsing
│   │   ├── urgency.py           # Urgency calculation
│   │   ├── recurrence.py        # Recurrence engine
│   │   ├── dependencies.py      # Dependency management
│   │   ├── virtual_tags.py      # Computed tags
│   │   ├── uda.py               # User-defined attributes
│   │   ├── sorting.py           # Multi-key sorting
│   │   ├── projects.py          # Project hierarchy
│   │   ├── context.py           # Task contexts
│   │   ├── hooks.py             # Hook system
│   │   ├── reports.py           # Report definitions
│   │   ├── boards.py            # Kanban boards
│   │   ├── statistics.py        # Task statistics
│   │   ├── id_parser.py         # ID expression parsing
│   │   └── exceptions.py        # Custom exceptions
│   ├── storage/
│   │   ├── __init__.py
│   │   ├── database.py          # SQLite connection
│   │   ├── schema.py            # Schema definition
│   │   ├── repository.py        # Data access layer
│   │   ├── import_tw.py         # Taskwarrior import
│   │   └── migrations/
│   │       ├── __init__.py
│   │       ├── env.py
│   │       └── versions/
│   │           └── 001_initial_schema.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py          # Config management
│   │   └── defaults.py          # Default values
│   └── utils/
│       └── __init__.py
├── tests/
│   ├── conftest.py              # Shared fixtures
│   ├── unit/                    # Unit tests
│   └── integration/             # CLI integration tests
├── docs/
│   └── USER_GUIDE.md
├── scripts/
│   └── ci.sh
├── pyproject.toml
├── README.md
├── CLAUDE.md
└── ARCHITECTURE.md
```

---

## Performance Characteristics

| Operation | Strategy |
|-----------|----------|
| `task add` | Direct insert, lazy imports |
| `task list` | Indexed SQL query, pagination |
| Filter parsing | Compiled to SQL WHERE |
| Urgency calc | Batch calculation with caching |
| Virtual tags | Python-side evaluation |

---

## Testing Strategy

- **Unit tests**: Core logic (filters, urgency, recurrence, dates)
- **Integration tests**: Database operations, CLI commands
- **Coverage**: >80% required (enforced by CI)
- **Fixtures**: Temporary database, CLI runner, mock config

---

*Last Updated: 2025-01-22*
*Version: 0.3.0*
