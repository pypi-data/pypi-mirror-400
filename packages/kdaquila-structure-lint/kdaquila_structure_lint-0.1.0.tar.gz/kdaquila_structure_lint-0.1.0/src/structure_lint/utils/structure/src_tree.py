"""Validation logic for src tree structure."""

from pathlib import Path

from structure_lint.config import Config
from structure_lint.utils.structure.base_folder import validate_base_folder


def validate_src_tree(root: Path, config: Config) -> list[str]:
    """Validate src tree structure."""
    errors: list[str] = []
    children = {c.name for c in root.iterdir() if c.is_dir() and c.name != "__pycache__"}

    src_base_folders = config.structure.src_base_folders
    if children != src_base_folders:
        missing = src_base_folders - children
        extra = children - src_base_folders
        if missing:
            errors.append(f"{root}: Missing base folders: {missing}")
        if extra:
            errors.append(f"{root}: Unexpected folders: {extra}")

    files = [c.name for c in root.iterdir() if c.is_file()]
    if files:
        errors.append(f"{root}: Files not allowed in root: {files}")

    free_form_bases = config.structure.free_form_bases
    for base in src_base_folders:
        base_path = root / base
        if base_path.exists():
            if base in free_form_bases:
                continue
            errors.extend(validate_base_folder(base_path, config))

    return errors
