"""Tests for nested functions and classes in one-per-file validation."""


from collections.abc import Callable
from pathlib import Path

from features.config import Config
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorNested:
    """Tests for nested functions and classes."""

    def test_nested_functions_not_counted(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should not count nested functions as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def outer():
    def inner():
        pass
    return inner
"""
        python_file_factory("src/nested.py", content, config.project_root)

        # Only one top-level definition (outer)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_nested_classes_not_counted(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should not count nested classes as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class Outer:
    class Inner:
        pass
"""
        python_file_factory("src/nested.py", content, config.project_root)

        # Only one top-level definition (Outer)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_class_methods_not_counted(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should not count class methods as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

    async def method3(self):
        pass
"""
        python_file_factory("src/class.py", content, config.project_root)

        # Only one top-level definition (MyClass)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0
