"""Count lines in Python files."""

from pathlib import Path


def count_file_lines(file_path: Path) -> int:
    """Count the number of lines in a file."""
    try:
        with file_path.open(encoding="utf-8") as f:
            return sum(1 for _ in f)
    except (OSError, UnicodeDecodeError):
        # Return -1 to indicate error
        return -1
