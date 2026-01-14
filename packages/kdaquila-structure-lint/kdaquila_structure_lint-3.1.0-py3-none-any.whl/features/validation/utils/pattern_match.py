"""Pattern matching utilities for validation."""

import fnmatch


def matches_any_pattern(name: str, patterns: set[str]) -> bool:
    """Check if name matches any pattern (supports wildcards)."""
    return any(fnmatch.fnmatch(name, pattern) for pattern in patterns)
