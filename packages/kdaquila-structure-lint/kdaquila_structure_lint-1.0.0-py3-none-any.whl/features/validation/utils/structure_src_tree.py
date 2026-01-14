"""Validation logic for src tree structure."""

from pathlib import Path

from features.config import Config
from features.validation.constants.internally_allowed import IGNORED_DIRECTORIES
from features.validation.utils.structure_base_folder import validate_base_folder


def validate_src_tree(root: Path, config: Config) -> list[str]:
    """Validate src tree structure."""
    errors: list[str] = []
    children = {c.name for c in root.iterdir() if c.is_dir() and c.name not in IGNORED_DIRECTORIES}

    # Validate all subdirectories in src/ as base folders
    # No exact match required - accept any folders

    files = [c.name for c in root.iterdir() if c.is_file()]
    if files:
        errors.append(f"{root}: Files not allowed in root: {files}")

    # Validate all actual subdirectories found in src/
    for child in children:
        base_path = root / child
        errors.extend(validate_base_folder(base_path, config))

    return errors
