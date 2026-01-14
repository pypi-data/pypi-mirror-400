"""Helpers for fragua-sets."""

from pathlib import Path


def get_project_root() -> Path:
    """
    Return the current project root directory.

    This is defined as the current working directory
    where the process was started.
    """
    return Path.cwd()
