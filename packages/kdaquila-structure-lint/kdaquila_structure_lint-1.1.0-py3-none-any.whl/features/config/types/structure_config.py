"""Structure validation configuration."""

from dataclasses import dataclass, field


@dataclass
class StructureConfig:
    """Configuration for structure validator."""

    src_root: str = "src"
    standard_folders: set[str] = field(
        default_factory=lambda: {"types", "utils", "constants", "tests"}
    )
    general_folder: str = "general"
    free_form_roots: set[str] = field(default_factory=set)
    allowed_files: set[str] = field(default_factory=lambda: {"README.md"})
    internally_allowed_files: set[str] = field(
        default_factory=lambda: {"__init__.py", "conftest.py"}
    )
    ignored_directories: set[str] = field(
        default_factory=lambda: {
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
            ".tox",
            ".coverage",
            ".egg-info",  # .egg-info added
        }
    )
