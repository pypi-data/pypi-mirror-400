"""Fixture for creating a minimal Config object with defaults."""

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
def minimal_config(tmp_path: Path) -> Config:
    """Create a minimal Config object with all defaults."""
    return Config(
        enabled=True,
        project_root=tmp_path,
        validators=ValidatorToggles(),
        line_limits=LineLimitsConfig(),
        one_per_file=OnePerFileConfig(),
        structure=StructureConfig(),
    )
