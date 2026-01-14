"""Tests for custom structure configuration."""

from pathlib import Path

from features.test_fixtures import create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestStructureValidatorCustomConfig:
    """Tests for custom structure configuration."""

    def test_custom_src_root(self, tmp_path: Path) -> None:
        """Should use custom src_root."""
        config = create_minimal_config(tmp_path)
        config.structure.src_root = "lib"

        # Create structure with custom src_root
        lib = config.project_root / "lib"
        features = lib / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_free_form_roots_allowed(self, tmp_path: Path) -> None:
        """Should allow free-form structure in free_form_roots at project root."""
        config = create_minimal_config(tmp_path)
        config.structure.free_form_roots = {"experimental"}

        # Create valid src structure
        src = config.project_root / "src"
        src.mkdir()
        features = src / "features"
        features.mkdir()
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Free-form experimental directory at project root (anything goes, not validated)
        experimental = config.project_root / "experimental"
        experimental.mkdir()
        (experimental / "random_folder").mkdir()
        (experimental / "random_folder" / "nested").mkdir()
        (experimental / "random_file.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_custom_allowed_files(self, tmp_path: Path) -> None:
        """Should allow custom files like py.typed via allowed_files config."""
        config = create_minimal_config(tmp_path)
        config.structure.allowed_files = {"__init__.py", "py.typed"}

        # Create valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Add custom allowed file - should be allowed
        (features / "my_feature" / "py.typed").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_custom_ignored_folders(self, tmp_path: Path) -> None:
        """Should ignore custom folders like .venv, build via ignored_folders config."""
        config = create_minimal_config(tmp_path)
        config.structure.ignored_folders = {
            "__pycache__",
            ".venv",
            "build",
            ".egg-info",
        }

        # Create valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Add ignored directories - should be ignored
        (features / "my_feature" / ".venv").mkdir()
        (features / "my_feature" / ".venv" / "lib").mkdir()
        (features / "my_feature" / "build").mkdir()
        (features / "my_feature" / "build" / "output.txt").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0
