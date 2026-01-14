"""Integration tests for CLI path handling."""

from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from features.cli import main
from features.test_fixtures import create_python_file


class TestCLIIntegrationPaths:
    """Integration tests for CLI path handling."""

    def test_cli_no_arguments_autodetect(self, tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
        """Should auto-detect project root when no arguments provided."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        monkeypatch.chdir(tmp_path)
        exit_code = main([])
        assert exit_code == 0

    def test_cli_with_relative_paths(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Should handle relative paths correctly."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false
""")

        (tmp_path / "src").mkdir()
        create_python_file(tmp_path, "src/module.py", "def hello():\n    pass\n")

        monkeypatch.chdir(tmp_path)
        exit_code = main(["--project-root", "."])
        assert exit_code == 0

    def test_cli_empty_project_with_validators_enabled(self, tmp_path: Path) -> None:
        """Should handle empty project (no Python files) gracefully."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false
""")

        # Create empty src directory
        (tmp_path / "src").mkdir()

        exit_code = main(["--project-root", str(tmp_path)])
        # Should succeed (no violations in empty project)
        assert exit_code == 0
