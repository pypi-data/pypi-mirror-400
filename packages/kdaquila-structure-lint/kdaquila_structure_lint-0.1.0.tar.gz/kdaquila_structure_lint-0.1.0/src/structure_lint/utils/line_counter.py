"""Counts and validates lines in files.

This module re-exports everything from the line_counter package for backward compatibility.
"""

from structure_lint.utils.line_counter.counter import count_file_lines
from structure_lint.utils.line_counter.validator import validate_file_lines

__all__ = [
    "count_file_lines",
    "validate_file_lines",
]
