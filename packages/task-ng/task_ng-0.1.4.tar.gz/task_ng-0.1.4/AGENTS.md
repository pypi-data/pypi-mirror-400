# Task-NG Agent Guide

Quick reference for coding agents working on Task-NG, a modern Python task manager built with Typer, Pydantic, Rich, and SQLite.

## Quick Start

```bash
# Install in editable mode with dependencies (REQUIRED for development)
poetry install
poetry run pip install -e .

# After editing Python files, refresh the installation
./scripts/refresh.sh                         # Clears cache + reinstalls

# Run development version
./scripts/dev.sh add "Test task"             # Auto-refresh + run
# OR:
poetry run task-ng add "Test task"           # Must refresh manually first

# Run full CI suite (REQUIRED before committing)
./scripts/ci.sh

# Run tests
pytest                                          # All tests
pytest tests/unit/test_dates.py                # Single file
pytest tests/unit/test_dates.py::test_parse_tomorrow  # Single test
pytest -v                                       # Verbose
pytest -x                                       # Stop on first failure
pytest --cov=taskng --cov-report=term-missing  # With coverage

# Quality checks
poetry run ruff check src tests              # Lint
poetry run ruff check --fix src tests        # Lint + auto-fix
poetry run ruff format src tests             # Format code
poetry run mypy src                          # Type check (strict mode)

# File-scoped (faster feedback)
poetry run mypy src/taskng/core/dates.py
poetry run ruff check src/taskng/cli/commands/add.py
poetry run ruff format src/taskng/core/models.py
```

## Tech Stack

- **Python 3.11+**: Use modern syntax (`list[str]`, `dict[str, int]`, `X | None`)
- **CLI**: Typer 0.9+ with Rich 13+ for output
- **Validation**: Pydantic 2.0+ with strict validation
- **Database**: SQLite with Alembic migrations
- **Testing**: pytest 7+ (80% coverage minimum)
- **Linting**: Ruff with pyupgrade, isort, flake8-bugbear
- **Type Checking**: mypy in strict mode

## Code Style

### Type Hints (Strict)

```python
# ✅ Modern Python 3.11+ syntax
def parse_date(date_string: str) -> datetime | None:
    """Parse natural language date."""

def get_tasks(filters: list[str]) -> list[Task]:
    """Get filtered tasks."""

# ❌ Never do this
def parse_date(date_string: str):  # Missing return type
def get_tasks(filters: List[str]) -> Optional[List[Task]]:  # Old syntax
```

### Imports

Order (auto-sorted by ruff):
1. Standard library
2. Third-party packages
3. Local modules

```python
# ✅ Correct order
import re
from datetime import datetime, timedelta

import typer
from pydantic import BaseModel, Field
from rich.console import Console

from taskng.core.exceptions import TaskNotFoundError
from taskng.core.models import Task, TaskStatus
from taskng.storage.repository import TaskRepository
```

### Docstrings

Use Google style with Args/Returns/Raises:

```python
def parse_duration(duration_string: str) -> timedelta | None:
    """Parse duration string like '3d', '2w', '1h'.

    Args:
        duration_string: Duration in format like "3d" (days), "2w" (weeks)

    Returns:
        Parsed timedelta or None if format invalid.

    Raises:
        ValueError: If duration format is invalid and strict mode enabled.
    """
```

### Naming Conventions

- **Modules/packages**: `snake_case` (e.g., `date_parser.py`, `task_repository.py`)
- **Classes**: `PascalCase` (e.g., `Task`, `TaskRepository`, `TaskStatus`)
- **Functions/variables**: `snake_case` (e.g., `parse_date`, `task_id`)
- **Constants**: `UPPER_SNAKE_CASE` (e.g., `DEFAULT_DB_PATH`, `MAX_RETRIES`)
- **Private**: Prefix with `_` (e.g., `_internal_helper`)

### Error Handling

Use custom exceptions from `taskng.core.exceptions`:

```python
# ✅ Good - Specific exceptions
from contextlib import suppress
from taskng.core.exceptions import TaskNotFoundError, InvalidFilterError

def get_task(task_id: int) -> Task:
    task = repo.get_task_by_id(task_id)
    if not task:
        raise TaskNotFoundError(f"Task {task_id} not found")
    return task

# Silent failure for non-critical operations
with suppress(FileNotFoundError):
    config = Path("~/.taskngrc").read_text()

# ❌ Never do this
try:
    task = repo.get_task_by_id(task_id)
except:  # Bare except!
    return None
```

