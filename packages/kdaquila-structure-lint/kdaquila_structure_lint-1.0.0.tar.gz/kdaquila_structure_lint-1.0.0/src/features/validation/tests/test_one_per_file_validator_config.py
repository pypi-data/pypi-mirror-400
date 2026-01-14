"""Tests for configuration and path handling in one-per-file validation."""


from collections.abc import Callable
from pathlib import Path

from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorConfig:
    """Tests for configuration and path handling."""

    def test_custom_search_paths(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should check custom search paths."""
        config = minimal_config
        config.one_per_file.search_paths = ["lib", "app"]

        (config.project_root / "lib").mkdir()
        (config.project_root / "app").mkdir()

        # Create violating file in lib
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("lib/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_missing_search_path(self, minimal_config: Config, capsys: CaptureFixture[str]) -> None:
        """Should warn about missing search paths and continue."""
        config = minimal_config
        config.one_per_file.search_paths = ["nonexistent", "src"]

        # Create valid file in src
        (config.project_root / "src").mkdir()
        (config.project_root / "src" / "module.py").write_text("def hello():\n    pass\n")

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should warn about nonexistent
        assert "Warning" in captured.out or "not found" in captured.out
        # Should still succeed
        assert exit_code == 0

    def test_all_search_paths_missing(
        self, minimal_config: Config, capsys: CaptureFixture[str]
    ) -> None:
        """Should handle all search paths missing gracefully."""
        config = minimal_config
        config.one_per_file.search_paths = ["nonexistent1", "nonexistent2"]

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should warn
        assert "Warning" in captured.out or "not found" in captured.out
        # Should succeed (no files to check)
        assert exit_code == 0

    def test_nested_directories(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should check files in nested directories."""
        config = minimal_config
        (config.project_root / "src" / "sub" / "deep").mkdir(parents=True)

        # Create violating file in nested directory
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/sub/deep/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_excludes_venv_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude .venv and venv directories."""
        config = minimal_config

        (config.project_root / "src").mkdir()
        (config.project_root / "src" / ".venv").mkdir()
        (config.project_root / "src" / "venv").mkdir()

        # Create violating files in excluded directories
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/.venv/lib.py", content, config.project_root)
        python_file_factory("src/venv/lib.py", content, config.project_root)

        # Should pass because excluded directories are ignored
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_pycache_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude __pycache__ directories."""
        config = minimal_config

        (config.project_root / "src" / "__pycache__").mkdir(parents=True)

        # Create violating file in __pycache__
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/__pycache__/module.py", content, config.project_root)

        # Should pass because __pycache__ is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_git_directory(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should exclude .git directories."""
        config = minimal_config

        (config.project_root / "src" / ".git").mkdir(parents=True)

        # Create violating file in .git
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/.git/hooks.py", content, config.project_root)

        # Should pass because .git is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0
