"""One-per-file configuration."""

from dataclasses import dataclass, field


@dataclass
class OnePerFileConfig:
    """Configuration for one-per-file validator."""
    search_paths: list[str] = field(default_factory=lambda: ["src"])
