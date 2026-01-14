"""Counts and validates top-level definitions in files.

This module re-exports everything from the definition_counter package for backward compatibility.
"""

from structure_lint.utils.definition_counter.counter import count_top_level_definitions
from structure_lint.utils.definition_counter.validator import validate_file_definitions

__all__ = [
    "count_top_level_definitions",
    "validate_file_definitions",
]
