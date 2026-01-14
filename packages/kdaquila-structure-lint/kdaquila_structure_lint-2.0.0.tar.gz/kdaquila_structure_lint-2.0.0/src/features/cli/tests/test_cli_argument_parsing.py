"""Tests for command-line argument parsing."""

from pathlib import Path

import pytest
from _pytest.capture import CaptureFixture

from features.cli import main


class TestCLIArgumentParsing:
    """Tests for command-line argument parsing."""

    def test_cli_help_flag(self) -> None:
        """Should display help and exit with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_cli_version_flag(self) -> None:
        """Should display version and exit with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_cli_project_root_argument(self, tmp_path: Path) -> None:
        """Should accept --project-root argument."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        # Create empty src to avoid warnings
        (tmp_path / "src").mkdir()

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_config_argument(self, tmp_path: Path) -> None:
        """Should accept --config argument."""
        pyproject = tmp_path / "custom.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        exit_code = main(["--config", str(pyproject)])
        assert exit_code == 0

    def test_cli_verbose_flag(self, tmp_path: Path, capsys: CaptureFixture[str]) -> None:
        """Should accept --verbose flag."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        exit_code = main(["--project-root", str(tmp_path), "--verbose"])
        captured = capsys.readouterr()

        assert exit_code == 0
        # Verbose should show project root
        assert "Project root:" in captured.out or "Warning" in captured.out

    def test_cli_verbose_short_flag(self, tmp_path: Path) -> None:
        """Should accept -v short flag for verbose."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        exit_code = main(["--project-root", str(tmp_path), "-v"])
        assert exit_code == 0
