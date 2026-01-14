"""Validates structured base folder (features)."""

from pathlib import Path

from structure_lint.config import Config
from structure_lint.utils.structure.custom_folder import validate_custom_folder


def validate_base_folder(base_path: Path, config: Config) -> list[str]:
    """Validate features base folder structure."""
    errors: list[str] = []
    for custom in base_path.iterdir():
        if custom.is_dir() and custom.name != "__pycache__":
            errors.extend(validate_custom_folder(custom, config, depth=1))
    return errors
