"""Configuration loading and management for structure-lint.

This module re-exports everything from the config package for backward compatibility.
"""

from features.config.types import (
    Config,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)
from features.config.utils.loader import load_config
from features.config.utils.project_root import find_project_root

__all__ = [
    "Config",
    "LineLimitsConfig",
    "OnePerFileConfig",
    "StructureConfig",
    "ValidatorToggles",
    "find_project_root",
    "load_config",
]
