"""Tests for edge cases and special scenarios in structure validation."""


from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_structure import validate_structure


class TestStructureValidatorEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_pycache_ignored_in_src_root(self, minimal_config: Config) -> None:
        """Should ignore __pycache__ directories."""
        config = minimal_config

        # Create valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Add __pycache__ (should be ignored)
        (src / "__pycache__").mkdir()

        # Add valid content
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_multiple_structure_violations_all_reported(
        self, minimal_config: Config, capsys: CaptureFixture[str]
    ) -> None:
        """Should report all violations, not just first one."""
        config = minimal_config

        # Create structure with multiple issues
        src = config.project_root / "src"
        src.mkdir()
        # Base folders (automatically accepted)
        (src / "base1").mkdir()
        (src / "base2").mkdir()
        # Create files directly in root - these are not allowed
        (src / "file1.py").touch()
        (src / "file2.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Should report files not allowed in root
        assert "Files not allowed" in captured.out or "file1.py" in captured.out
        assert exit_code == 1

    def test_empty_src_directory_passes(self, minimal_config: Config) -> None:
        """Should pass when src directory is empty (no base folders yet)."""
        config = minimal_config

        # Create empty src directory
        (config.project_root / "src").mkdir()

        exit_code = validate_structure(config)
        # Empty src is valid - allows gradual project setup
        assert exit_code == 0

    def test_complex_valid_structure(self, minimal_config: Config) -> None:
        """Should pass with complex but valid structure."""
        config = minimal_config

        # Create complex valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Multiple features - use only standard folders (no general)
        for feature_name in ["auth", "users", "posts"]:
            feature_dir = features / feature_name
            feature_dir.mkdir()

            # Standard folders in each feature
            for folder in ["types", "utils"]:
                folder_dir = feature_dir / folder
                folder_dir.mkdir()
                (folder_dir / f"{feature_name}_{folder}.py").touch()

        # Scripts directory
        scripts = config.project_root / "scripts"
        scripts.mkdir()
        for script_folder in ["build", "test", "deploy"]:
            script_dir = scripts / script_folder
            script_dir.mkdir()
            (script_dir / "run.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0
