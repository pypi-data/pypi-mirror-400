"""Tests for one-per-file validation successes."""

from collections.abc import Callable
from pathlib import Path

from features.config import Config
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorSuccess:
    """Tests for success cases in one-per-file validation."""

    def test_files_with_single_definition_pass(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass when files have single definition."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create files with single definitions
        python_file_factory("src/func.py", "def hello():\n    pass\n", config.project_root)
        python_file_factory("src/cls.py", "class MyClass:\n    pass\n", config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_empty_file_passes(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass for empty files (0 definitions)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        python_file_factory("src/empty.py", "", config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_only_imports_passes(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass for files with only imports (0 top-level definitions)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """import os
import sys
from pathlib import Path
from collections.abc import Callable
from features.config import Config
"""
        python_file_factory("src/imports.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_constants_and_function_passes(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should pass when file has constants plus one function (constants don't count)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """MAX_SIZE = 100
DEFAULT_NAME = "test"

def process():
    pass
"""
        python_file_factory("src/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0
