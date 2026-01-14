"""Validation logic for scripts tree structure."""

from pathlib import Path

from structure_lint.config import Config
from structure_lint.utils.structure.script_folder import validate_script_folder


def validate_scripts_tree(root: Path, config: Config) -> list[str]:
    """Validate scripts tree structure."""
    errors: list[str] = []

    files = [c.name for c in root.iterdir() if c.is_file() and c.name != "__init__.py"]
    if files:
        errors.append(f"{root}: Files not allowed in root, use custom folders: {files}")

    for custom in root.iterdir():
        if not custom.is_dir():
            continue
        errors.extend(validate_script_folder(custom, config))

    return errors
