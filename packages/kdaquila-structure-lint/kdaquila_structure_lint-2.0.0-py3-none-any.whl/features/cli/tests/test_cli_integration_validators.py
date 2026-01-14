"""Integration tests for CLI with multiple validators."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.cli import main
from features.test_fixtures import create_python_file


class TestCLIIntegrationValidators:
    """Integration tests for CLI with multiple validators."""

    def test_cli_with_multiple_validators_all_pass(self, tmp_path: Path) -> None:
        """Should pass when multiple validators all succeed."""
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

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_with_multiple_validators_one_fails(self, tmp_path: Path) -> None:
        """Should fail when any validator fails."""
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
        # Valid for line limits, invalid for one-per-file
        create_python_file(
            tmp_path, "src/module.py", "def func1():\n    pass\n\ndef func2():\n    pass\n"
        )

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 1

    def test_cli_with_missing_search_paths(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should handle missing search paths gracefully."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false

[tool.structure-lint.line_limits]
search_paths = ["nonexistent"]
""")

        exit_code = main(["--project-root", str(tmp_path)])
        captured = capsys.readouterr()

        # Should warn about missing paths
        assert "Warning" in captured.out or "not found" in captured.out
        # Should still succeed (no violations found)
        assert exit_code == 0

    def test_cli_output_messages(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should produce helpful output messages."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = false
structure = false
""")

        (tmp_path / "src").mkdir()
        create_python_file(tmp_path, "src/good.py", "def hello():\n    pass\n")

        exit_code = main(["--project-root", str(tmp_path)])
        captured = capsys.readouterr()

        # Should show progress and results
        assert "Running line limit validation" in captured.out
        assert (
            "All validations passed" in captured.out
            or "All Python files are within" in captured.out
        )
        assert exit_code == 0
