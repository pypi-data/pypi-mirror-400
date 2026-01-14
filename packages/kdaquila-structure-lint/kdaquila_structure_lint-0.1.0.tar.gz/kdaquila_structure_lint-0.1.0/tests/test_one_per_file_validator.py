"""Tests for one-per-file validator."""



from structure_lint.validators.one_per_file import validate_one_per_file


class TestOnePerFileValidator:
    """Tests for validate_one_per_file function."""

    def test_files_with_single_definition_pass(self, minimal_config, python_file_factory):
        """Should pass when files have single definition."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create files with single definitions
        python_file_factory("src/func.py", "def hello():\n    pass\n", config.project_root)
        python_file_factory("src/cls.py", "class MyClass:\n    pass\n", config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_multiple_functions_fails(self, minimal_config, python_file_factory):
        """Should fail when file has multiple functions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def func1():
    pass

def func2():
    pass
"""
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_file_with_multiple_classes_fails(self, minimal_config, python_file_factory):
        """Should fail when file has multiple classes."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class Class1:
    pass

class Class2:
    pass
"""
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_file_with_function_and_class_fails(self, minimal_config, python_file_factory):
        """Should fail when file has both function and class."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def my_func():
    pass

class MyClass:
    pass
"""
        python_file_factory("src/mixed.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_empty_file_passes(self, minimal_config, python_file_factory):
        """Should pass for empty files (0 definitions)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        python_file_factory("src/empty.py", "", config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_only_imports_passes(self, minimal_config, python_file_factory):
        """Should pass for files with only imports (0 top-level definitions)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """import os
import sys
from pathlib import Path
"""
        python_file_factory("src/imports.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_constants_and_function_passes(self, minimal_config, python_file_factory):
        """Should pass when file has constants plus one function (constants don't count)."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """MAX_SIZE = 100
DEFAULT_NAME = "test"

def process():
    pass
"""
        python_file_factory("src/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_async_function_counted(self, minimal_config, python_file_factory):
        """Should count async functions as definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """async def async_func():
    pass

def sync_func():
    pass
"""
        python_file_factory("src/async.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_nested_functions_not_counted(self, minimal_config, python_file_factory):
        """Should not count nested functions as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def outer():
    def inner():
        pass
    return inner
"""
        python_file_factory("src/nested.py", content, config.project_root)

        # Only one top-level definition (outer)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_nested_classes_not_counted(self, minimal_config, python_file_factory):
        """Should not count nested classes as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class Outer:
    class Inner:
        pass
"""
        python_file_factory("src/nested.py", content, config.project_root)

        # Only one top-level definition (Outer)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_class_methods_not_counted(self, minimal_config, python_file_factory):
        """Should not count class methods as separate definitions."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """class MyClass:
    def method1(self):
        pass

    def method2(self):
        pass

    async def method3(self):
        pass
"""
        python_file_factory("src/class.py", content, config.project_root)

        # Only one top-level definition (MyClass)
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_custom_search_paths(self, minimal_config, python_file_factory):
        """Should check custom search paths."""
        config = minimal_config
        config.one_per_file.search_paths = ["lib", "app"]

        (config.project_root / "lib").mkdir()
        (config.project_root / "app").mkdir()

        # Create violating file in lib
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("lib/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_missing_search_path(self, minimal_config, capsys):
        """Should warn about missing search paths and continue."""
        config = minimal_config
        config.one_per_file.search_paths = ["nonexistent", "src"]

        # Create valid file in src
        (config.project_root / "src").mkdir()
        (config.project_root / "src" / "module.py").write_text("def hello():\n    pass\n")

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should warn about nonexistent
        assert "Warning" in captured.out or "not found" in captured.out
        # Should still succeed
        assert exit_code == 0

    def test_all_search_paths_missing(self, minimal_config, capsys):
        """Should handle all search paths missing gracefully."""
        config = minimal_config
        config.one_per_file.search_paths = ["nonexistent1", "nonexistent2"]

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should warn
        assert "Warning" in captured.out or "not found" in captured.out
        # Should succeed (no files to check)
        assert exit_code == 0

    def test_nested_directories(self, minimal_config, python_file_factory):
        """Should check files in nested directories."""
        config = minimal_config
        (config.project_root / "src" / "sub" / "deep").mkdir(parents=True)

        # Create violating file in nested directory
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/sub/deep/module.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_excludes_venv_directory(self, minimal_config, python_file_factory):
        """Should exclude .venv and venv directories."""
        config = minimal_config

        (config.project_root / "src").mkdir()
        (config.project_root / "src" / ".venv").mkdir()
        (config.project_root / "src" / "venv").mkdir()

        # Create violating files in excluded directories
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/.venv/lib.py", content, config.project_root)
        python_file_factory("src/venv/lib.py", content, config.project_root)

        # Should pass because excluded directories are ignored
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_pycache_directory(self, minimal_config, python_file_factory):
        """Should exclude __pycache__ directories."""
        config = minimal_config

        (config.project_root / "src" / "__pycache__").mkdir(parents=True)

        # Create violating file in __pycache__
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/__pycache__/module.py", content, config.project_root)

        # Should pass because __pycache__ is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_excludes_git_directory(self, minimal_config, python_file_factory):
        """Should exclude .git directories."""
        config = minimal_config

        (config.project_root / "src" / ".git").mkdir(parents=True)

        # Create violating file in .git
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/.git/hooks.py", content, config.project_root)

        # Should pass because .git is excluded
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_syntax_error_reported_as_failure(self, minimal_config, python_file_factory, capsys):
        """Should report files with syntax errors."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create file with syntax error
        content = "def broken(\n    # Missing closing paren\n"
        python_file_factory("src/broken.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should report error
        assert "Error parsing file" in captured.out or "broken.py" in captured.out
        assert exit_code == 1

    def test_error_messages_use_relative_paths(self, minimal_config, python_file_factory, capsys):
        """Should use relative paths in error messages."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create violating file
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Error message should use relative path
        assert "src" in captured.out or "src\\multi.py" in captured.out or "src/multi.py" in captured.out
        assert exit_code == 1

    def test_multiple_violations_all_reported(self, minimal_config, python_file_factory, capsys):
        """Should report all violations, not just first one."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Create multiple violating files
        content = "def func1():\n    pass\n\ndef func2():\n    pass\n"
        python_file_factory("src/file1.py", content, config.project_root)
        python_file_factory("src/file2.py", content, config.project_root)
        python_file_factory("src/file3.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should mention all files
        assert "file1.py" in captured.out
        assert "file2.py" in captured.out
        assert "file3.py" in captured.out
        assert exit_code == 1

    def test_error_message_shows_definition_names(self, minimal_config, python_file_factory, capsys):
        """Should show names of definitions in error message."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """def hello():
    pass

def world():
    pass

class Greeting:
    pass
"""
        python_file_factory("src/multi.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should mention definition names
        assert "hello" in captured.out
        assert "world" in captured.out
        assert "Greeting" in captured.out
        assert exit_code == 1

    def test_unicode_in_definition_names(self, minimal_config, python_file_factory):
        """Should handle Unicode in definition names."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Python allows Unicode identifiers
        content = """def функция():
    pass

def 函数():
    pass
"""
        python_file_factory("src/unicode.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_file_with_decorators_counted_once(self, minimal_config, python_file_factory):
        """Should count decorated functions as single definition."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """@decorator
@another_decorator
def decorated():
    pass
"""
        python_file_factory("src/decorated.py", content, config.project_root)

        # Only one definition despite decorators
        exit_code = validate_one_per_file(config)
        assert exit_code == 0

    def test_file_with_multiple_decorated_functions_fails(self, minimal_config, python_file_factory):
        """Should count each decorated function separately."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        content = """@decorator1
def func1():
    pass

@decorator2
def func2():
    pass
"""
        python_file_factory("src/multi_decorated.py", content, config.project_root)

        exit_code = validate_one_per_file(config)
        assert exit_code == 1

    def test_output_format(self, minimal_config, python_file_factory, capsys):
        """Should produce clear output format."""
        config = minimal_config
        (config.project_root / "src").mkdir()

        # Valid case
        python_file_factory("src/good.py", "def hello():\n    pass\n", config.project_root)

        exit_code = validate_one_per_file(config)
        captured = capsys.readouterr()

        # Should have clear success message
        assert "Checking" in captured.out or "one function/class per file" in captured.out
        assert exit_code == 0
