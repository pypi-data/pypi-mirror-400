"""Files and directories that are always allowed/ignored internally."""

# Files that are always allowed internally in any folder
INTERNALLY_ALLOWED_FILES = ["__init__.py", "conftest.py"]

# Directories that should be ignored during structure validation
IGNORED_DIRECTORIES = {
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".hypothesis",
    ".tox",
    ".coverage",
}
