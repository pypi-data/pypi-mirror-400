"""Factory fixture for creating Python test files dynamically."""

from collections.abc import Callable
from pathlib import Path

import pytest


@pytest.fixture
def python_file_factory(tmp_path: Path) -> Callable[[str, str, Path | None], Path]:
    """Factory fixture to create Python files with specified content."""

    def _create_python_file(
        relative_path: str,
        content: str,
        base_dir: Path | None = None
    ) -> Path:
        """Create a Python file at relative_path with given content.

        Args:
            relative_path: Path relative to base_dir (e.g., "src/module.py")
            content: Content to write to the file
            base_dir: Base directory (defaults to tmp_path)

        Returns:
            Absolute path to created file
        """
        if base_dir is None:
            base_dir = tmp_path

        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_python_file
