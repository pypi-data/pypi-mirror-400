"""Finds Python files recursively."""

from pathlib import Path

EXCLUDE_DIRS = {".git", ".hg", ".svn", ".venv", "venv", "node_modules", "__pycache__"}


def find_python_files(root: Path) -> list[Path]:
    """Find all Python files in root, excluding common non-source directories."""
    python_files = []
    for py_file in root.rglob("*.py"):
        # Skip if any parent directory is in EXCLUDE_DIRS
        if any(part in EXCLUDE_DIRS for part in py_file.parts):
            continue
        python_files.append(py_file)
    return sorted(python_files, key=lambda p: p.stat().st_mtime, reverse=True)
