"""Fixture for valid Python file content."""

import pytest


@pytest.fixture
def sample_valid_file_content() -> str:
    """Return content for a valid Python file."""
    return """def hello():
    '''A simple function.'''
    return "Hello, world!"
"""
