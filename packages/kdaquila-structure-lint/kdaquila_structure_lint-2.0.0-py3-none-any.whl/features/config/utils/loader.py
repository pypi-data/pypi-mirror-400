"""Configuration loading from pyproject.toml."""

import sys
from pathlib import Path

from features.config.types import (
    Config,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)
from features.config.utils.project_root import find_project_root

# Python 3.11+ has tomllib, older versions need tomli
if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


def load_config(
    project_root: Path | None = None,
    config_path: Path | None = None
) -> Config:
    """Load configuration from pyproject.toml with defaults.

    Args:
        project_root: Override project root (if None, auto-detect)
        config_path: Path to pyproject.toml (if None, search from cwd)

    Returns:
        Config object with user settings merged with defaults
    """
    # Step 1: Determine project root
    if project_root is None:
        project_root = config_path.parent if config_path is not None else find_project_root()

    # Step 2: Find pyproject.toml
    if config_path is None:
        config_path = project_root / "pyproject.toml"

    # Step 3: Parse TOML (if file exists)
    user_config = {}
    if config_path.exists():
        with config_path.open("rb") as f:
            toml_data = tomllib.load(f)
            user_config = toml_data.get("tool", {}).get("structure-lint", {})

    # Step 4: Deep merge with defaults
    enabled = user_config.get("enabled", True)

    # Validators section
    validators_data = user_config.get("validators", {})
    validators = ValidatorToggles(
        structure=validators_data.get("structure", False),
        line_limits=validators_data.get("line_limits", True),
        one_per_file=validators_data.get("one_per_file", True),
    )

    # Line limits section
    line_limits_data = user_config.get("line_limits", {})
    line_limits = LineLimitsConfig(
        max_lines=line_limits_data.get("max_lines", 150),
        search_paths=line_limits_data.get("search_paths", ["src"]),
    )

    # One-per-file section
    one_per_file_data = user_config.get("one_per_file", {})
    one_per_file = OnePerFileConfig(
        search_paths=one_per_file_data.get("search_paths", ["src"]),
    )

    # Structure section
    structure_data = user_config.get("structure", {})
    structure = StructureConfig(
        src_root=structure_data.get("src_root", "src"),
        standard_folders=set(
            structure_data.get("standard_folders", ["types", "utils", "constants", "tests"])
        ),
        general_folder=structure_data.get("general_folder", "general"),
        free_form_roots=set(structure_data.get("free_form_roots", [])),
        allowed_files=set(structure_data.get("allowed_files", ["__init__.py", "README.md"])),
        ignored_folders=set(
            structure_data.get(
                "ignored_folders",
                ["__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache",
                 ".hypothesis", ".tox", ".coverage", "*.egg-info"]
            )
        ),
    )

    return Config(
        enabled=enabled,
        project_root=project_root,
        validators=validators,
        line_limits=line_limits,
        one_per_file=one_per_file,
        structure=structure,
    )
