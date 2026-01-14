"""Tests for decorator handling in one-per-file validation."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorDecorators:
    """Tests for decorator handling."""

    def test_file_with_decorators_counted_once(self, tmp_path: Path) -> None:
        """Should count decorated functions as single definition."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        content = """@decorator
@another_decorator
def decorated():
    pass
"""
        create_python_file(tmp_path, "src/decorated.py", content)

        # Only one definition despite decorators
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_multiple_decorated_functions_fails(
        self, tmp_path: Path
    ) -> None:
        """Should count each decorated function separately."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        content = """@decorator1
def func1():
    pass

@decorator2
def func2():
    pass
"""
        create_python_file(tmp_path, "src/multi_decorated.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_output_format(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should produce clear output format."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Valid case
        create_python_file(tmp_path, "src/good.py", "def hello():\n    pass\n")

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should have clear success message
        assert "Checking" in captured.out or "one function/class per file" in captured.out
        assert exit_code == 0