### Pydantic Models

```python
# ✅ Full validation, no mutable defaults
from pydantic import BaseModel, Field, ConfigDict

class Task(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        str_strip_whitespace=True,
    )

    id: int | None = None
    uuid: str = Field(default_factory=lambda: str(uuid4()))
    description: str = Field(..., min_length=1, max_length=1000)
    status: TaskStatus = TaskStatus.PENDING
    tags: list[str] = Field(default_factory=list)  # Factory for mutables!

# ❌ Never use mutable defaults
class Task(BaseModel):
    tags: list[str] = []  # WRONG!
```

### Database Queries

```python
# ✅ Always use parameterized queries
def get_task_by_id(self, task_id: int) -> Task | None:
    cursor = self.db.execute(
        "SELECT * FROM tasks WHERE id = ?",
        (task_id,)
    )
    row = cursor.fetchone()
    return Task(**row) if row else None

# ❌ NEVER use f-strings (SQL injection risk!)
cursor = self.db.execute(f"SELECT * FROM tasks WHERE id = {task_id}")
```

## Common CI Fixes

### Ruff Errors

```python
# UP038 - Use X | Y instead of Union[X, Y]
isinstance(x, int | float)  # ✅
isinstance(x, (int, float))  # ❌

# SIM105 - Use contextlib.suppress
with suppress(Exception):  # ✅
    do_something()

try:  # ❌
    do_something()
except Exception:
    pass
```

### Mypy Errors

```python
# Missing return type
def get_task(task_id: int) -> Task | None:  # ✅
    return repo.get_task(task_id)

# Untyped library import
import dateparser  # type: ignore[import-untyped]

# Cast for external libraries
from typing import cast
result = cast(dict[str, Any], external_lib.parse(data))
```

## Testing

```python
# Unit tests: tests/unit/test_dates.py
class TestParseDuration:
    """Test duration parsing."""

    def test_parse_days(self):
        """Should parse day duration."""
        result = parse_duration("3d")
        assert result == timedelta(days=3)

# Integration tests: tests/integration/test_add_command.py
class TestAddCommand:
    """Test task-ng add command."""

    def test_add_basic_task(self, cli_runner, temp_db):
        """Should add task with description."""
        result = cli_runner.invoke(app, ["add", "Test task"])
        assert result.exit_code == 0
        assert "Created task" in result.stdout
```

Coverage requirement: **80% minimum** (enforced by CI)

## Pre-Commit Checklist

Before committing, verify:

- [ ] `ruff check src tests` passes
- [ ] `ruff format --check src tests` passes
- [ ] `mypy src` passes
- [ ] `pytest --cov=taskng` passes with >80% coverage
- [ ] `./scripts/ci.sh` completes successfully
- [ ] All functions have return type annotations
- [ ] Public functions have Google-style docstrings
- [ ] New code has corresponding tests
- [ ] No secrets, API keys, or credentials

## Prohibited Patterns

### Never Use

- ❌ Bare `except:` clauses
- ❌ Mutable default arguments (`def foo(x=[]):`)
- ❌ SQL queries with f-strings
- ❌ `# type: ignore` without specific error code
- ❌ Old-style type hints (`List`, `Dict`, `Optional`)
- ❌ Incomplete implementations or TODO comments

### Phrases to Avoid

- ❌ "In a full implementation..."
- ❌ "This is a simplified version..."
- ❌ "For production, you should..."
- ❌ "TODO: Implement this later"
- ❌ "Great question!" / "You're absolutely right!"

## Working Guidelines

- **Understand first**: Read existing code before modifying
- **Follow patterns**: Match the style you observe in codebase
- **Test incrementally**: Write tests as you go, not at the end
- **Run CI frequently**: Check after each significant change
- **Production quality**: Write complete, production-ready code only
- **Read docs**: Consult CLAUDE.md and ARCHITECTURE.md when needed

## Understanding the Development Environment

### Poetry and Editable Installation

This project uses **Poetry** for dependency management and **editable installation** for development:

**Normal Installation (copies files):**
```
Your source:     /home/user/task-ng/src/taskng/
Installed copy:  ~/.local/lib/python3.13/site-packages/taskng/
When you edit:   Changes NOT reflected (Python runs the copy)
```

