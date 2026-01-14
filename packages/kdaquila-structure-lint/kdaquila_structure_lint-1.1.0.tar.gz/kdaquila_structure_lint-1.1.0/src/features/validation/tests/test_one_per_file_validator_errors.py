"""Tests for error handling and reporting in one-per-file validation."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorErrors:
    """Tests for error handling and reporting."""

    def test_syntax_error_reported_as_failure(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should report files with syntax errors."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Create file with syntax error
        content = "def broken(\n    # Missing closing paren\n"
        create_python_file(tmp_path, "src/broken.py", content)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should report error
        assert "Error parsing file" in captured.out or "broken.py" in captured.out
        assert exit_code == 1

    def test_error_messages_use_relative_paths(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should use relative paths in error messages."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Create violating file
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/multi.py", content)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Error message should use relative path
        assert (
            "src" in captured.out
            or "src\\multi.py" in captured.out
            or "src/multi.py" in captured.out
        )
        assert exit_code == 1

    def test_multiple_violations_all_reported(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should report all violations, not just first one."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Create multiple violating files
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/file1.py", content)
        create_python_file(tmp_path, "src/file2.py", content)
        create_python_file(tmp_path, "src/file3.py", content)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should mention all files
        assert "file1.py" in captured.out
        assert "file2.py" in captured.out
        assert "file3.py" in captured.out
        assert exit_code == 1

    def test_error_message_shows_definition_names(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should show names of definitions in error message."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        content = """def hello():
    pass

def world():
    pass

class Greeting:
    pass
"""
        create_python_file(tmp_path, "src/multi.py", content)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should mention definition names
        assert "hello" in captured.out
        assert "world" in captured.out
        assert "Greeting" in captured.out
        assert exit_code == 1

    def test_unicode_in_definition_names(self, tmp_path: Path) -> None:
        """Should handle Unicode in definition names."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Python allows Unicode identifiers
        content = """def функция():
    pass

def 函数():
    pass
"""
        create_python_file(tmp_path, "src/unicode.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1
