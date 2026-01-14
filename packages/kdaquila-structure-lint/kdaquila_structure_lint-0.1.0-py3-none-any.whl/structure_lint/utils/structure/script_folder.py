"""Validates individual script folder structure."""

from pathlib import Path

from structure_lint.config import Config


def validate_script_folder(path: Path, config: Config) -> list[str]:
    """Validate individual script folder (1 level deep)."""
    errors: list[str] = []

    general_folder = config.structure.general_folder
    standard_folders = config.structure.standard_folders

    children = [c for c in path.iterdir() if c.is_dir() and c.name != "__pycache__"]
    child_names = {c.name for c in children}

    if general_folder in child_names:
        errors.append(f"{path}: general folder not allowed in scripts tree.")

    custom_folders = child_names - standard_folders
    if custom_folders:
        errors.append(
            f"{path}: Nested custom folders not allowed in scripts tree: {custom_folders}"
        )

    return errors
