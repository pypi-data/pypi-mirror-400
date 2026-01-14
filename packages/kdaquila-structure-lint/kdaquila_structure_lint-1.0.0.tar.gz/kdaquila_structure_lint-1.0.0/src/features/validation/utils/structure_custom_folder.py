"""Validates custom folder structure."""

from pathlib import Path

from features.config import Config
from features.validation.constants import INTERNALLY_ALLOWED_FILES
from features.validation.constants.internally_allowed import IGNORED_DIRECTORIES
from features.validation.utils.structure_general_folder import validate_general_folder


def validate_custom_folder(path: Path, config: Config, depth: int) -> list[str]:
    """Validate custom folder in structured base."""
    errors: list[str] = []

    # Merge internally allowed files with config allowed files
    allowed_files = INTERNALLY_ALLOWED_FILES + list(config.structure.allowed_files)
    general_folder = config.structure.general_folder
    standard_folders = config.structure.standard_folders

    # Skip validation for standard folders (they can be empty)
    if path.name in standard_folders:
        return errors

    # Check for disallowed files
    files = [c.name for c in path.iterdir() if c.is_file()]
    disallowed = [f for f in files if f not in allowed_files]
    if disallowed:
        errors.append(
            f"{path}: Disallowed files (only {allowed_files} allowed): {disallowed}"
        )

    children = [c for c in path.iterdir() if c.is_dir() and c.name not in IGNORED_DIRECTORIES]
    child_names = {c.name for c in children}

    has_general = general_folder in child_names
    has_standard = bool(child_names & standard_folders)
    has_custom = bool(child_names - standard_folders - {general_folder})

    if has_general and has_standard:
        errors.append(f"{path}: Cannot mix general and standard folders.")
    elif has_general and not has_custom:
        errors.append(f"{path}: general requires at least one custom subfolder.")
    elif has_custom or has_general:
        # Validate general folder if it exists
        if has_general:
            errors.extend(validate_general_folder(path / general_folder, config))
        # Validate all custom subfolders
        for child in children:
            if child.name not in (general_folder, *standard_folders):
                if depth >= 2:
                    errors.append(f"{child}: Exceeds max depth of 2 custom layers.")
                else:
                    errors.extend(validate_custom_folder(child, config, depth + 1))
    elif not has_standard:
        errors.append(f"{path}: Must contain standard folders or custom subfolders.")

    for std in child_names & standard_folders:
        std_path = path / std
        subdirs = [
            c
            for c in std_path.iterdir()
            if c.is_dir() and c.name not in IGNORED_DIRECTORIES
        ]
        if subdirs:
            errors.append(f"{std_path}: Standard folder cannot have subdirectories.")

    return errors
