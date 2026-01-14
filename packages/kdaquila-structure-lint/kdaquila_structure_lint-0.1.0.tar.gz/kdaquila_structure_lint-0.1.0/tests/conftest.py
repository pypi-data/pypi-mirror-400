"""Shared fixtures for all tests."""

from pathlib import Path

import pytest

from structure_lint.config import (
    Config,
    LineLimitsConfig,
    OnePerFileConfig,
    StructureConfig,
    ValidatorToggles,
)


@pytest.fixture
def temp_project(tmp_path: Path) -> Path:
    """Create a temporary project directory."""
    return tmp_path


@pytest.fixture
def temp_project_with_pyproject(tmp_path: Path) -> Path:
    """Create a temporary project with a basic pyproject.toml."""
    pyproject = tmp_path / "pyproject.toml"
    pyproject.write_text(
        """[tool.structure-lint]
enabled = true
"""
    )
    return tmp_path


@pytest.fixture
def minimal_config(tmp_path: Path) -> Config:
    """Create a minimal Config object with all defaults."""
    return Config(
        enabled=True,
        project_root=tmp_path,
        validators=ValidatorToggles(),
        line_limits=LineLimitsConfig(),
        one_per_file=OnePerFileConfig(),
        structure=StructureConfig(),
    )


@pytest.fixture
def custom_config(tmp_path: Path) -> Config:
    """Create a Config object with custom settings."""
    return Config(
        enabled=True,
        project_root=tmp_path,
        validators=ValidatorToggles(
            structure=True,
            line_limits=True,
            one_per_file=True,
        ),
        line_limits=LineLimitsConfig(
            max_lines=100,
            search_paths=["src", "lib"],
        ),
        one_per_file=OnePerFileConfig(
            search_paths=["src", "lib"],
        ),
        structure=StructureConfig(
            src_root="lib",
            src_base_folders={"apps", "features"},
            scripts_root="tools",
            standard_folders={"types", "utils", "helpers"},
            general_folder="common",
            free_form_bases={"experimental"},
            allowed_files={"README.md", "NOTES.md"},
        ),
    )


@pytest.fixture
def python_file_factory(tmp_path: Path):
    """Factory fixture to create Python files with specified content."""
    def _create_python_file(
        relative_path: str,
        content: str,
        base_dir: Path | None = None
    ) -> Path:
        """Create a Python file at relative_path with given content.

        Args:
            relative_path: Path relative to base_dir (e.g., "src/module.py")
            content: Content to write to the file
            base_dir: Base directory (defaults to tmp_path)

        Returns:
            Absolute path to created file
        """
        if base_dir is None:
            base_dir = tmp_path

        file_path = base_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")
        return file_path

    return _create_python_file


@pytest.fixture
def sample_valid_file_content() -> str:
    """Return content for a valid Python file."""
    return """def hello():
    '''A simple function.'''
    return "Hello, world!"
"""


@pytest.fixture
def sample_too_long_file_content() -> str:
    """Return content that exceeds typical line limits."""
    lines = ["# Line {i}".format(i=i) for i in range(1, 201)]
    return "\n".join(lines)


@pytest.fixture
def sample_multiple_definitions_content() -> str:
    """Return content with multiple top-level definitions."""
    return """def function_one():
    pass

def function_two():
    pass

class MyClass:
    pass
"""


@pytest.fixture
def sample_empty_file_content() -> str:
    """Return empty file content."""
    return ""


@pytest.fixture
def sample_syntax_error_content() -> str:
    """Return content with Python syntax errors."""
    return """def broken_function(
    # Missing closing parenthesis
    return "incomplete"
"""
