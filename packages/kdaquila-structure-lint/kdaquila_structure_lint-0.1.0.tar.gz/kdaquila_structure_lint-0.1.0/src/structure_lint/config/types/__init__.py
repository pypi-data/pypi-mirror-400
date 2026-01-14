"""Configuration type definitions for structure-lint."""

from structure_lint.config.types.validator_toggles import ValidatorToggles
from structure_lint.config.types.line_limits_config import LineLimitsConfig
from structure_lint.config.types.one_per_file_config import OnePerFileConfig
from structure_lint.config.types.structure_config import StructureConfig
from structure_lint.config.types.config import Config

__all__ = [
    "ValidatorToggles",
    "LineLimitsConfig",
    "OnePerFileConfig",
    "StructureConfig",
    "Config",
]
