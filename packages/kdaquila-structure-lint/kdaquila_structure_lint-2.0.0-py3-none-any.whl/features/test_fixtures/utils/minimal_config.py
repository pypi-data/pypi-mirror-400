"""Helper function for creating a minimal Config object with defaults."""

from pathlib import Path

from features.config import (
    Config,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)


def create_minimal_config(tmp_path: Path) -> Config:
    """Create a minimal Config object with all defaults.

    Args:
        tmp_path: The temporary path to use as project root.

    Returns:
        A Config object with default settings.
    """
    return Config(
        enabled=True,
        project_root=tmp_path,
        validators=ValidatorToggles(),
        line_limits=LineLimitsConfig(),
        one_per_file=OnePerFileConfig(),
        structure=StructureConfig(),
    )
