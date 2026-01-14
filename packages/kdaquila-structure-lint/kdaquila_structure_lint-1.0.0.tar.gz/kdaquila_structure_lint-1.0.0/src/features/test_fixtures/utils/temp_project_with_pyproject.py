"""Fixture for creating a temporary project with pyproject.toml."""

from pathlib import Path

import pytest


@pytest.fixture
def temp_project_with_pyproject(tmp_path: Path) -> Path:
    """Create a temporary project with a basic pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[tool.structure-lint]
enabled = true
"""
    )
    return tmp_path