**Editable Installation (creates link):**
```
Your source:     /home/user/task-ng/src/taskng/
Installed link:  ~/.local/lib/.../taskng → points to source
When you edit:   Changes ARE reflected (Python runs your source)
```

The `poetry run pip install -e .` command creates this link, so your code changes take effect immediately.

### Python Bytecode Cache

Python compiles `.py` files to `.pyc` bytecode for performance. These live in `__pycache__/` directories.
Even with editable installation, Python may use old cached bytecode after you edit files.

**Solution:** The refresh script clears this cache before reinstalling.

### Isolated Development Environment

The dev script uses environment variables to isolate development from production:

```bash
# Production (normal task-ng command):
Config: ~/.config/taskng/config.toml
Data:   ~/.local/share/taskng/

# Development (./scripts/dev.sh):
Config: .dev/config.toml          ← Isolated
Data:   .dev/data/                ← Isolated
```

This is achieved by setting:
- `TASKNG_CONFIG_FILE=".dev/config.toml"`
- `TASKNG_DATA_DIR=".dev/data"`

## Development Scripts

### `./scripts/refresh.sh`
Run this after editing Python files to ensure changes take effect:
- Clears Python bytecode cache (`__pycache__`, `.pyc` files)
- Reinstalls package in editable mode
- Required when you modify CLI commands, function signatures, or any code

### `./scripts/dev.sh [args...]`
Convenience script that auto-refreshes and runs task-ng with **isolated development database**:
```bash
./scripts/dev.sh add "Test task" --tag urgent    # Auto-refresh + run
./scripts/dev.sh list                            # Auto-refresh + run
./scripts/dev.sh --help                          # Auto-refresh + run
```

**Features:**
- **Isolated database**: Uses `.dev/` directory for config and data (git-ignored)
- **Safe testing**: Never touches your production tasks in `~/.local/share/taskng`
- **Auto-refresh**: Clears cache and reinstalls before each run
- **Auto-setup**: Creates development config automatically on first run

**Workflow:**
```bash
# 1. Initial setup (once)
poetry install
poetry run pip install -e .

# 2. Daily development
nano src/taskng/cli/main.py           # Edit code
./scripts/dev.sh add "Test"           # Test changes (auto-refreshes)

# 3. Use production (unaffected)
task-ng add "Real task"               # Uses ~/.local/share/taskng
```

## Releasing to PyPI

The project uses GitLab CI/CD to automatically publish to PyPI when a git tag is pushed. Use the release script to automate the entire process.

### `./scripts/release.sh <version>`

Automates version bumping, git tagging, and pushing to trigger PyPI deployment:

```bash
# Semantic version bumping (auto-increment)
./scripts/release.sh patch              # 0.1.1 → 0.1.2
./scripts/release.sh minor              # 0.1.1 → 0.2.0
./scripts/release.sh major              # 0.1.1 → 1.0.0

# Explicit version
./scripts/release.sh 1.0.0              # Set to 1.0.0

# Preview changes without executing
./scripts/release.sh --dry-run patch    # Shows what would happen

# Skip confirmation prompts (for CI/automation)
./scripts/release.sh --force 0.2.0
```

**What the script does:**

1. ✅ Validates version format (semantic versioning)
2. ✅ Checks git working directory is clean
3. ✅ Updates `version` in `pyproject.toml`
4. ✅ Creates commit: `"Bump version to X.Y.Z"`
5. ✅ Creates git tag: `vX.Y.Z`
6. ✅ Pushes commit and tag to GitLab
7. ✅ GitLab CI automatically publishes to PyPI

**Prerequisites:**

- Clean git working directory (no uncommitted changes)
- Push access to the repository
- `PYPI_API_TOKEN` configured in GitLab CI/CD variables

**Manual release (if needed):**

```bash
# 1. Generate version metadata
python scripts/generate_version.py

# 2. Build the package
pip install --upgrade build twine
python -m build

# 3. Verify the build
twine check dist/*

# 4. Upload to PyPI
twine upload dist/*
```

**Monitor the release:**

After pushing a tag, GitLab CI will:
1. Run all tests and quality checks
2. Build the distribution packages
3. Upload to PyPI (if tests pass)

Check the pipeline at: https://gitlab.com/mathias.ewald/task-ng/-/pipelines
