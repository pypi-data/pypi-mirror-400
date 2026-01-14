"""Tests for load_config path resolution and error handling."""

from pathlib import Path

import pytest
from _pytest.monkeypatch import MonkeyPatch

from features.config import load_config


class TestLoadConfigPaths:
    """Tests for path resolution and error handling."""

    def test_load_config_autodetect_project_root(
        self, tmp_path: Path, monkeypatch: MonkeyPatch
    ) -> None:
        """Should auto-detect project root when not specified."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.structure-lint]\nenabled = true")

        subdir = tmp_path / "src"
        subdir.mkdir()
        monkeypatch.chdir(subdir)

        config = load_config()

        assert config.project_root == tmp_path

    def test_load_config_with_config_path_sets_project_root(self, tmp_path: Path) -> None:
        """Should set project_root to config_path parent if not specified."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[tool.structure-lint]\nenabled = true")

        config = load_config(config_path=pyproject)

        assert config.project_root == tmp_path

    def test_load_config_invalid_toml(self, tmp_path: Path) -> None:
        """Should raise error for invalid TOML."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("""
[tool.structure-lint
# Missing closing bracket
enabled = true
""")

        # Should raise ValueError or similar due to TOML decode error
        with pytest.raises((ValueError, KeyError, AttributeError)):
            load_config(project_root=tmp_path, config_path=pyproject)
