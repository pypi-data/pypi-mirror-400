"""Tests for CLI exit codes."""

from collections.abc import Callable
from pathlib import Path

from features.cli import main


class TestCLIExitCodes:
    """Tests for CLI exit codes."""

    def test_cli_success_exit_code(
        self,
        tmp_path: Path,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
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

    def test_cli_validation_failure_exit_code(
        self,
        tmp_path: Path,
        python_file_factory: Callable[[str, str, Path | None], Path],
    ) -> None:
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
        long_content = "\n".join([f"# Line {i}" for i in range(1, 20)])
        python_file_factory("src/module.py", long_content, tmp_path)

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 1

    def test_cli_disabled_exit_code(self, tmp_path: Path) -> None:
        """Should return 0 when tool is disabled."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = false
""")

        exit_code = main(["--project-root", str(tmp_path)])
        assert exit_code == 0

    def test_cli_no_validators_enabled_exit_code(self, tmp_path: Path) -> None:
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

    def test_cli_invalid_toml_exit_code(self, tmp_path: Path) -> None:
        """Should return 2 for configuration errors."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint
# Invalid TOML - missing closing bracket
enabled = true
""")

        exit_code = main(["--config", str(pyproject)])
        assert exit_code == 2
