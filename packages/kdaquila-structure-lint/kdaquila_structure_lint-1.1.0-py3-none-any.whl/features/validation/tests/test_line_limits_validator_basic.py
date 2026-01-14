"""Basic tests for line limits validation."""

from pathlib import Path

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorBasic:
    """Basic tests for validate_line_limits function."""

    def test_all_files_within_limit(self, tmp_path: Path) -> None:
        """Should pass when all files are within limit."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Create files within limit
        create_python_file(tmp_path, "src/small1.py", "def hello():\n    pass\n")
        create_python_file(tmp_path, "src/small2.py", "# Comment\npass\n")

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exceeds_limit(self, tmp_path: Path) -> None:
        """Should fail when a file exceeds line limit."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join([f"# Line {i}" for i in range(1, 21)])
        create_python_file(tmp_path, "src/too_long.py", long_content)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_multiple_files_some_exceed_limit(self, tmp_path: Path) -> None:
        """Should fail when some files exceed limit."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create mix of valid and invalid files
        create_python_file(tmp_path, "src/good.py", "def hello():\n    pass\n")
        long_content = "\n".join([f"# Line {i}" for i in range(1, 21)])
        create_python_file(tmp_path, "src/bad.py", long_content)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_empty_file_passes(self, tmp_path: Path) -> None:
        """Should pass for empty files."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        create_python_file(tmp_path, "src/empty.py", "")

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exactly_at_limit_passes(self, tmp_path: Path) -> None:
        """Should pass when file is exactly at limit."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with exactly 10 lines
        content = "\n".join([f"# Line {i}" for i in range(1, 11)])
        create_python_file(tmp_path, "src/exact.py", content)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_one_over_limit_fails(self, tmp_path: Path) -> None:
        """Should fail when file is one line over limit."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with 11 lines
        content = "\n".join([f"# Line {i}" for i in range(1, 12)])
        create_python_file(tmp_path, "src/over.py", content)

        exit_code = validate_line_limits(config)
        assert exit_code == 1
