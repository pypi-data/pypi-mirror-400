"""Helper function for creating temporary project directories."""

from pathlib import Path


def create_temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory.

    Args:
        tmp_path: The temporary path to use as the project directory.

    Returns:
        The tmp_path as the project directory.
    """
    return tmp_path
