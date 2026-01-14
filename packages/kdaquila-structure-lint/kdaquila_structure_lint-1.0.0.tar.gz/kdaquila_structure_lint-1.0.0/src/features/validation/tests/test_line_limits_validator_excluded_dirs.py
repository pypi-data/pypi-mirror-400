"""Tests for excluded directories in line limits validation."""


from collections.abc import Callable
from pathlib import Path

from features.config import Config
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorExcludedDirs:
    """Tests for excluded directory handling."""

    def test_excludes_venv_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude .venv and venv directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src").mkdir()
        (config.project_root / "src" / ".venv").mkdir()
        (config.project_root / "src" / "venv").mkdir()

        # Create long files in excluded directories
        long_content = "\n".join([f"# Line {i}" for i in range(1, 100)])
        python_file_factory("src/.venv/lib.py", long_content, config.project_root)
        python_file_factory("src/venv/lib.py", long_content, config.project_root)

        # Should pass because excluded directories are ignored
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_excludes_pycache_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude __pycache__ directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src" / "__pycache__").mkdir(parents=True)

        # Create long file in __pycache__
        long_content = "\n".join([f"# Line {i}" for i in range(1, 100)])
        python_file_factory("src/__pycache__/module.py", long_content, config.project_root)

        # Should pass because __pycache__ is excluded
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_excludes_git_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude .git directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src" / ".git").mkdir(parents=True)

        # Create long file in .git
        long_content = "\n".join([f"# Line {i}" for i in range(1, 100)])
        python_file_factory("src/.git/hooks.py", long_content, config.project_root)

        # Should pass because .git is excluded
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_nested_directories(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should check files in nested directories."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src" / "sub" / "deep").mkdir(parents=True)

        # Create file in nested directory
        long_content = "\n".join([f"# Line {i}" for i in range(1, 10)])
        python_file_factory("src/sub/deep/module.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1
