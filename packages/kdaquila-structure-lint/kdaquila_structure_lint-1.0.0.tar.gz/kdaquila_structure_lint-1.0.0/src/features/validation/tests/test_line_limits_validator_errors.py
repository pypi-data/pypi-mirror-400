"""Tests for error handling and reporting in line limits validation."""


from collections.abc import Callable
from pathlib import Path

from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorErrors:
    """Tests for error handling and reporting."""

    def test_error_messages_use_relative_paths(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
        capsys: CaptureFixture[str],
    ) -> None:
        """Should use relative paths in error messages."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join([f"# Line {i}" for i in range(1, 15)])
        python_file_factory("src/too_long.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Error message should use relative path
        assert (
            "src" in captured.out
            or "src\\too_long.py" in captured.out
            or "src/too_long.py" in captured.out
        )
        # Should not contain absolute path markers
        assert exit_code == 1

    def test_multiple_violations_all_reported(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
        capsys: CaptureFixture[str],
    ) -> None:
        """Should report all violations, not just first one."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create multiple violating files
        long_content = "\n".join([f"# Line {i}" for i in range(1, 15)])
        python_file_factory("src/file1.py", long_content, config.project_root)
        python_file_factory("src/file2.py", long_content, config.project_root)
        python_file_factory("src/file3.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention all files
        assert "file1.py" in captured.out
        assert "file2.py" in captured.out
        assert "file3.py" in captured.out
        assert exit_code == 1

    def test_unicode_file_content(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should handle Unicode content correctly."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with Unicode content
        unicode_content = "# こんにちは\n# Привет\n# مرحبا\npass\n"
        python_file_factory("src/unicode.py", unicode_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_with_very_long_lines(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should count lines correctly even with very long lines."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with very long lines
        long_line = "x = " + "1" * 10000
        content = "\n".join([long_line] * 3)
        python_file_factory("src/long_lines.py", content, config.project_root)

        # 3 lines, should pass
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_output_shows_max_lines_limit(
        self, minimal_config: Config, capsys: CaptureFixture[str]
    ) -> None:
        """Should show the max_lines limit in output."""
        config = minimal_config
        config.line_limits.max_lines = 100
        (config.project_root / "src").mkdir()

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention the limit
        assert "100" in captured.out
        assert exit_code == 0
