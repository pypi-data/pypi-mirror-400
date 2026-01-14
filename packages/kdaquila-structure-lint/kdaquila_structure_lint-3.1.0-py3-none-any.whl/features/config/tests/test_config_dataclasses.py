"""Tests for config dataclass defaults."""

from features.config import (
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)


class TestConfigDataclasses:
    """Tests for config dataclass defaults."""

    def test_validator_toggles_defaults(self) -> None:
        """Should have correct default values."""
        toggles = ValidatorToggles()
        assert toggles.structure is False
        assert toggles.line_limits is True
        assert toggles.one_per_file is True

    def test_line_limits_config_defaults(self) -> None:
        """Should have correct default values."""
        config = LineLimitsConfig()
        assert config.max_lines == 150
        assert config.search_paths == ["src"]

    def test_one_per_file_config_defaults(self) -> None:
        """Should have correct default values."""
        config = OnePerFileConfig()
        assert config.search_paths == ["src"]

    def test_structure_config_defaults(self) -> None:
        """Should have correct default values."""
        config = StructureConfig()
        assert config.strict_format_roots == {"src"}
        assert config.folder_depth == 2
        assert config.standard_folders == {"types", "utils", "constants", "tests"}
        assert config.general_folder == "general"
        assert config.files_allowed_anywhere == {"__init__.py"}
        assert config.ignored_folders == {
            "__pycache__",
            ".mypy_cache",
            ".pytest_cache",
            ".ruff_cache",
            ".hypothesis",
            ".tox",
            ".coverage",
            "*.egg-info",
        }
