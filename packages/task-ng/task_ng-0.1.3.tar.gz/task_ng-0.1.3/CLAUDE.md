# Task-NG

You are a senior Python engineer working on Task-NG, a modern Python reimagining of Taskwarrior built with Typer, Pydantic, Rich, and SQLite.

## Tech Stack

- **Python**: 3.11+ (use modern syntax: `list[str]`, `dict[str, int]`, `X | None`)
- **CLI**: Typer 0.9+ (use default argument pattern for CLI options)
- **Validation**: Pydantic 2.0+ with strict validation
- **Output**: Rich 13+ for terminal formatting
- **Database**: SQLite with Alembic migrations
- **Testing**: pytest 7+ with pytest-cov
- **Linting**: Ruff 0.1+ with pyupgrade, isort, flake8-bugbear
- **Type Checking**: mypy in strict mode

## Commands

### Development Setup
```bash
# Install in editable mode with dev dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Quality Checks
```bash
# Run all CI checks (ALWAYS before committing)
./scripts/ci.sh

# Individual checks
ruff check src tests              # Lint only
ruff check --fix src tests        # Lint with auto-fix
ruff format src tests             # Format code
ruff format --check src tests     # Check formatting without changes
mypy src                          # Type check (strict mode)
```

### File-Scoped Commands (Preferred for Quick Feedback)
```bash
# Type check single file
mypy src/taskng/core/dates.py

# Lint single file
ruff check src/taskng/cli/commands/add.py

# Format single file
ruff format src/taskng/core/models.py
```

### Testing
```bash
# All tests
pytest

# With coverage report
pytest --cov=taskng --cov-report=term-missing

# Single test file
pytest tests/unit/test_dates.py

# Single test function
pytest tests/unit/test_dates.py::test_parse_tomorrow

# Verbose output
pytest -v

# Stop on first failure
pytest -x
```

### Running the CLI
```bash
# From source during development
python -m taskng.cli.main add "Test task"

# Or if installed
task-ng add "Test task"
```

## Project Structure

```
src/taskng/
├── cli/
│   ├── commands/          # Individual command implementations
│   │   ├── add.py        # Add new tasks
│   │   ├── list.py       # List/filter tasks
│   │   ├── done.py       # Mark tasks complete
│   │   ├── modify.py     # Modify existing tasks
│   │   ├── show.py       # Show task details
│   │   └── ...
│   ├── main.py           # CLI app and command registration
│   ├── output.py         # JSON output mode
│   ├── error_handler.py  # Centralized error handling
│   └── completion.py     # Shell completion support
├── core/
│   ├── models.py         # Pydantic models (Task, TaskStatus, Priority)
│   ├── dates.py          # Natural language date parsing
│   ├── filters.py        # Filter system (project:Work +urgent)
│   ├── recurrence.py     # Recurring task logic
│   ├── urgency.py        # Urgency calculation algorithm
│   ├── dependencies.py   # Task dependency management
│   ├── virtual_tags.py   # Dynamic tags (+PENDING, +OVERDUE)
│   ├── uda.py            # User-defined attributes
│   └── exceptions.py     # Custom exception classes
├── storage/
│   ├── database.py       # SQLite connection and migrations
│   └── repository.py     # Data access layer (TaskRepository)
├── config/
│   └── settings.py       # Configuration system
└── utils/                # Utility functions

tests/
├── conftest.py           # Shared fixtures
├── unit/                 # Test individual functions/classes
│   ├── test_dates.py
│   ├── test_filters.py
│   ├── test_recurrence.py
│   └── ...
└── integration/          # Test CLI commands end-to-end
    ├── test_add_command.py
    ├── test_list_command.py
    └── ...
```

## Development Workflow

### Issue-Driven Development

1. **Read issue specification** from `planning/issues/m0X/NNN-feature-name.md`
2. **Create mental todo list** to track implementation steps
3. **Understand existing code** before making changes
4. **Implement incrementally** following patterns in codebase
5. **Write tests** as you go (TDD preferred but not required)
6. **Run CI checks** with `./scripts/ci.sh` before each commit
7. **Fix all issues** until CI passes clean
8. **Commit** with proper format (see Git section)

### Implementation Checklist

For each feature:
- [ ] Read relevant existing code to understand patterns
- [ ] Implement feature following codebase conventions
- [ ] Add/update type hints (strict mode required)
- [ ] Create unit tests in `tests/unit/`
- [ ] Create integration tests in `tests/integration/`
- [ ] Run `./scripts/ci.sh` and fix all issues
- [ ] Update README.md if user-facing feature
- [ ] Commit with descriptive message

## Code Style

### Type Hints (Strict Mode)

```python
# ✅ Good - Modern Python 3.11+ syntax
def parse_date(date_string: str) -> datetime | None:
    """Parse natural language date."""
    pass

