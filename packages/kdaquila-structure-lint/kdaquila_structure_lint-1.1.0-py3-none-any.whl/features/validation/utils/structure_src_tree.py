"""Validation logic for src tree structure."""

from pathlib import Path

from features.config import Config
from features.validation.utils.structure_base_folder import validate_base_folder


def validate_src_tree(root: Path, config: Config) -> list[str]:
    """Validate src tree structure."""
    errors: list[str] = []
    children = {
        c.name
        for c in root.iterdir()
        if c.is_dir() and c.name not in config.structure.ignored_directories
    }

    # Validate all subdirectories in src/ as base folders
    # No exact match required - accept any folders

    files = [c.name for c in root.iterdir() if c.is_file()]
    disallowed = [f for f in files if f not in config.structure.internally_allowed_files]
    if disallowed:
        errors.append(f"{root}: Files not allowed in root: {disallowed}")

    # Validate all actual subdirectories found in src/
    for child in children:
        base_path = root / child
        errors.extend(validate_base_folder(base_path, config))

    return errors
