"""Basic tests for line limits validation."""


from collections.abc import Callable
from pathlib import Path

from features.config import Config
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorBasic:
    """Basic tests for validate_line_limits function."""

    def test_all_files_within_limit(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass when all files are within limit."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create files within limit
        python_file_factory("src/small1.py", "def hello():\n    pass\n", config.project_root)
        python_file_factory("src/small2.py", "# Comment\npass\n", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exceeds_limit(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when a file exceeds line limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join([f"# Line {i}" for i in range(1, 21)])
        python_file_factory("src/too_long.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_multiple_files_some_exceed_limit(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when some files exceed limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create mix of valid and invalid files
        python_file_factory("src/good.py", "def hello():\n    pass\n", config.project_root)
        long_content = "\n".join([f"# Line {i}" for i in range(1, 21)])
        python_file_factory("src/bad.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_empty_file_passes(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass for empty files."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        python_file_factory("src/empty.py", "", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exactly_at_limit_passes(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass when file is exactly at limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with exactly 10 lines
        content = "\n".join([f"# Line {i}" for i in range(1, 11)])
        python_file_factory("src/exact.py", content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_one_over_limit_fails(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when file is one line over limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with 11 lines
        content = "\n".join([f"# Line {i}" for i in range(1, 12)])
        python_file_factory("src/over.py", content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1
