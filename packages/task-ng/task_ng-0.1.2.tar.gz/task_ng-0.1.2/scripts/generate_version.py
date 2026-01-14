#!/usr/bin/env python3
"""Generate version info file with git commit details."""

import subprocess
from pathlib import Path


def get_git_info() -> tuple[str, str]:
    """Get git commit hash and date.

    Returns:
        Tuple of (commit_hash, commit_date).
    """
    try:
        commit = subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        date = subprocess.check_output(
            ["git", "log", "-1", "--format=%ci"],
            stderr=subprocess.DEVNULL,
            text=True,
        ).strip()

        return commit, date
    except (subprocess.CalledProcessError, FileNotFoundError):
        return "unknown", "unknown"


def generate_version_file() -> None:
    """Generate _version_info.py with git details."""
    commit, date = get_git_info()

    content = f'''"""Version information including git commit details.

This file is generated at build time by scripts/generate_version.py.
Do not edit manually.
"""

# These values are updated at build time
GIT_COMMIT = "{commit}"
GIT_DATE = "{date}"
'''

    version_file = Path(__file__).parent.parent / "src" / "taskng" / "_version_info.py"
    version_file.write_text(content)
    print(f"Generated {version_file}")
    print(f"  Commit: {commit}")
    print(f"  Date: {date}")


if __name__ == "__main__":
    generate_version_file()
