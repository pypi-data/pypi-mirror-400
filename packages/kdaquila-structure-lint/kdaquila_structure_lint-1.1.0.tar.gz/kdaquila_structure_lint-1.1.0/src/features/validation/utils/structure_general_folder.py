"""Validates general folder structure."""

from pathlib import Path

from features.config import Config


def validate_general_folder(path: Path, config: Config) -> list[str]:
    """Validate general folder contains only standard folders and allowed files."""
    errors: list[str] = []
    if not path.exists():
        return errors

    # Merge internally allowed files with config allowed files
    allowed_files = list(config.structure.internally_allowed_files) + list(
        config.structure.allowed_files
    )
    standard_folders = config.structure.standard_folders

    # Check for disallowed files
    files = [c.name for c in path.iterdir() if c.is_file()]
    disallowed = [f for f in files if f not in allowed_files]
    if disallowed:
        errors.append(
            f"{path}: Disallowed files (only {allowed_files} allowed): {disallowed}"
        )

    children = {c.name for c in path.iterdir() if c.is_dir()}
    invalid = children - standard_folders
    if invalid:
        errors.append(
            f"{path}: general can only contain standard folders, found: {invalid}"
        )

    return errors
