"""Tests for load_config with custom configurations."""

from pathlib import Path

from features.config import load_config


class TestLoadConfigCustom:
    """Tests for custom configuration loading."""

    def test_load_config_with_custom_validators(self, tmp_path: Path) -> None:
        """Should load custom validator toggles."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.validators]
structure = true
line_limits = false
one_per_file = false
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.validators.structure is True
        assert config.validators.line_limits is False
        assert config.validators.one_per_file is False

    def test_load_config_with_custom_line_limits(self, tmp_path: Path) -> None:
        """Should load custom line limits configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.line_limits]
max_lines = 100
search_paths = ["src", "lib", "app"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.line_limits.max_lines == 100
        assert config.line_limits.search_paths == ["src", "lib", "app"]

    def test_load_config_with_custom_one_per_file(self, tmp_path: Path) -> None:
        """Should load custom one-per-file configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.one_per_file]
search_paths = ["modules"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.one_per_file.search_paths == ["modules"]

    def test_load_config_with_custom_structure(self, tmp_path: Path) -> None:
        """Should load custom structure configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.structure]
strict_format_roots = ["lib", "app"]
folder_depth = 3
standard_folders = ["types", "helpers"]
general_folder = "common"
files_allowed_anywhere = ["README.md", "NOTES.md"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.structure.strict_format_roots == {"lib", "app"}
        assert config.structure.folder_depth == 3
        assert config.structure.standard_folders == {"types", "helpers"}
        assert config.structure.general_folder == "common"
        assert config.structure.files_allowed_anywhere == {"README.md", "NOTES.md"}

    def test_load_config_with_full_custom_config(self, tmp_path: Path) -> None:
        """Should load comprehensive custom configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
structure = true
line_limits = true
one_per_file = false

[tool.structure-lint.line_limits]
max_lines = 200
search_paths = ["src"]

[tool.structure-lint.one_per_file]
search_paths = ["src"]

[tool.structure-lint.structure]
strict_format_roots = ["source"]
folder_depth = 1
standard_folders = ["utils"]
general_folder = "shared"
files_allowed_anywhere = ["README.md"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        # Verify all settings
        assert config.enabled is True
        assert config.validators.structure is True
        assert config.validators.line_limits is True
        assert config.validators.one_per_file is False
        assert config.line_limits.max_lines == 200
        assert config.line_limits.search_paths == ["src"]
        assert config.one_per_file.search_paths == ["src"]
        assert config.structure.strict_format_roots == {"source"}
        assert config.structure.folder_depth == 1
        assert config.structure.standard_folders == {"utils"}
        assert config.structure.general_folder == "shared"
        assert config.structure.files_allowed_anywhere == {"README.md"}

    def test_load_structure_files_allowed_anywhere_and_ignored(
        self, tmp_path: Path
    ) -> None:
        """Should load files_allowed_anywhere and ignored_folders from TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.structure]
files_allowed_anywhere = ["__init__.py", "py.typed", "VERSION", "README.md"]
ignored_folders = ["__pycache__", ".venv", "build", "dist", ".egg-info"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.structure.files_allowed_anywhere == {
            "__init__.py",
            "py.typed",
            "VERSION",
            "README.md",
        }
        assert config.structure.ignored_folders == {
            "__pycache__",
            ".venv",
            "build",
            "dist",
            ".egg-info",
        }
