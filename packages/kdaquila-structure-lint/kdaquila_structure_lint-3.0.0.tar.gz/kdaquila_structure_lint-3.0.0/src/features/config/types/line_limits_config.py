"""Line limits configuration."""

from dataclasses import dataclass, field


@dataclass
class LineLimitsConfig:
    """Configuration for line limits validator."""
    max_lines: int = 150
    search_paths: list[str] = field(default_factory=lambda: ["src"])
