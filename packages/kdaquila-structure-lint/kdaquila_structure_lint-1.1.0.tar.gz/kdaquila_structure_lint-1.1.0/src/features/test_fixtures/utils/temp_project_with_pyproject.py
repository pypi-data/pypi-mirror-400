"""Helper function for creating a temporary project with pyproject.toml."""

from pathlib import Path


def create_temp_project_with_pyproject(tmp_path: Path) -> Path:
    """Create a temporary project with a basic pyproject.toml.

    Args:
        tmp_path: The temporary path to use as the project directory.

    Returns:
        The tmp_path with a pyproject.toml file created.
    """
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[tool.structure-lint]
enabled = true
"""
    )
    return tmp_path
