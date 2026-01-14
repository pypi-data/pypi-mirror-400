"""Tests for decorator handling in one-per-file validation."""


from collections.abc import Callable
from pathlib import Path

from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorDecorators:
    """Tests for decorator handling."""

    def test_file_with_decorators_counted_once(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should count decorated functions as single definition."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """@decorator
@another_decorator
def decorated():
    pass
"""
        python_file_factory("src/decorated.py", content, config.project_root)

        # Only one definition despite decorators
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_multiple_decorated_functions_fails(
        self, minimal_config: Config, python_file_factory: Callable[[str, str, Path | None], Path]
    ) -> None:
        """Should count each decorated function separately."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """@decorator1
def func1():
    pass

@decorator2
def func2():
    pass
"""
        python_file_factory("src/multi_decorated.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_output_format(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
        capsys: CaptureFixture[str],
    ) -> None:
        """Should produce clear output format."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Valid case
        python_file_factory("src/good.py", "def hello():\n    pass\n", config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should have clear success message
        assert "Checking" in captured.out or "one function/class per file" in captured.out
        assert exit_code == 0
