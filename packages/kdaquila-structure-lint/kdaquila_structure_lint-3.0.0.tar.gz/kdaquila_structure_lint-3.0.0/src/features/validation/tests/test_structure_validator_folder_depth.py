"""Tests for folder_depth configuration."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestFolderDepthVariations:
    """Tests for folder_depth configuration."""

    def test_folder_depth_0_requires_standard_at_base(self, tmp_path: Path) -> None:
        """With folder_depth=0, base folders must have standard folders only."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 0

        # Create structure: src/features/ must have standard folders only
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "types").mkdir()
        (features / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        # This should pass - base folder has standard folders
        assert exit_code == 0

    def test_folder_depth_0_rejects_nested_custom_folders(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """With folder_depth=0, nested custom folders inside first layer fail."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 0

        # Create structure with nested custom folder inside first custom layer
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        # nested_feature is a CUSTOM folder inside my_feature - should fail
        (features / "my_feature" / "nested_feature").mkdir()
        (features / "my_feature" / "nested_feature" / "types").mkdir()
        (features / "my_feature" / "nested_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Nested custom folder "nested_feature" exceeds depth 0
        assert exit_code == 1
        assert "Exceeds max depth" in captured.out

    def test_folder_depth_1_allows_one_custom_layer(self, tmp_path: Path) -> None:
        """With folder_depth=1, one layer of custom folders is allowed."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 1

        # Create structure: src/features/my_feature/types/
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_folder_depth_1_rejects_nested_custom(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """With folder_depth=1, nested custom folders should fail."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 1

        # Create structure with 2 layers of custom folders
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "domain").mkdir()
        (features / "domain" / "subdomain").mkdir()
        (features / "domain" / "subdomain" / "types").mkdir()
        (features / "domain" / "subdomain" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Exceeds max depth" in captured.out

    def test_folder_depth_2_allows_two_custom_layers(self, tmp_path: Path) -> None:
        """With folder_depth=2 (default), two layers of custom folders allowed."""
        config = create_minimal_config(tmp_path)
        # Default is 2, but let's be explicit
        config.structure.folder_depth = 2

        # Create structure with 2 layers of custom folders
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "domain").mkdir()
        (features / "domain" / "subdomain").mkdir()
        (features / "domain" / "subdomain" / "types").mkdir()
        (features / "domain" / "subdomain" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_folder_depth_3_allows_three_custom_layers(self, tmp_path: Path) -> None:
        """With folder_depth=3, three layers of custom folders allowed."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 3

        # Create structure with 3 layers of custom folders
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "level1").mkdir()
        (features / "level1" / "level2").mkdir()
        (features / "level1" / "level2" / "level3").mkdir()
        (features / "level1" / "level2" / "level3" / "types").mkdir()
        (features / "level1" / "level2" / "level3" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0
