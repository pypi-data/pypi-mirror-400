"""Helper function for creating Python test files dynamically."""

from pathlib import Path


def create_python_file(
    tmp_path: Path,
    relative_path: str,
    content: str,
    base_dir: Path | None = None,
) -> Path:
    """Create a Python file at relative_path with given content.

    Args:
        tmp_path: The temporary path (used as default base directory).
        relative_path: Path relative to base_dir (e.g., "src/module.py").
        content: Content to write to the file.
        base_dir: Base directory (defaults to tmp_path if None).

    Returns:
        Absolute path to created file.
    """
    if base_dir is None:
        base_dir = tmp_path

    file_path = base_dir / relative_path
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_text(content, encoding="utf-8")
    return file_path
