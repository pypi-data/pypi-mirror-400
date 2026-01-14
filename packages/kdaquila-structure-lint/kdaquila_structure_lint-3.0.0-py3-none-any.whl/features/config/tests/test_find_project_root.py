"""Tests for find_project_root function."""

from pathlib import Path

from _pytest.monkeypatch import MonkeyPatch

from features.config import find_project_root


class TestFindProjectRoot:
    """Tests for find_project_root function."""

    def test_find_pyproject_in_current_dir(self, tmp_path: Path) -> None:
        """Should find pyproject.toml in current directory."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        result = find_project_root(tmp_path)
        assert result == tmp_path

    def test_find_pyproject_in_parent_dir(self, tmp_path: Path) -> None:
        """Should find pyproject.toml in parent directory."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        subdir = tmp_path / "src" / "module"
        subdir.mkdir(parents=True)

        result = find_project_root(subdir)
        assert result == tmp_path

    def test_no_pyproject_returns_cwd(self, tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
        """Should return current directory if no pyproject.toml found."""
        # Create temp dir without pyproject.toml
        test_dir = tmp_path / "test"
        test_dir.mkdir()

        monkeypatch.chdir(test_dir)
        result = find_project_root(test_dir)
        assert result == test_dir

    def test_default_start_path_uses_cwd(self, tmp_path: Path, monkeypatch: MonkeyPatch) -> None:
        """Should use current directory as start_path if None provided."""
        pyproject = tmp_path / "pyproject.toml"
        pyproject.write_text("[project]\nname = 'test'")

        monkeypatch.chdir(tmp_path)
        result = find_project_root()
        assert result == tmp_path
