"""Constant for Python file content that exceeds line limits."""

SAMPLE_TOO_LONG_FILE_CONTENT: str = "\n".join([f"# Line {i}" for i in range(1, 201)])
