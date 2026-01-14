"""Main configuration object."""

from dataclasses import dataclass
from pathlib import Path

from features.config.types.line_limits_config import LineLimitsConfig
from features.config.types.one_per_file_config import OnePerFileConfig
from features.config.types.structure_config import StructureConfig
from features.config.types.validator_toggles import ValidatorToggles


@dataclass
class Config:
    """Master configuration object."""
    enabled: bool
    project_root: Path
    validators: ValidatorToggles
    line_limits: LineLimitsConfig
    one_per_file: OnePerFileConfig
    structure: StructureConfig
