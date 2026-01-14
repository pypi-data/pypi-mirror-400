"""Validate top-level definitions in Python files."""

from pathlib import Path

from features.validation.utils.definition_counter_counter import count_top_level_definitions


def validate_file_definitions(file_path: Path) -> str | None:
    """Check if file has more than one top-level definition. Returns error or None."""
    result = count_top_level_definitions(file_path)

    if result is None:
        return f"{file_path}: Error parsing file"

    count, names = result
    if count > 1:
        return f"{file_path}: {count} definitions (expected ≤1): {', '.join(names)}"

    return None
