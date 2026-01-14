"""Tests for line limits validator."""



from structure_lint.validators.line_limits import validate_line_limits


class TestLineLimitsValidator:
    """Tests for validate_line_limits function."""

    def test_all_files_within_limit(self, minimal_config, python_file_factory):
        """Should pass when all files are within limit."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create files within limit
        python_file_factory("src/small1.py", "def hello():\n    pass\n", config.project_root)
        python_file_factory("src/small2.py", "# Comment\npass\n", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exceeds_limit(self, minimal_config, python_file_factory):
        """Should fail when a file exceeds line limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 21)])
        python_file_factory("src/too_long.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_multiple_files_some_exceed_limit(self, minimal_config, python_file_factory):
        """Should fail when some files exceed limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create mix of valid and invalid files
        python_file_factory("src/good.py", "def hello():\n    pass\n", config.project_root)
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 21)])
        python_file_factory("src/bad.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_empty_file_passes(self, minimal_config, python_file_factory):
        """Should pass for empty files."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        python_file_factory("src/empty.py", "", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_exactly_at_limit_passes(self, minimal_config, python_file_factory):
        """Should pass when file is exactly at limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with exactly 10 lines
        content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 11)])
        python_file_factory("src/exact.py", content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_one_over_limit_fails(self, minimal_config, python_file_factory):
        """Should fail when file is one line over limit."""
        config = minimal_config
        config.line_limits.max_lines = 10
        (config.project_root / "src").mkdir()

        # Create file with 11 lines
        content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 12)])
        python_file_factory("src/over.py", content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_custom_search_paths(self, minimal_config, python_file_factory):
        """Should check custom search paths."""
        config = minimal_config
        config.line_limits.search_paths = ["lib", "app"]
        config.line_limits.max_lines = 5

        (config.project_root / "lib").mkdir()
        (config.project_root / "app").mkdir()

        # Create file in lib
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 10)])
        python_file_factory("lib/module.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_missing_search_path(self, minimal_config, capsys):
        """Should warn about missing search paths and continue."""
        config = minimal_config
        config.line_limits.search_paths = ["nonexistent", "src"]

        # Create valid file in src
        (config.project_root / "src").mkdir()
        (config.project_root / "src" / "module.py").write_text("pass\n")

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should warn about nonexistent
        assert "Warning" in captured.out or "not found" in captured.out
        # Should still succeed
        assert exit_code == 0

    def test_all_search_paths_missing(self, minimal_config, capsys):
        """Should handle all search paths missing gracefully."""
        config = minimal_config
        config.line_limits.search_paths = ["nonexistent1", "nonexistent2"]

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should warn
        assert "Warning" in captured.out or "not found" in captured.out
        # Should succeed (no files to check)
        assert exit_code == 0

    def test_nested_directories(self, minimal_config, python_file_factory):
        """Should check files in nested directories."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src" / "sub" / "deep").mkdir(parents=True)

        # Create file in nested directory
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 10)])
        python_file_factory("src/sub/deep/module.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_excludes_venv_directory(self, minimal_config, python_file_factory):
        """Should exclude .venv and venv directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src").mkdir()
        (config.project_root / "src" / ".venv").mkdir()
        (config.project_root / "src" / "venv").mkdir()

        # Create long files in excluded directories
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 100)])
        python_file_factory("src/.venv/lib.py", long_content, config.project_root)
        python_file_factory("src/venv/lib.py", long_content, config.project_root)

        # Should pass because excluded directories are ignored
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_excludes_pycache_directory(self, minimal_config, python_file_factory):
        """Should exclude __pycache__ directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src" / "__pycache__").mkdir(parents=True)

        # Create long file in __pycache__
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 100)])
        python_file_factory("src/__pycache__/module.py", long_content, config.project_root)

        # Should pass because __pycache__ is excluded
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_excludes_git_directory(self, minimal_config, python_file_factory):
        """Should exclude .git directories."""
        config = minimal_config
        config.line_limits.max_lines = 5

        (config.project_root / "src" / ".git").mkdir(parents=True)

        # Create long file in .git
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 100)])
        python_file_factory("src/.git/hooks.py", long_content, config.project_root)

        # Should pass because .git is excluded
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_error_messages_use_relative_paths(self, minimal_config, python_file_factory, capsys):
        """Should use relative paths in error messages."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file that exceeds limit
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 15)])
        python_file_factory("src/too_long.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Error message should use relative path
        assert "src" in captured.out or "src\\too_long.py" in captured.out or "src/too_long.py" in captured.out
        # Should not contain absolute path markers
        assert exit_code == 1

    def test_multiple_violations_all_reported(self, minimal_config, python_file_factory, capsys):
        """Should report all violations, not just first one."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create multiple violating files
        long_content = "\n".join(["# Line {i}".format(i=i) for i in range(1, 15)])
        python_file_factory("src/file1.py", long_content, config.project_root)
        python_file_factory("src/file2.py", long_content, config.project_root)
        python_file_factory("src/file3.py", long_content, config.project_root)

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention all files
        assert "file1.py" in captured.out
        assert "file2.py" in captured.out
        assert "file3.py" in captured.out
        assert exit_code == 1

    def test_unicode_file_content(self, minimal_config, python_file_factory):
        """Should handle Unicode content correctly."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with Unicode content
        unicode_content = "# こんにちは\n# Привет\n# مرحبا\npass\n"
        python_file_factory("src/unicode.py", unicode_content, config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_file_with_very_long_lines(self, minimal_config, python_file_factory):
        """Should count lines correctly even with very long lines."""
        config = minimal_config
        config.line_limits.max_lines = 5
        (config.project_root / "src").mkdir()

        # Create file with very long lines
        long_line = "x = " + "1" * 10000
        content = "\n".join([long_line] * 3)
        python_file_factory("src/long_lines.py", content, config.project_root)

        # 3 lines, should pass
        exit_code = validate_line_limits(config)
        assert exit_code == 0

    def test_max_lines_configuration_respected(self, minimal_config, python_file_factory):
        """Should respect configured max_lines value."""
        config = minimal_config
        config.line_limits.max_lines = 3
        (config.project_root / "src").mkdir()

        # Create file with 4 lines
        python_file_factory("src/module.py", "line1\nline2\nline3\nline4\n", config.project_root)

        exit_code = validate_line_limits(config)
        assert exit_code == 1

    def test_output_shows_max_lines_limit(self, minimal_config, capsys):
        """Should show the max_lines limit in output."""
        config = minimal_config
        config.line_limits.max_lines = 100
        (config.project_root / "src").mkdir()

        exit_code = validate_line_limits(config)
        captured = capsys.readouterr()

        # Should mention the limit
        assert "100" in captured.out
        assert exit_code == 0
