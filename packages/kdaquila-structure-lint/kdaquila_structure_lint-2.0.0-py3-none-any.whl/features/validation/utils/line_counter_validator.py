"""Validate line counts in Python files."""

from pathlib import Path

from features.validation.utils.line_counter_counter import count_file_lines


def validate_file_lines(file_path: Path, max_lines: int) -> str | None:
    """Check if file exceeds line limit. Returns error message or None."""
    line_count = count_file_lines(file_path)

    if line_count == -1:
        return f"{file_path}: Error reading file"

    if line_count > max_lines:
        excess = line_count - max_lines
        return f"{file_path}: {line_count} lines (exceeds limit by {excess})"

    return None
