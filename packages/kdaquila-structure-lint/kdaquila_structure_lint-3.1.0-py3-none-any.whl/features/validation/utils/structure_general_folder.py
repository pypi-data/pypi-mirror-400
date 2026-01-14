"""Validates general folder structure."""

from pathlib import Path

from features.config import Config
from features.validation.utils.pattern_match import matches_any_pattern


def validate_general_folder(path: Path, config: Config) -> list[str]:
    """Validate general folder contains only standard folders and allowed files."""
    errors: list[str] = []
    if not path.exists():
        return errors

    files_allowed_anywhere = config.structure.files_allowed_anywhere
    standard_folders = config.structure.standard_folders

    # Check for disallowed files
    py_files = [c.name for c in path.iterdir() if c.is_file() and c.suffix == ".py"]
    disallowed = [f for f in py_files if f not in files_allowed_anywhere]
    if disallowed:
        errors.append(
            f"{path}: Disallowed files (only {files_allowed_anywhere} allowed): {disallowed}"
        )

    children = [
        c for c in path.iterdir()
        if c.is_dir() and not matches_any_pattern(c.name, config.structure.ignored_folders)
    ]
    child_names = {c.name for c in children}
    invalid = child_names - standard_folders
    if invalid:
        errors.append(
            f"{path}: general can only contain standard folders, found: {invalid}"
        )

    # Validate that standard folders inside general don't have subdirectories
    for std in child_names & standard_folders:
        std_path = path / std
        subdirs = [
            c
            for c in std_path.iterdir()
            if c.is_dir() and not matches_any_pattern(c.name, config.structure.ignored_folders)
        ]
        if subdirs:
            errors.append(f"{std_path}: Standard folder cannot have subdirectories.")

    return errors
