"""Project root detection utilities."""

from pathlib import Path


def find_project_root(start_path: Path | None = None) -> Path:
    """Find project root by searching for pyproject.toml upward from start_path."""
    if start_path is None:
        start_path = Path.cwd()

    current = start_path.resolve()

    # Search upward until we find pyproject.toml or hit filesystem root
    while True:
        pyproject = current / "pyproject.toml"
        if pyproject.exists():
            return current

        parent = current.parent
        if parent == current:  # Reached filesystem root
            # No pyproject.toml found - use current directory
            return Path.cwd()

        current = parent
