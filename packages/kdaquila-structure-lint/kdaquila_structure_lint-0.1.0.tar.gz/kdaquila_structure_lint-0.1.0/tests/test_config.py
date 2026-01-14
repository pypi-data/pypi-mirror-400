"""Tests for configuration loading and validation."""

from pathlib import Path

import pytest

from structure_lint.config import (
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
    find_project_root,
    load_config,
)


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_find_pyproject_in_current_dir(self, tmp_path: Path):
        """Should find pyproject.toml in current directory."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        result = find_project_root(tmp_path)
        assert result == tmp_path

    def test_find_pyproject_in_parent_dir(self, tmp_path: Path):
        """Should find pyproject.toml in parent directory."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        subdir = tmp_path / "src" / "module"
        subdir.mkdir(parents=True)

        result = find_project_root(subdir)
        assert result == tmp_path

    def test_no_pyproject_returns_cwd(self, tmp_path: Path, monkeypatch):
        """Should return current directory if no pyproject.toml found."""
        # Create temp dir without pyproject.toml
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        monkeypatch.chdir(test_dir)
        result = find_project_root(test_dir)
        assert result == test_dir

    def test_default_start_path_uses_cwd(self, tmp_path: Path, monkeypatch):
        """Should use current directory as start_path if None provided."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        monkeypatch.chdir(tmp_path)
        result = find_project_root()
        assert result == tmp_path


class TestLoadConfig:
    """Tests for load_config function."""

    def test_load_config_with_all_defaults(self, tmp_path: Path):
        """Should use all default values when no config file exists."""
        config = load_config(project_root=tmp_path)

        assert config.enabled is True
        assert config.project_root == tmp_path
        assert config.validators.structure is False
        assert config.validators.line_limits is True
        assert config.validators.one_per_file is True
        assert config.line_limits.max_lines == 150
        assert config.line_limits.search_paths == ["src", "scripts"]
        assert config.one_per_file.search_paths == ["src", "scripts"]
        assert config.structure.src_root == "src"
        assert config.structure.src_base_folders == {"features"}
        assert config.structure.scripts_root == "scripts"
        assert config.structure.standard_folders == {"types", "utils", "constants", "tests"}
        assert config.structure.general_folder == "general"
        assert config.structure.free_form_bases == set()
        assert config.structure.allowed_files == {"README.md"}

    def test_load_config_with_minimal_toml(self, tmp_path: Path):
        """Should merge minimal config with defaults."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint]
enabled = false
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.enabled is False
        # All other values should be defaults
        assert config.validators.line_limits is True
        assert config.line_limits.max_lines == 150

    def test_load_config_with_custom_validators(self, tmp_path: Path):
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

    def test_load_config_with_custom_line_limits(self, tmp_path: Path):
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

    def test_load_config_with_custom_one_per_file(self, tmp_path: Path):
        """Should load custom one-per-file configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.one_per_file]
search_paths = ["modules"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.one_per_file.search_paths == ["modules"]

    def test_load_config_with_custom_structure(self, tmp_path: Path):
        """Should load custom structure configuration."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.structure]
src_root = "lib"
src_base_folders = ["apps", "features"]
scripts_root = "tools"
standard_folders = ["types", "helpers"]
general_folder = "common"
free_form_bases = ["experimental"]
allowed_files = ["README.md", "NOTES.md"]
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.structure.src_root == "lib"
        assert config.structure.src_base_folders == {"apps", "features"}
        assert config.structure.scripts_root == "tools"
        assert config.structure.standard_folders == {"types", "helpers"}
        assert config.structure.general_folder == "common"
        assert config.structure.free_form_bases == {"experimental"}
        assert config.structure.allowed_files == {"README.md", "NOTES.md"}

    def test_load_config_with_full_custom_config(self, tmp_path: Path):
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
src_root = "source"
src_base_folders = ["apps"]
scripts_root = "bin"
standard_folders = ["utils"]
general_folder = "shared"
free_form_bases = ["sandbox"]
allowed_files = ["README.md"]
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
        assert config.structure.src_root == "source"
        assert config.structure.src_base_folders == {"apps"}
        assert config.structure.scripts_root == "bin"
        assert config.structure.standard_folders == {"utils"}
        assert config.structure.general_folder == "shared"
        assert config.structure.free_form_bases == {"sandbox"}
        assert config.structure.allowed_files == {"README.md"}

    def test_load_config_partial_overrides(self, tmp_path: Path):
        """Should merge partial config with defaults."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint.line_limits]
max_lines = 80
# search_paths not specified, should use default
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        assert config.line_limits.max_lines == 80
        assert config.line_limits.search_paths == ["src", "scripts"]  # default

    def test_load_config_autodetect_project_root(self, tmp_path: Path, monkeypatch):
        """Should auto-detect project root when not specified."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.structure-lint]\nenabled = true")

        subdir = tmp_path / "src"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        config = load_config()

        assert config.project_root == tmp_path

    def test_load_config_with_config_path_sets_project_root(self, tmp_path: Path):
        """Should set project_root to config_path parent if not specified."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.structure-lint]\nenabled = true")

        config = load_config(config_path=pyproject)

        assert config.project_root == tmp_path

    def test_load_config_missing_tool_section(self, tmp_path: Path):
        """Should use defaults when [tool.structure-lint] section missing."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[project]
name = "test-project"
""")

        config = load_config(project_root=tmp_path, config_path=pyproject)

        # Should use all defaults
        assert config.enabled is True
        assert config.validators.line_limits is True
        assert config.line_limits.max_lines == 150

    def test_load_config_invalid_toml(self, tmp_path: Path):
        """Should raise error for invalid TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint
# Missing closing bracket
enabled = true
""")

        with pytest.raises(Exception):  # tomllib.TOMLDecodeError
            load_config(project_root=tmp_path, config_path=pyproject)

    def test_load_config_nonexistent_file_uses_defaults(self, tmp_path: Path):
        """Should use defaults when config file doesn't exist."""
        config = load_config(project_root=tmp_path)

        assert config.enabled is True
        assert config.project_root == tmp_path


class TestConfigDataclasses:
    """Tests for config dataclass defaults."""

    def test_validator_toggles_defaults(self):
        """Should have correct default values."""
        toggles = ValidatorToggles()
        assert toggles.structure is False
        assert toggles.line_limits is True
        assert toggles.one_per_file is True

    def test_line_limits_config_defaults(self):
        """Should have correct default values."""
        config = LineLimitsConfig()
        assert config.max_lines == 150
        assert config.search_paths == ["src", "scripts"]

    def test_one_per_file_config_defaults(self):
        """Should have correct default values."""
        config = OnePerFileConfig()
        assert config.search_paths == ["src", "scripts"]

    def test_structure_config_defaults(self):
        """Should have correct default values."""
        config = StructureConfig()
        assert config.src_root == "src"
        assert config.src_base_folders == {"features"}
        assert config.scripts_root == "scripts"
        assert config.standard_folders == {"types", "utils", "constants", "tests"}
        assert config.general_folder == "general"
        assert config.free_form_bases == set()
        assert config.allowed_files == {"README.md"}
