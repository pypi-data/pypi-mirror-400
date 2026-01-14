"""Tests for general folder respecting depth limits."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestGeneralFolderDepthLimit:
    """Tests for general folder respecting depth limits."""

    def test_general_folder_at_max_depth_rejected(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """General folder at max depth should be rejected."""
        config = create_minimal_config(tmp_path)
        config.structure.folder_depth = 1

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        # At depth=1, my_feature is the max custom layer
        # Adding general here would exceed depth
        (features / "my_feature" / "general").mkdir()
        (features / "my_feature" / "general" / "module.py").touch()
        # Also need a custom sibling for general to be valid
        (features / "my_feature" / "subfolder").mkdir()
        (features / "my_feature" / "subfolder" / "types").mkdir()
        (features / "my_feature" / "subfolder" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        # The subfolder exceeds depth too
        assert "Exceeds max depth" in captured.out
