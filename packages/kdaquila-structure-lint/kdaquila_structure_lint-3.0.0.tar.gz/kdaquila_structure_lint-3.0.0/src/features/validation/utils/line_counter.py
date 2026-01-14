"""Counts and validates lines in files.

This module re-exports everything from the line_counter modules for backward compatibility.
"""

from features.validation.utils.line_counter_counter import count_file_lines
from features.validation.utils.line_counter_validator import validate_file_lines

__all__ = [
    "count_file_lines",
    "validate_file_lines",
]
