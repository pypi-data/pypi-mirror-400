"""Fixture for empty Python file content."""

import pytest


@pytest.fixture
def sample_empty_file_content() -> str:
    """Return empty file content."""
    return ""
