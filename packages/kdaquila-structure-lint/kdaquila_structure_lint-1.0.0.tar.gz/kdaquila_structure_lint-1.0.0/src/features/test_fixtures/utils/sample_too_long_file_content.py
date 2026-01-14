"""Fixture for Python file content that exceeds line limits."""

import pytest


@pytest.fixture
def sample_too_long_file_content() -> str:
    """Return content that exceeds typical line limits."""
    lines = [f"# Line {i}" for i in range(1, 201)]
    return "\n".join(lines)
