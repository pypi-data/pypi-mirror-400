"""Utilities function types."""

from pathlib import Path
from typing import Any, Callable, List, Union


PathLike = Union[str, Path]

# -------------
# PATH CHECKING
# -------------


def path_exists(path: PathLike) -> bool:
    """
    Check whether a filesystem path exists.

    This function checks for the existence of a file system
    entry (file or directory) without validating its type.

    Parameters
    ----------
    path:
        Path to a file or directory.

    Returns
    -------
    bool
        True if the path exists, False otherwise.
    """
    return Path(path).exists()


def ensure_dir_exists(path: PathLike) -> Path:
    """
    Ensure that a directory exists.

    If the directory does not exist, it is created along with
    all required parent directories. If the path exists but is
    not a directory, a ValueError is raised.

    Parameters
    ----------
    path:
        Path to the directory.

    Returns
    -------
    Path
        Path object pointing to the ensured directory.

    Raises
    ------
    ValueError
        If the path exists and is not a directory.
    """
    dir_path = Path(path)

    if dir_path.exists() and not dir_path.is_dir():
        raise ValueError(f"Path exists and is not a directory: {dir_path}")

    dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def ensure_parent_dir_exists(path: PathLike) -> Path:
    """
    Ensure that the parent directory of a file path exists.

    This function is intended for file outputs. It creates
    the parent directory if it does not exist.

    Parameters
    ----------
    path:
        File path whose parent directory should be ensured.

    Returns
    -------
    Path
        Path object pointing to the original file path.
    """
    file_path = Path(path)
    parent_dir = file_path.parent

    parent_dir.mkdir(parents=True, exist_ok=True)
    return file_path


UTILITY_FUNCTIONS: List[Callable[..., Any]] = [
    path_exists,
    ensure_dir_exists,
    ensure_parent_dir_exists,
]
