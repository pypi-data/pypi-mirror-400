"""Hooks system for Task-NG."""

import json
import subprocess
from pathlib import Path

from taskng.config.settings import get_config
from taskng.core.models import Task


def get_hooks_dir() -> Path:
    """Get hooks directory path.

    Returns:
        Path to hooks directory.
    """
    config = get_config()
    config_dir = Path(config.config_path).parent
    return config_dir / "hooks"


class HookRunner:
    """Runs hook scripts for task operations."""

    def __init__(self) -> None:
        """Initialize hook runner."""
        self.hooks_dir = get_hooks_dir()

    def run_hooks(
        self,
        event: str,
        task: Task,
        old_task: Task | None = None,
    ) -> tuple[bool, str]:
        """Run all hooks for an event.

        Args:
            event: Hook event (on-add, on-modify, on-complete)
            task: Current task data
            old_task: Previous task data (for modify)

        Returns:
            Tuple of (success, message)
        """
        hooks_dir = self.hooks_dir / event
        if not hooks_dir.exists():
            return True, ""

        # Get hook scripts (executable files only)
        hooks = sorted(hooks_dir.glob("*"))
        hooks = [h for h in hooks if h.is_file() and h.stat().st_mode & 0o111]

        if not hooks:
            return True, ""

        # Prepare input JSON
        input_data: dict[str, dict[str, object]] = {
            "task": json.loads(task.model_dump_json()),
        }
        if old_task:
            input_data["old"] = json.loads(old_task.model_dump_json())

        input_json = json.dumps(input_data)

        # Run each hook
        messages: list[str] = []
        for hook in hooks:
            success, msg = self._run_hook(hook, input_json)
            if not success:
                return False, f"Hook {hook.name} failed: {msg}"
            if msg:
                messages.append(msg)

        return True, "\n".join(messages)

    def _run_hook(self, hook_path: Path, input_json: str) -> tuple[bool, str]:
        """Run a single hook script.

        Args:
            hook_path: Path to hook script
            input_json: JSON input to pass

        Returns:
            Tuple of (success, output)
        """
        try:
            result = subprocess.run(
                [str(hook_path)],
                input=input_json,
                capture_output=True,
                text=True,
                timeout=30,
            )

            if result.returncode != 0:
                return False, result.stderr or f"Exit code {result.returncode}"

            return True, result.stdout.strip()

        except subprocess.TimeoutExpired:
            return False, "Hook timed out"
        except Exception as e:
            return False, str(e)


def run_on_add_hooks(task: Task) -> tuple[bool, str]:
    """Run on-add hooks.

    Args:
        task: New task

    Returns:
        Tuple of (success, message)
    """
    runner = HookRunner()
    return runner.run_hooks("on-add", task)


def run_on_modify_hooks(task: Task, old_task: Task) -> tuple[bool, str]:
    """Run on-modify hooks.

    Args:
        task: Modified task
        old_task: Original task

    Returns:
        Tuple of (success, message)
    """
    runner = HookRunner()
    return runner.run_hooks("on-modify", task, old_task)


def run_on_complete_hooks(task: Task) -> tuple[bool, str]:
    """Run on-complete hooks.

    Args:
        task: Completed task

    Returns:
        Tuple of (success, message)
    """
    runner = HookRunner()
    return runner.run_hooks("on-complete", task)
