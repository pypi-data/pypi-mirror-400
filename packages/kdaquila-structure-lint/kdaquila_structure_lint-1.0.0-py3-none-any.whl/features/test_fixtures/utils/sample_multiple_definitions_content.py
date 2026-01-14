"""Fixture for Python file content with multiple top-level definitions."""

import pytest


@pytest.fixture
def sample_multiple_definitions_content() -> str:
    """Return content with multiple top-level definitions."""
    return """def function_one():
    pass

def function_two():
    pass

class MyClass:
    pass
"""
