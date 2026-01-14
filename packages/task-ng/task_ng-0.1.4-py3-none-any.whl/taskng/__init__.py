"""Task-NG: A modern Python reimagining of Taskwarrior."""

from importlib.metadata import PackageNotFoundError, version

try:
    __version__ = version("task-ng")
except PackageNotFoundError:
    __version__ = "0.0.0.dev0"  # Fallback for uninstalled package

__author__ = "Task-NG Contributors"