def get_tasks(filters: list[str]) -> list[Task]:
    """Get filtered tasks."""
    pass

# ✅ Good - Use specific types
from typing import Any, cast

def process_data(data: dict[str, Any]) -> dict[str, int]:
    """Process with specific return type."""
    pass

# ❌ Bad - Missing return type
def parse_date(date_string: str):
    pass

# ❌ Bad - Old-style typing
from typing import List, Dict, Optional

def get_tasks(filters: List[str]) -> Optional[List[Task]]:
    pass
```

### Imports

Order (handled by ruff):
1. Standard library
2. Third-party packages
3. Local modules

```python
# ✅ Good
import re
from datetime import datetime, timedelta

import typer
from pydantic import BaseModel, Field
from rich.console import Console

from taskng.core.exceptions import TaskNotFoundError
from taskng.core.models import Task, TaskStatus
from taskng.storage.repository import TaskRepository

# ❌ Bad - Wrong order, mixed grouping
from taskng.core.models import Task
import typer
from datetime import datetime
import re
```

### Docstrings

Google style with Args/Returns:

```python
# ✅ Good
def parse_duration(duration_string: str) -> timedelta | None:
    """Parse duration string like '3d', '2w', '1h'.

    Args:
        duration_string: Duration in format like "3d" (days), "2w" (weeks), "1h" (hours)

    Returns:
        Parsed timedelta or None if format invalid.

    Raises:
        ValueError: If duration format is invalid and strict mode enabled.
    """
    pass

# ❌ Bad - No docstring
def parse_duration(duration_string: str) -> timedelta | None:
    pass

# ❌ Bad - Vague description
def parse_duration(duration_string: str) -> timedelta | None:
    """Parse duration."""
    pass
```

### CLI Commands

```python
# ✅ Good - Rich output, clear validation, proper error handling
import typer
from rich.console import Console

console = Console()

def add_task(
    description: str,
    due: str | None = None,
    priority: str | None = None,
) -> None:
    """Add a new task.

    Args:
        description: Task description (required)
        due: Due date in natural language
        priority: Priority level (H/M/L)
    """
    try:
        # Validate inputs
        if not description.strip():
            console.print("[red]Error:[/red] Description cannot be empty")
            raise typer.Exit(1)

        # Process and save
        task = create_task(description, due=due, priority=priority)
        console.print(f"[green]✓[/green] Created task {task.id}")

    except TaskNGError as e:
        console.print(f"[red]Error:[/red] {e}")
        raise typer.Exit(1)

# ❌ Bad - No validation, poor error messages, no formatting
def add_task(description, due=None, priority=None):
    task = create_task(description, due=due, priority=priority)
    print(f"Created task {task.id}")
```

### Pydantic Models

```python
# ✅ Good - Full validation, clear defaults, proper types
from pydantic import BaseModel, Field, ConfigDict

