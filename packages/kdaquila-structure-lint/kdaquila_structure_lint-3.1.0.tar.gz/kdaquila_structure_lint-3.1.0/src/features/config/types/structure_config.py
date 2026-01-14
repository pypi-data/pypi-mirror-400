"""Structure validation configuration."""

from dataclasses import dataclass, field


@dataclass
class StructureConfig:
    """Configuration for structure validator."""

    strict_format_roots: set[str] = field(default_factory=lambda: {"src"})
    folder_depth: int = 2
    standard_folders: set[str] = field(
        default_factory=lambda: {"types", "utils", "constants", "tests"}
    )
    general_folder: str = "general"
    files_allowed_anywhere: set[str] = field(default_factory=lambda: {"__init__.py"})
    ignored_folders: set[str] = field(
        default_factory=lambda: {
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
            ".tox",
            ".coverage",
            "*.egg-info",  # matches any .egg-info directory
        }
    )
