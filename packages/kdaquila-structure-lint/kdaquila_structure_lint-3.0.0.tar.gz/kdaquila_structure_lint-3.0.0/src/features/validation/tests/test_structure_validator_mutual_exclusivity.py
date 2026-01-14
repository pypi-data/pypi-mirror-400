"""Tests for mutual exclusivity rules at folder levels."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestMutualExclusivity:
    """Tests for mutual exclusivity rules at folder levels."""

    def test_standard_and_custom_at_same_level_fails(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Cannot mix standard folders with custom folders at same level."""
        config = create_minimal_config(tmp_path)

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        # Mix standard folder (types) with custom folder (custom_thing)
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()
        (features / "my_feature" / "custom_thing").mkdir()
        (features / "my_feature" / "custom_thing" / "types").mkdir()
        (features / "my_feature" / "custom_thing" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Cannot mix standard and custom folders" in captured.out

    def test_standard_and_general_at_same_level_fails(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Cannot mix standard folders with general folder at same level."""
        config = create_minimal_config(tmp_path)

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        # Mix standard folder (types) with general folder at same level
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()
        (features / "my_feature" / "general").mkdir()
        (features / "my_feature" / "general" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Cannot mix general and standard folders" in captured.out

    def test_general_folder_requires_custom_sibling(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """General folder requires at least one custom subfolder as sibling."""
        config = create_minimal_config(tmp_path)

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        # Only general folder, no custom siblings
        (features / "my_feature" / "general").mkdir()
        (features / "my_feature" / "general" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "general requires at least one custom subfolder" in captured.out
