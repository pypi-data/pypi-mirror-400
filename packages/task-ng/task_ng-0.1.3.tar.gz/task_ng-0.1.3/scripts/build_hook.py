"""Hatchling build hook to generate version info before building."""

import subprocess
from pathlib import Path

from hatchling.builders.hooks.plugin.interface import BuildHookInterface


class CustomBuildHook(BuildHookInterface):
    """Custom build hook to generate version information."""

    def initialize(self, version: str, build_data: dict) -> None:
        """Run before the build starts.

        Args:
            version: The version of the project
            build_data: Build configuration data
        """
        # Run the version generation script
        script_path = Path(__file__).parent / "generate_version.py"
        subprocess.run(["python", str(script_path)], check=True)
