"""Tests for configuration and path handling in one-per-file validation."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config, create_python_file
from features.validation.utils.validator_one_per_file import validate_one_per_file


class TestOnePerFileValidatorConfig:
    """Tests for configuration and path handling."""

    def test_custom_search_paths(self, tmp_path: Path) -> None:
        """Should check custom search paths."""
        config = create_minimal_config(tmp_path)
        config.one_per_file.search_paths = ["lib", "app"]

        (config.project_root / "lib").mkdir()
        (config.project_root / "app").mkdir()

        # Create violating file in lib
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "lib/module.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_missing_search_path(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should warn about missing search paths and continue."""
        config = create_minimal_config(tmp_path)
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
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should handle all search paths missing gracefully."""
        config = create_minimal_config(tmp_path)
        config.one_per_file.search_paths = ["nonexistent1", "nonexistent2"]

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should warn
        assert "Warning" in captured.out or "not found" in captured.out
        # Should succeed (no files to check)
        assert exit_code == 0

    def test_nested_directories(self, tmp_path: Path) -> None:
        """Should check files in nested directories."""
        config = create_minimal_config(tmp_path)
        (config.project_root / "src" / "sub" / "deep").mkdir(parents=True)

        # Create violating file in nested directory
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/sub/deep/module.py", content)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_excludes_venv_directory(self, tmp_path: Path) -> None:
        """Should exclude .venv and venv directories."""
        config = create_minimal_config(tmp_path)

        (config.project_root / "src").mkdir()
        (config.project_root / "src" / ".venv").mkdir()
        (config.project_root / "src" / "venv").mkdir()

        # Create violating files in excluded directories
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/.venv/lib.py", content)
        create_python_file(tmp_path, "src/venv/lib.py", content)

        # Should pass because excluded directories are ignored
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_pycache_directory(self, tmp_path: Path) -> None:
        """Should exclude __pycache__ directories."""
        config = create_minimal_config(tmp_path)

        (config.project_root / "src" / "__pycache__").mkdir(parents=True)

        # Create violating file in __pycache__
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/__pycache__/module.py", content)

        # Should pass because __pycache__ is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_git_directory(self, tmp_path: Path) -> None:
        """Should exclude .git directories."""
        config = create_minimal_config(tmp_path)

        (config.project_root / "src" / ".git").mkdir(parents=True)

        # Create violating file in .git
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        create_python_file(tmp_path, "src/.git/hooks.py", content)

        # Should pass because .git is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0
