"""Tests for one-per-file validation failures."""

from collections.abc import Callable
from pathlib import Path

from features.config import Config
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorFailures:
    """Tests for failure cases in one-per-file validation."""

    def test_file_with_multiple_functions_fails(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when file has multiple functions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def func1():
    pass

def func2():
    pass
"""
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_file_with_multiple_classes_fails(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when file has multiple classes."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class Class1:
    pass

class Class2:
    pass
"""
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_file_with_function_and_class_fails(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should fail when file has both function and class."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def my_func():
    pass

class MyClass:
    pass
"""
        python_file_factory("src/mixed.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_async_function_counted(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should count async functions as definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """async def async_func():
    pass

def sync_func():
    pass
"""
        python_file_factory("src/async.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1
