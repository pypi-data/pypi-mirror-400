"""Tests for basic structure validation functionality."""

from pathlib import Path

from _pytest.capture import CaptureFixture

from features.test_fixtures import create_minimal_config
from features.validation.utils.validator_structure import validate_structure


class TestStructureValidatorBasic:
    """Basic tests for validate_structure function."""

    def test_missing_src_root_fails(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should fail when src root doesn't exist."""
        config = create_minimal_config(tmp_path)

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert "not found" in captured.out or "Error" in captured.out
        assert exit_code == 1

    def test_valid_minimal_structure_passes(self, tmp_path: Path) -> None:
        """Should pass with valid minimal structure."""
        config = create_minimal_config(tmp_path)

        # Create minimal valid structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Create a valid folder in features
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_files_in_src_root_fails(self, tmp_path: Path) -> None:
        """Should fail when files exist in src root."""
        config = create_minimal_config(tmp_path)

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Add file in src root (not allowed)
        (src / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 1

    def test_files_in_base_folder_fails(
        self, tmp_path: Path, capsys: CaptureFixture[str]
    ) -> None:
        """Should fail when files exist directly in base folders like features/."""
        config = create_minimal_config(tmp_path)

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Add files directly in features/ (not allowed)
        (features / "calculator.py").touch()
        (features / "validator.py").touch()
        (features / "process_data.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert exit_code == 1
        assert "Files not allowed in root" in captured.out
        assert "calculator.py" in captured.out

    def test_multiple_base_folders_accepted(self, tmp_path: Path) -> None:
        """Any base folders in src/ should be accepted automatically."""
        config = create_minimal_config(tmp_path)

        # Create multiple base folders
        src = config.project_root / "src"
        (src / "features").mkdir(parents=True)
        (src / "features" / "__init__.py").touch()
        (src / "apps").mkdir(parents=True)
        (src / "apps" / "__init__.py").touch()
        (src / "libs").mkdir(parents=True)
        (src / "libs" / "__init__.py").touch()

        exit_code = validate_structure(config)

        # Should pass - all base folders automatically accepted
        assert exit_code == 0
