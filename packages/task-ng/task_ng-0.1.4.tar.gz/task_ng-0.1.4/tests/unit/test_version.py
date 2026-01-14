"""Test version and basic imports."""

import re

from taskng import __version__


def test_version():
    """Version should be a non-empty string."""
    assert __version__
    assert isinstance(__version__, str)


def test_version_format():
    """Version should start with semver-like format (e.g., 0.1.1 or 0.1.2.dev0+g...)."""
    # Match versions like: 0.1.1, 0.1.2.dev0, 0.1.2.dev0+g12345678
    pattern = r"^\d+\.\d+\.\d+"
    assert re.match(pattern, __version__), (
        f"Version '{__version__}' doesn't match expected pattern"
    )
