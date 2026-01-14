"""Tests for configuration and path handling in line limits validation."""


from collections.abc import Callable
from pathlib import Path

from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_line_limits import validate_line_limits


class TestLineLimitsValidatorConfigPaths:
    """Tests for configuration and path handling."""

    def test_custom_search_paths(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should check custom search paths."""
        config = minimal_config
        config.line_limits.search_paths = ["lib", "app"]
        config.line_limits.max_lines = 5

        (config.project_root / "lib").mkdir()
        (config.project_root / "app").mkdir()

        # Create file in lib
        long_content = "\n".join([f"# Line {i}" for i in range(1, 10)])
        python_file_factory("lib/module.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_missing_search_path(
        self, minimal_config: Config, capsys: CaptureFixture[str]
    ) -> None:
        """Should warn about missing search paths and continue."""
        config = minimal_config
        config.line_limits.search_paths = ["nonexistent", "src"]

        # Create valid file in src
        (config.project_root / "src").mkdir()
        (config.project_root / "src" / "module.py").write_text("pass\n")

        exit_code = validate_line_limits(config)
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
        config.line_limits.search_paths = ["nonexistent1", "nonexistent2"]

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should warn
        assert "Warning" in captured.out or "not found" in captured.out
        # Should succeed (no files to check)
        assert exit_code == 0

    def test_max_lines_configuration_respected(
        self,
        minimal_config: Config,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
        """Should respect configured max_lines value."""
        config = minimal_config
        config.line_limits.max_lines = 3
        (config.project_root / "src").mkdir()

        # Create file with 4 lines
        python_file_factory("src/module.py", "line1\nline2\nline3\nline4\n", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1
