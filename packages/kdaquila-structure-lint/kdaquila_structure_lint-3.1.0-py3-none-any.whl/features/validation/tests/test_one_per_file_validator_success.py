"""Tests for one-per-file validation successes."""

from pathlib import Path

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorSuccess:
    """Tests for success cases in one-per-file validation."""

    def test_files_with_single_definition_pass(self, tmp_path: Path) -> None:
        """Should pass when files have single definition."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        # Create files with single definitions
        create_python_file(tmp_path, "src/func.py", "def hello():\n    pass\n")
        create_python_file(tmp_path, "src/cls.py", "class MyClass:\n    pass\n")

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_empty_file_passes(self, tmp_path: Path) -> None:
        """Should pass for empty files (0 definitions)."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        create_python_file(tmp_path, "src/empty.py", "")

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_only_imports_passes(self, tmp_path: Path) -> None:
        """Should pass for files with only imports (0 top-level definitions)."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        content = """import os
import sys
from pathlib import Path
from collections.abc import Callable
from features.config import Config
"""
        create_python_file(tmp_path, "src/imports.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_constants_and_function_passes(self, tmp_path: Path) -> None:
        """Should pass when file has constants plus one function (constants don't count)."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src").mkdir()

        content = """MAX_SIZE = 100
DEFAULT_NAME = "test"

def process():
    pass
"""
        create_python_file(tmp_path, "src/module.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0
