"""Validates structured base folder (features)."""

from pathlib import Path

from features.config import Config
from features.validation.utils.pattern_match import matches_any_pattern
from features.validation.utils.structure_custom_folder import validate_custom_folder


def validate_base_folder(base_path: Path, config: Config) -> list[str]:
    """Validate features base folder structure."""
    errors: list[str] = []

    # Prevent base folders from using standard folder names
    if base_path.name in config.structure.standard_folders:
        errors.append(
            f"{base_path}: Base folder '{base_path.name}' conflicts with standard "
            f"folder names {config.structure.standard_folders}. "
            f"Base folders (features) cannot use these reserved names."
        )
        return errors

    # Check for files in base folder (only allowed files like __init__.py)
    files = [c.name for c in base_path.iterdir() if c.is_file()]
    disallowed = [f for f in files if f not in config.structure.allowed_files]
    if disallowed:
        errors.append(f"{base_path}: Files not allowed in root: {disallowed}")

    # Validate subdirectories
    for custom in base_path.iterdir():
        if custom.is_dir() and not matches_any_pattern(
            custom.name, config.structure.ignored_folders
        ):
            errors.extend(validate_custom_folder(custom, config, depth=1))
    return errors
