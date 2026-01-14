"""Unit tests for hooks system."""

import stat
from pathlib import Path

from taskng.core.hooks import (
    HookRunner,
    get_hooks_dir,
    run_on_add_hooks,
    run_on_complete_hooks,
    run_on_modify_hooks,
)
from taskng.core.models import Task


class TestGetHooksDir:
    """Tests for get_hooks_dir function."""

    def test_returns_path(self) -> None:
        result = get_hooks_dir()
        assert isinstance(result, Path)

    def test_ends_with_hooks(self) -> None:
        result = get_hooks_dir()
        assert result.name == "hooks"


class TestHookRunner:
    """Tests for HookRunner class."""

    def test_init_sets_hooks_dir(self) -> None:
        runner = HookRunner()
        assert runner.hooks_dir is not None
        assert runner.hooks_dir.name == "hooks"

    def test_run_hooks_no_dir_returns_success(self, tmp_path: Path) -> None:
        runner = HookRunner()
        runner.hooks_dir = tmp_path / "nonexistent"

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert message == ""

    def test_run_hooks_empty_dir_returns_success(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert message == ""

    def test_run_hooks_non_executable_ignored(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create non-executable file
        hook_file = hooks_dir / "hook.sh"
        hook_file.write_text("#!/bin/bash\necho 'test'")

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert message == ""

    def test_run_hooks_executable_runs(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create executable hook
        hook_file = hooks_dir / "hook.sh"
        hook_file.write_text("#!/bin/bash\necho 'Hook ran'")
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert message == "Hook ran"

    def test_run_hooks_receives_task_json(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create hook that reads stdin
        hook_file = hooks_dir / "hook.py"
        hook_file.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "data = json.load(sys.stdin)\n"
            "print(data['task']['description'])\n"
        )
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        task = Task(description="My test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert message == "My test task"

    def test_run_hooks_with_old_task(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-modify"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create hook that reads both tasks
        hook_file = hooks_dir / "hook.py"
        hook_file.write_text(
            "#!/usr/bin/env python3\n"
            "import json, sys\n"
            "data = json.load(sys.stdin)\n"
            "print(f\"{data['old']['description']} -> {data['task']['description']}\")\n"
        )
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        old_task = Task(description="Old description")
        new_task = Task(description="New description")
        success, message = runner.run_hooks("on-modify", new_task, old_task)

        assert success is True
        assert message == "Old description -> New description"

    def test_run_hooks_failure_returns_error(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create failing hook
        hook_file = hooks_dir / "hook.sh"
        hook_file.write_text("#!/bin/bash\necho 'Error message' >&2\nexit 1")
        hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is False
        assert "hook.sh failed" in message
        assert "Error message" in message

    def test_run_hooks_multiple_hooks_run_in_order(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # Create multiple hooks
        for i in range(1, 4):
            hook_file = hooks_dir / f"0{i}-hook.sh"
            hook_file.write_text(f"#!/bin/bash\necho 'Hook {i}'")
            hook_file.chmod(hook_file.stat().st_mode | stat.S_IEXEC)

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is True
        assert "Hook 1" in message
        assert "Hook 2" in message
        assert "Hook 3" in message

    def test_run_hooks_stops_on_failure(self, tmp_path: Path) -> None:
        runner = HookRunner()
        hooks_dir = tmp_path / "hooks" / "on-add"
        hooks_dir.mkdir(parents=True)
        runner.hooks_dir = tmp_path / "hooks"

        # First hook succeeds
        hook1 = hooks_dir / "01-hook.sh"
        hook1.write_text("#!/bin/bash\necho 'Hook 1'")
        hook1.chmod(hook1.stat().st_mode | stat.S_IEXEC)

        # Second hook fails
        hook2 = hooks_dir / "02-hook.sh"
        hook2.write_text("#!/bin/bash\nexit 1")
        hook2.chmod(hook2.stat().st_mode | stat.S_IEXEC)

        # Third hook should not run
        hook3 = hooks_dir / "03-hook.sh"
        hook3.write_text("#!/bin/bash\necho 'Hook 3'")
        hook3.chmod(hook3.stat().st_mode | stat.S_IEXEC)

        task = Task(description="Test task")
        success, message = runner.run_hooks("on-add", task)

        assert success is False
        assert "02-hook.sh failed" in message


class TestRunOnAddHooks:
    """Tests for run_on_add_hooks function."""

    def test_returns_tuple(self) -> None:
        task = Task(description="Test task")
        result = run_on_add_hooks(task)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_success_when_no_hooks(self) -> None:
        task = Task(description="Test task")
        success, message = run_on_add_hooks(task)

        assert success is True


class TestRunOnModifyHooks:
    """Tests for run_on_modify_hooks function."""

    def test_returns_tuple(self) -> None:
        task = Task(description="Test task")
        old_task = Task(description="Old task")
        result = run_on_modify_hooks(task, old_task)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_success_when_no_hooks(self) -> None:
        task = Task(description="Test task")
        old_task = Task(description="Old task")
        success, message = run_on_modify_hooks(task, old_task)

        assert success is True


class TestRunOnCompleteHooks:
    """Tests for run_on_complete_hooks function."""

    def test_returns_tuple(self) -> None:
        task = Task(description="Test task")
        result = run_on_complete_hooks(task)

        assert isinstance(result, tuple)
        assert len(result) == 2

    def test_success_when_no_hooks(self) -> None:
        task = Task(description="Test task")
        success, message = run_on_complete_hooks(task)

        assert success is True
