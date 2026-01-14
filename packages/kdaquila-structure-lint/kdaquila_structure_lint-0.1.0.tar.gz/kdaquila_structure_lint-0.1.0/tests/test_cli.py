"""Tests for CLI argument parsing and exit codes."""

from pathlib import Path

import pytest

from structure_lint.cli import main


class TestCLIArgumentParsing:
    """Tests for command-line argument parsing."""

    def test_cli_help_flag(self):
        """Should display help and exit with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--help"])
        assert exc_info.value.code == 0

    def test_cli_version_flag(self):
        """Should display version and exit with code 0."""
        with pytest.raises(SystemExit) as exc_info:
            main(["--version"])
        assert exc_info.value.code == 0

    def test_cli_project_root_argument(self, tmp_path: Path):
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

    def test_cli_config_argument(self, tmp_path: Path):
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

    def test_cli_verbose_flag(self, tmp_path: Path, capsys):
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

    def test_cli_verbose_short_flag(self, tmp_path: Path):
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


class TestCLIExitCodes:
    """Tests for CLI exit codes."""

    def test_cli_success_exit_code(self, tmp_path: Path, python_file_factory):
        """Should return 0 when all validations pass."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false
""")

        # Create valid Python files
        (tmp_path / "src").mkdir()
        python_file_factory(
            "src/module.py",
            "def hello():\n    return 'world'\n",
            tmp_path
        )

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_validation_failure_exit_code(self, tmp_path: Path, python_file_factory):
        """Should return 1 when validation fails."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false

[tool.structure-lint.line_limits]
max_lines = 5
""")

        # Create file that violates line limit
        (tmp_path / "src").mkdir()
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 20)])
        python_file_factory("src/module.py", long_content, tmp_path)

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 1

    def test_cli_disabled_exit_code(self, tmp_path: Path):
        """Should return 0 when tool is disabled."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = false
""")

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_no_validators_enabled_exit_code(self, tmp_path: Path):
        """Should return 0 when no validators are enabled."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
""")

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_invalid_toml_exit_code(self, tmp_path: Path):
        """Should return 2 for configuration errors."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint
# Invalid TOML - missing closing bracket
enabled = true
""")

        exit_code = main(["--config", str(pyproject)])
        assert exit_code == 2


class TestCLIIntegration:
    """Integration tests for CLI with various scenarios."""

    def test_cli_with_multiple_validators_all_pass(self, tmp_path: Path, python_file_factory):
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
        python_file_factory("src/module.py", "def hello():\n    pass\n", tmp_path)

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_with_multiple_validators_one_fails(self, tmp_path: Path, python_file_factory):
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
        python_file_factory(
            "src/module.py",
            "def func1():\n    pass\n\ndef func2():\n    pass\n",
            tmp_path
        )

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 1

    def test_cli_with_missing_search_paths(self, tmp_path: Path, capsys):
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

    def test_cli_no_arguments_autodetect(self, tmp_path: Path, monkeypatch):
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

    def test_cli_with_relative_paths(self, tmp_path: Path, monkeypatch, python_file_factory):
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
        python_file_factory("src/module.py", "def hello():\n    pass\n", tmp_path)

        monkeypatch.chdir(tmp_path)
        exit_code = main(["--project-root", "."])
        assert exit_code == 0

    def test_cli_empty_project_with_validators_enabled(self, tmp_path: Path, capsys):
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

    def test_cli_output_messages(self, tmp_path: Path, python_file_factory, capsys):
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
        python_file_factory("src/good.py", "def hello():\n    pass\n", tmp_path)

        exit_code = main(["--project-root", str(tmp_path)])
        captured = capsys.readouterr()

        # Should show progress and results
        assert "Running line limit validation" in captured.out
        assert "All validations passed" in captured.out or "All Python files are within" in captured.out
        assert exit_code == 0
