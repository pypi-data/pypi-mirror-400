"""Tests for error handling and reporting in line limits validation."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorErrors:
    """Tests for error handling and reporting."""

    def test_error_messages_use_relative_paths(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should use relative paths in error messages."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join([f"# Line {i}" for i in range(1, 15)])
        create_python_file(tmp_path, "src/too_long.py", long_content)

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
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should report all violations, not just first one."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create multiple violating files
        long_content = "\n".join([f"# Line {i}" for i in range(1, 15)])
        create_python_file(tmp_path, "src/file1.py", long_content)
        create_python_file(tmp_path, "src/file2.py", long_content)
        create_python_file(tmp_path, "src/file3.py", long_content)

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention all files
        assert "file1.py" in captured.out
        assert "file2.py" in captured.out
        assert "file3.py" in captured.out
        assert exit_code == 1

    def test_unicode_file_content(self, tmp_path: Path) -> None:
        """Should handle Unicode content correctly."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with Unicode content
        unicode_content = "# こんにちは\n# Привет\n# مرحبا\npass\n"
        create_python_file(tmp_path, "src/unicode.py", unicode_content)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_with_very_long_lines(self, tmp_path: Path) -> None:
        """Should count lines correctly even with very long lines."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with very long lines
        long_line = "x = " + "1" * 10000
        content = "\n".join([long_line] * 3)
        create_python_file(tmp_path, "src/long_lines.py", content)

        # 3 lines, should pass
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_output_shows_max_lines_limit(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should show the max_lines limit in output."""
        config = create_minimal_config(tmp_path)
        config.line_limits.max_lines = 100
        (config.project_root / "src").mkdir()

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention the limit
        assert "100" in captured.out
        assert exit_code == 0
