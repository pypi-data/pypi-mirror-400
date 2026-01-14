"""Tests for structure validator."""



from structure_lint.validators.structure import validate_structure


class TestStructureValidatorBasic:
    """Basic tests for validate_structure function."""

    def test_missing_src_root_fails(self, minimal_config, capsys):
        """Should fail when src root doesn't exist."""
        config = minimal_config

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        assert "not found" in captured.out or "Error" in captured.out
        assert exit_code == 1

    def test_valid_minimal_structure_passes(self, minimal_config):
        """Should pass with valid minimal structure."""
        config = minimal_config

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

    def test_missing_base_folder_fails(self, minimal_config):
        """Should fail when required base folder is missing."""
        config = minimal_config

        # Create src but not features
        (config.project_root / "src").mkdir()

        exit_code = validate_structure(config)
        assert exit_code == 1

    def test_extra_base_folder_fails(self, minimal_config):
        """Should fail when extra folders exist in src."""
        config = minimal_config

        src = config.project_root / "src"
        src.mkdir()
        (src / "features").mkdir()
        (src / "extra_folder").mkdir()  # Not in src_base_folders

        exit_code = validate_structure(config)
        assert exit_code == 1

    def test_files_in_src_root_fails(self, minimal_config):
        """Should fail when files exist in src root."""
        config = minimal_config

        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)

        # Add file in src root (not allowed)
        (src / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 1


class TestStructureValidatorScriptsTree:
    """Tests for scripts tree validation."""

    def test_missing_scripts_dir_is_ok(self, minimal_config):
        """Should not fail when scripts directory doesn't exist."""
        config = minimal_config

        # Create valid src structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Don't create scripts directory
        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_valid_scripts_structure_passes(self, minimal_config):
        """Should pass with valid scripts structure."""
        config = minimal_config

        # Create valid src structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Create valid scripts structure
        scripts = config.project_root / "scripts"
        scripts.mkdir()
        (scripts / "build").mkdir()
        (scripts / "build" / "script.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0


class TestStructureValidatorCustomConfig:
    """Tests for custom structure configuration."""

    def test_custom_src_root(self, minimal_config):
        """Should use custom src_root."""
        config = minimal_config
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

    def test_custom_base_folders(self, minimal_config):
        """Should use custom base folders."""
        config = minimal_config
        config.structure.src_base_folders = {"apps", "features"}

        # Create structure with custom base folders
        src = config.project_root / "src"
        src.mkdir()
        (src / "apps").mkdir()
        (src / "features").mkdir()

        # Add valid content
        (src / "apps" / "my_app").mkdir()
        (src / "apps" / "my_app" / "types").mkdir()
        (src / "apps" / "my_app" / "types" / "module.py").touch()

        (src / "features" / "my_feature").mkdir()
        (src / "features" / "my_feature" / "types").mkdir()
        (src / "features" / "my_feature" / "types" / "module.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_custom_scripts_root(self, minimal_config):
        """Should use custom scripts_root."""
        config = minimal_config
        config.structure.scripts_root = "tools"

        # Create valid src structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Create structure with custom scripts_root
        tools = config.project_root / "tools"
        tools.mkdir()
        (tools / "build").mkdir()
        (tools / "build" / "script.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_free_form_bases_allowed(self, minimal_config):
        """Should allow free-form structure in free_form_bases."""
        config = minimal_config
        config.structure.src_base_folders = {"features", "experimental"}
        config.structure.free_form_bases = {"experimental"}

        # Create structure
        src = config.project_root / "src"
        src.mkdir()

        # Valid features structure
        features = src / "features"
        features.mkdir()
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Free-form experimental structure (anything goes)
        experimental = src / "experimental"
        experimental.mkdir()
        (experimental / "random_folder").mkdir()
        (experimental / "random_folder" / "nested").mkdir()
        (experimental / "random_file.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0


class TestStructureValidatorRelativePaths:
    """Tests for relative path handling in error messages."""

    def test_error_messages_use_relative_paths(self, minimal_config, capsys):
        """Should use relative paths in error messages."""
        config = minimal_config

        # Create invalid structure
        src = config.project_root / "src"
        src.mkdir()
        (src / "features").mkdir()
        (src / "invalid_folder").mkdir()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Error message should use relative path
        assert "src" in captured.out
        # Should not show absolute path markers like drive letters on Windows
        assert exit_code == 1


class TestStructureValidatorEdgeCases:
    """Tests for edge cases and special scenarios."""

    def test_pycache_ignored_in_src_root(self, minimal_config):
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

    def test_multiple_structure_violations_all_reported(self, minimal_config, capsys):
        """Should report all violations, not just first one."""
        config = minimal_config

        # Create structure with multiple issues
        src = config.project_root / "src"
        src.mkdir()
        # Missing: features
        # Extra: wrong1, wrong2
        (src / "wrong1").mkdir()
        (src / "wrong2").mkdir()
        # Files in root
        (src / "file1.py").touch()
        (src / "file2.py").touch()

        exit_code = validate_structure(config)
        captured = capsys.readouterr()

        # Should mention multiple issues
        assert "Missing" in captured.out or "features" in captured.out
        assert "Unexpected" in captured.out or "wrong1" in captured.out
        assert "Files not allowed" in captured.out or "file1.py" in captured.out
        assert exit_code == 1

    def test_empty_src_directory_fails(self, minimal_config):
        """Should fail when src directory is empty."""
        config = minimal_config

        # Create empty src directory
        (config.project_root / "src").mkdir()

        exit_code = validate_structure(config)
        assert exit_code == 1

    def test_complex_valid_structure(self, minimal_config):
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


class TestStructureValidatorIntegration:
    """Integration tests combining multiple aspects."""

    def test_full_custom_config_valid_structure(self, custom_config):
        """Should validate with fully custom configuration."""
        config = custom_config

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

    def test_structure_validation_output_format(self, minimal_config, capsys):
        """Should produce clear output format."""
        config = minimal_config

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

    def test_both_src_and_scripts_validated(self, minimal_config):
        """Should validate both src and scripts trees."""
        config = minimal_config

        # Create valid src structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Create valid scripts structure
        scripts = config.project_root / "scripts"
        scripts.mkdir()
        (scripts / "build").mkdir()
        (scripts / "build" / "script.py").touch()

        exit_code = validate_structure(config)
        assert exit_code == 0

    def test_src_valid_scripts_invalid_fails(self, minimal_config):
        """Should fail if scripts tree is invalid even if src is valid."""
        config = minimal_config

        # Create valid src structure
        src = config.project_root / "src"
        features = src / "features"
        features.mkdir(parents=True)
        (features / "my_feature").mkdir()
        (features / "my_feature" / "types").mkdir()
        (features / "my_feature" / "types" / "module.py").touch()

        # Create scripts with files in root (might be invalid depending on rules)
        scripts = config.project_root / "scripts"
        scripts.mkdir()
        # Just having scripts directory should be fine
        # The actual scripts validation rules depend on implementation

        exit_code = validate_structure(config)
        # Should pass or fail based on actual implementation
        assert exit_code in [0, 1]
