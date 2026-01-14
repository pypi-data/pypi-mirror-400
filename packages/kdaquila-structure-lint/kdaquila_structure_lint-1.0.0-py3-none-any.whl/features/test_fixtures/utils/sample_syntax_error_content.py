"""Fixture for Python file content with syntax errors."""

import pytest


@pytest.fixture
def sample_syntax_error_content() -> str:
    """Return content with Python syntax errors."""
    return """def broken_function(
    # Missing closing parenthesis
    return "incomplete"
"""
