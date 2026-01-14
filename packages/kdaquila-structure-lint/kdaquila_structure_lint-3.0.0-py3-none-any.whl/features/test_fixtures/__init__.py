"""Test fixtures feature - provides reusable helper functions and constants.

This feature organizes all test helpers into individual files following
the one-per-file rule:

Helper Functions (create_ prefix):
- create_temp_project: Creates a temporary project directory
- create_temp_project_with_pyproject: Creates a temporary project with pyproject.toml
- create_minimal_config: Creates a Config object with defaults
- create_custom_config: Creates a Config object with custom settings
- create_python_file: Factory for creating test files

Constants (UPPERCASE):
- SAMPLE_VALID_FILE_CONTENT: Valid Python file content
- SAMPLE_TOO_LONG_FILE_CONTENT: Content exceeding line limits
- SAMPLE_MULTIPLE_DEFINITIONS_CONTENT: Content with multiple definitions
- SAMPLE_EMPTY_FILE_CONTENT: Empty file content
- SAMPLE_SYNTAX_ERROR_CONTENT: Content with syntax errors
"""

from features.test_fixtures.utils import (
    SAMPLE_EMPTY_FILE_CONTENT,
    SAMPLE_MULTIPLE_DEFINITIONS_CONTENT,
    SAMPLE_SYNTAX_ERROR_CONTENT,
    SAMPLE_TOO_LONG_FILE_CONTENT,
    SAMPLE_VALID_FILE_CONTENT,
    create_custom_config,
    create_minimal_config,
    create_python_file,
    create_temp_project,
    create_temp_project_with_pyproject,
)

__all__ = [
    "SAMPLE_EMPTY_FILE_CONTENT",
    "SAMPLE_MULTIPLE_DEFINITIONS_CONTENT",
    "SAMPLE_SYNTAX_ERROR_CONTENT",
    "SAMPLE_TOO_LONG_FILE_CONTENT",
    "SAMPLE_VALID_FILE_CONTENT",
    "create_custom_config",
    "create_minimal_config",
    "create_python_file",
    "create_temp_project",
    "create_temp_project_with_pyproject",
]
