"""Structure validation configuration."""

from dataclasses import dataclass, field


@dataclass
class StructureConfig:
    """Configuration for structure validator."""
    src_root: str = "src"
    src_base_folders: set[str] = field(default_factory=lambda: {"features"})
    scripts_root: str = "scripts"
    standard_folders: set[str] = field(default_factory=lambda: {"types", "utils", "constants", "tests"})
    general_folder: str = "general"
    free_form_bases: set[str] = field(default_factory=set)
    allowed_files: set[str] = field(default_factory=lambda: {"README.md"})
