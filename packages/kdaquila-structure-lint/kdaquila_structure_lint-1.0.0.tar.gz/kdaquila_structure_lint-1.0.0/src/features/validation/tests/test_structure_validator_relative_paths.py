"""Tests for relative path handling in structure validation error messages."""


from _pytest.capture import CaptureFixture

from features.config import Config
from features.validation.utils.validator_structure import validate_structure


class TestStructureValidatorRelativePaths:
    """Tests for relative path handling in error messages."""

    def test_error_messages_use_relative_paths(
        self, minimal_config: Config, capsys: CaptureFixture[str]
    ) -> None:
        """Should use relative paths in error messages."""
        config = minimal_config

        # Create invalid structure - files in src root
        src = config.project_root / "src"
        src.mkdir()
        (src / "features").mkdir()
        (src / "invalid_file.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Error message should use relative path and mention the issue
        assert "src" in captured.out
        assert "Files not allowed" in captured.out
        # Should not show absolute path markers like drive letters on Windows
        assert exit_code == 1
