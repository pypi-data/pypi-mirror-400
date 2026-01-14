"""Configuration loading and management for structure-lint.

This module re-exports everything from the config package for backward compatibility.
"""

from structure_lint.config.types import (
    Config,
    ValidatorToggles,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
)
from structure_lint.config.project_root import find_project_root
from structure_lint.config.loader import load_config

__all__ = [
    "Config",
    "ValidatorToggles",
    "LineLimitsConfig",
    "OnePerFileConfig",
    "StructureConfig",
    "find_project_root",
    "load_config",
]
