"""Integration tests for structure validation combining multiple aspects."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_custom_config, create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestStructureValidatorIntegration:
    """Integration tests combining multiple aspects."""

    def test_full_custom_config_valid_structure(self, tmp_path: Path) -> None:
        """Should validate with fully custom configuration."""
        config = create_custom_config(tmp_path)

        # Create structure matching custom config
        lib = config.project_root / "lib"
        lib.mkdir()

        # Custom base folders: apps, features
        for base in ["apps", "features"]:
            base_dir = lib / base
            base_dir.mkdir()

            # Create a module in each - use only standard folders (no common/general)
            module_dir = base_dir / f"my_{base}"
            module_dir.mkdir()

            # Custom standard folders: types, utils, helpers
            for folder in ["types", "utils", "helpers"]:
                folder_dir = module_dir / folder
                folder_dir.mkdir()
                (folder_dir / "module.py").touch()

        # Custom scripts root: tools
        tools = config.project_root / "tools"
        tools.mkdir()
        (tools / "build").mkdir()
        (tools / "build" / "script.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_structure_validation_output_format(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should produce clear output format."""
        config = create_minimal_config(tmp_path)

        # Create valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Should have clear progress messages
        assert "Validating" in captured.out or "src" in captured.out
        assert "valid" in captured.out.lower() or "passed" in captured.out.lower()
        assert exit_code == 0
