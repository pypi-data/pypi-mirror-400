"""Fixture for creating a Config object with custom settings."""

from pathlib import Path

import pytest

from features.config import (
    Config,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)


@pytest.fixture
def custom_config(tmp_path: Path) -> Config:
    """Create a Config object with custom settings."""
    return Config(
        enabled=True,
        project_root=tmp_path,
        validators=ValidatorToggles(
            structure=True,
            line_limits=True,
            one_per_file=True,
        ),
        line_limits=LineLimitsConfig(
            max_lines=100,
            search_paths=["src", "lib"],
        ),
        one_per_file=OnePerFileConfig(
            search_paths=["src", "lib"],
        ),
        structure=StructureConfig(
            src_root="lib",
            standard_folders={"types", "utils", "helpers"},
            general_folder="common",
            free_form_roots={"experimental"},
            allowed_files={"README.md", "NOTES.md"},
        ),
    )