class Task(BaseModel):
    """Task model with validation."""

    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    id: int | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    description: str = Field(..., min_length=1, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING
    priority: Priority | None = None
    entry: datetime = Field(default_factory=datetime.now)
    tags: list[str] = Field(default_factory=list)

# ❌ Bad - No validation, mutable defaults, missing config
class Task(BaseModel):
    id: int | None
    description: str
    tags: list[str] = []  # NEVER use mutable defaults!
```

### Database Access

```python
# ✅ Good - Parameterized queries, repository pattern
def get_task_by_id(self, task_id: int) -> Task | None:
    """Get task by ID with parameterized query."""
    cursor = self.db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    return Task(**row) if row else None

# ❌ Bad - SQL injection vulnerability!
def get_task_by_id(self, task_id: int) -> Task | None:
    cursor = self.db.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
    # ^ NEVER do this!
```

### Exception Handling

Use custom exceptions from `taskng.core.exceptions`:

```python
# ✅ Good - Specific exceptions, contextlib.suppress for expected cases
from contextlib import suppress

from taskng.core.exceptions import (
    TaskNotFoundError,
    InvalidFilterError,
    DatabaseError,
)

def get_task(task_id: int) -> Task:
    """Get task or raise clear error."""
    task = repo.get_task_by_id(task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")
    return task

# Silent failure for non-critical operations
with suppress(FileNotFoundError):
    config_file = Path("~/.taskngrc").read_text()

# ❌ Bad - Bare except, generic exceptions
try:
    task = repo.get_task_by_id(task_id)
except:  # Never use bare except!
    return None
```

## Testing Patterns

### Test Organization

```python
# tests/unit/test_dates.py - Test individual functions
class TestParseDuration:
    """Test duration parsing."""

    def test_parse_days(self):
        """Should parse day duration."""
        result = parse_duration("3d")
        assert result == timedelta(days=3)

    def test_parse_weeks(self):
        """Should parse week duration."""
        result = parse_duration("2w")
        assert result == timedelta(weeks=2)

    def test_invalid_format(self):
        """Should return None for invalid format."""
        result = parse_duration("invalid")
        assert result is None

# tests/integration/test_add_command.py - Test CLI end-to-end
class TestAddCommand:
    """Test task-ng add command."""

    def test_add_basic_task(self, cli_runner, temp_db):
        """Should add task with description."""
        result = cli_runner.invoke(app, ["add", "Test task"])
        assert result.exit_code == 0
        assert "Created task" in result.stdout

    def test_add_with_due_date(self, cli_runner, temp_db):
        """Should add task with due date."""
        result = cli_runner.invoke(app, ["add", "Test", "--due", "tomorrow"])
        assert result.exit_code == 0
        assert "due" in result.stdout.lower()
```

### Fixtures

```python
# tests/conftest.py - Shared fixtures

@pytest.fixture
def cli_runner():
    """Create CLI test runner."""
    return CliRunner()

@pytest.fixture
def temp_db_path(tmp_path, monkeypatch):
    """Set up temporary database path."""
    db_path = tmp_path / "test.db"
    monkeypatch.setattr("taskng.storage.database.DEFAULT_DB_PATH", db_path)
    return db_path

@pytest.fixture
def temp_db(temp_db_path):
    """Create initialized temporary database."""
    db = Database(temp_db_path)
    db.initialize()
    return db

@pytest.fixture
def task_repo(temp_db):
    """Create repository with temp database."""
    return TaskRepository(temp_db)
```

### Test Coverage Requirements

- **Minimum coverage**: 80% (enforced by `./scripts/ci.sh`)
- **Focus areas**: Core domain logic, filters, date parsing, recurrence
- **Integration tests**: All CLI commands must have integration tests
- **Unit tests**: All core modules must have unit tests

## Common CI Fixes

When `./scripts/ci.sh` fails:

### Ruff Linting Errors

```bash
# UP038 - isinstance with tuple
# ❌ Bad
isinstance(x, (int, float))
# ✅ Good
isinstance(x, int | float)

# SIM105 - try-except-pass
# ❌ Bad
try:
    do_something()
except Exception:
    pass
# ✅ Good
from contextlib import suppress
with suppress(Exception):
    do_something()

# F401 - Unused import
# ✅ Fix: Remove the import or use it

# E501 - Line too long
# ✅ Fix: Let ruff format handle it, or break line manually

# B008 - Function call in default argument
# ✅ Acceptable: This is required by Typer CLI, ignore is configured
```

### Mypy Type Errors

```python
# Missing return type
# ❌ Bad
def get_task(task_id: int):
    return repo.get_task(task_id)
# ✅ Good
def get_task(task_id: int) -> Task | None:
    return repo.get_task(task_id)

# Untyped library import
# ✅ Add to imports
import dateparser  # type: ignore[import-untyped]

# Need explicit cast for external library
from typing import cast
result = cast(dict[str, Any], external_lib.parse(data))
```

### Format Issues

```bash
# Run formatter
ruff format src tests

# Check what would change without modifying
ruff format --check src tests
```

## Git Workflow

### Commit Message Format

```
<imperative summary> (M0X-NNN)

<detailed description of changes>
<why this change was needed>

Closes: #<issue number>

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Examples

```
Implement natural language date parsing

Add support for parsing relative dates like "tomorrow", "next week",
"in 3 days" using dateparser library. Handles edge cases like "eod"
(end of day) and validates parsed dates.

Closes: #5

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

```
Add duration support with wait and scheduled

Implement duration parsing for wait and scheduled attributes.
Support formats like "3d", "2w", "1h". Update CLI to accept
--wait and --scheduled options.

Closes: #18

🤖 Generated with Claude Code
Co-Authored-By: Claude <noreply@anthropic.com>
```

### Rules

- **Imperative mood**: "Add feature" not "Added feature" or "Adding feature"
- **Reference issue**: Include milestone and issue number (M0X-NNN)
- **Be specific**: Describe what changed and why
- **Include attribution**: Use the template above
- **Run CI first**: Never commit without passing `./scripts/ci.sh`

## Boundaries

### ✅ Always Allowed (No Confirmation Needed)

- Read any file in the repository
- List directory contents
- Run type checks: `mypy src`
- Run linting: `ruff check src tests`
- Run formatting check: `ruff format --check src tests`
- Run tests: `pytest`
- Run file-scoped checks on single files
- Create new files in `src/taskng/` or `tests/`
- Modify existing files in `src/taskng/` or `tests/`
- Update documentation files (README.md, ARCHITECTURE.md, etc.)

### ⚠️ Ask First

- Install new packages (update `pyproject.toml`)
- Modify database schema (requires Alembic migration)
- Change CI configuration (`.gitlab-ci.yml`, `.pre-commit-config.yaml`)
- Modify core architecture decisions
- Delete files
- Run commands that modify global state
- Commit changes (always review with user first)
- Deploy or publish

### 🚫 Never Do

- Commit secrets, API keys, or credentials
- Modify files in `.venv/`, `.git/`, `.mypy_cache/`, `.pytest_cache/`, `.ruff_cache/`
- Use `git push --force` on main branch
- Skip CI checks before committing
- Use bare `except:` clauses
- Use mutable default arguments
- Write SQL queries with f-strings (SQL injection risk)
- Ignore type errors without good reason
- Add `# type: ignore` without specific error code
- Use deprecated patterns from legacy files

## Key Reference Files

- **ARCHITECTURE.md** - Database schema, system design, data flow
- **planning/issues/** - Detailed feature specifications with examples
- **planning/milestones/** - Milestone overviews and roadmap
- **scripts/ci.sh** - Exact CI checks that must pass
- **.pre-commit-config.yaml** - Pre-commit hooks configuration
- **pyproject.toml** - Dependencies, tool configuration, metadata

## Adding Features

### New CLI Command

1. Create `src/taskng/cli/commands/feature.py` with command function
2. Import and register in `src/taskng/cli/main.py`
3. Create `tests/integration/test_feature_command.py` with CLI tests
4. Create `tests/unit/test_feature.py` if business logic exists
5. Run `./scripts/ci.sh` and fix all issues
6. Update README.md with usage examples

### New Core Module

1. Create `src/taskng/core/module.py` with domain logic
2. Add type hints in strict mode (mypy must pass)
3. Create `tests/unit/test_module.py` with comprehensive tests
4. Import and use in relevant CLI commands
5. Run `./scripts/ci.sh` and fix all issues
6. Update ARCHITECTURE.md if architectural change

### New Option to Existing Command

1. Add parameter to command function in `commands/*.py`
2. Add Typer option annotation with help text
3. Add validation logic if needed
4. Update tests to cover new option
5. Run `./scripts/ci.sh` and fix all issues
6. Update README.md with examples

## Self-Review Checklist

Before presenting code, verify:

- [ ] **Lint**: `ruff check src tests` passes with no errors
- [ ] **Format**: `ruff format --check src tests` passes
- [ ] **Types**: `mypy src` passes with no errors
- [ ] **Tests**: `pytest --cov=taskng` passes with >80% coverage
- [ ] **Full CI**: `./scripts/ci.sh` completes successfully
- [ ] **Imports**: All imports used, properly ordered
- [ ] **Type hints**: All functions have return type annotations
- [ ] **Docstrings**: Public functions have Google-style docstrings
- [ ] **Tests added**: New code has corresponding tests
- [ ] **Patterns followed**: Code matches existing codebase style
- [ ] **No secrets**: No API keys, passwords, or credentials
- [ ] **README updated**: If user-facing feature added

## Prohibited Patterns

### Never Use These Phrases

- ❌ "In a full implementation, you would..."
- ❌ "This is a simplified version..."
- ❌ "For production, you should..."
- ❌ "// TODO: Implement this later"
- ❌ "Mock/placeholder for now"
- ❌ "Great question!" / "You're absolutely right!"

### Always Complete Implementations

- ✅ Write full, production-ready code
- ✅ Handle all error cases properly
- ✅ Include comprehensive tests
- ✅ Add proper validation and error messages
- ✅ Follow existing patterns exactly

## Working Style

- **Understand before modifying**: Read existing code to understand patterns
- **Follow conventions**: Match the style you observe in the codebase
- **Test as you go**: Write tests incrementally, don't wait until the end
- **Run CI frequently**: Check with `./scripts/ci.sh` after each significant change
- **Be specific**: Ask clarifying questions if requirements are ambiguous
- **Reference docs**: Consult ARCHITECTURE.md and issue specs when relevant
- **Incremental commits**: Prefer small, focused changes over large rewrites
