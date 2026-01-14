"""Test fixtures feature - provides reusable pytest fixtures.

This feature organizes all test fixtures into individual files following
the one-per-file rule:
- temp_project: Temporary project directory fixture
- temp_project_with_pyproject: Temporary project with pyproject.toml
- minimal_config: Config object with defaults
- custom_config: Config object with custom settings
- python_file_factory: Factory for creating test files
- sample_valid_file_content: Valid Python file content
- sample_too_long_file_content: Content exceeding line limits
- sample_multiple_definitions_content: Content with multiple definitions
- sample_empty_file_content: Empty file content
- sample_syntax_error_content: Content with syntax errors
"""

from features.test_fixtures.utils import (
    custom_config,
    minimal_config,
    python_file_factory,
    sample_empty_file_content,
    sample_multiple_definitions_content,
    sample_syntax_error_content,
    sample_too_long_file_content,
    sample_valid_file_content,
    temp_project,
    temp_project_with_pyproject,
)

__all__ = [
    "custom_config",
    "minimal_config",
    "python_file_factory",
    "sample_empty_file_content",
    "sample_multiple_definitions_content",
    "sample_syntax_error_content",
    "sample_too_long_file_content",
    "sample_valid_file_content",
    "temp_project",
    "temp_project_with_pyproject",
]
