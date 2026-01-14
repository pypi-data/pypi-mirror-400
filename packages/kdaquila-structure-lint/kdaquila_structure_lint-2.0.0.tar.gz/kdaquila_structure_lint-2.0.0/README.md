# kdaquila-structure-lint

Opinionated Python project structure and code quality linter.

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/downloads/)

## Overview

`kdaquila-structure-lint` is a Python linter that enforces code quality and project structure conventions. It provides three validators that can be enabled independently:

- **Line Limits Validator** (enabled by default) - Enforces maximum line count per file
- **One-Per-File Validator** (enabled by default) - Ensures single function/class per file
- **Structure Validator** (opt-in) - Enforces opinionated folder structure rules

## Installation

Install from PyPI using pip:

```bash
pip install kdaquila-structure-lint
```

For development installations:

```bash
git clone https://github.com/kdaquila/kdaquila-structure-lint.git
cd kdaquila-structure-lint
pip install -e ".[dev]"
```

## Quick Start

Run the linter in your project directory:

```bash
structure-lint
```

The tool will:
1. Auto-detect your project root by searching for `pyproject.toml`
2. Load configuration from `[tool.structure-lint]` section (or use defaults)
3. Run all enabled validators
4. Report any violations with clear error messages

### Basic Example

Add configuration to your `pyproject.toml`:

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = false  # Opt-in only
```

Run the linter:

```bash
structure-lint
```

## Features

### Line Limits Validator

Enforces a maximum number of lines per Python file to encourage modular, maintainable code.

**Default**: 150 lines per file

**Configuration**:
```toml
[tool.structure-lint.line_limits]
max_lines = 150
search_paths = ["src"]
```

**Example Output**:
```
============================================================
Running line limit validation...
============================================================
✗ src/features/data_processing/processor.py: 187 lines (exceeds 150 line limit)
✗ src/analysis/report_generator.py: 203 lines (exceeds 150 line limit)

2 files exceed the line limit
```

### One-Per-File Validator

Ensures each Python file contains at most one top-level function or class definition, promoting better organization and discoverability.

**Configuration**:
```toml
[tool.structure-lint.one_per_file]
search_paths = ["src"]
```

**Example Output**:
```
============================================================
Running one-per-file validation...
============================================================
✗ src/utils/helpers.py: 3 definitions (expected 1)
  - format_date (function)
  - parse_date (function)
  - DateFormatter (class)

1 file violates one-per-file rule
```

### Structure Validator (Opt-in)

Enforces an opinionated folder structure based on feature-driven development principles. This validator is disabled by default as it's highly prescriptive.

**Enable with**:
```toml
[tool.structure-lint.validators]
structure = true
```

See [docs/validators.md](docs/validators.md) for detailed structure rules.

## Configuration

### Minimal Configuration

Create a minimal configuration in your `pyproject.toml`:

```toml
[tool.structure-lint]
enabled = true
```

This uses all default settings with `line_limits` and `one_per_file` enabled.

### Full Configuration

See all available options:

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
structure = false        # Opt-in (default: disabled)
line_limits = true       # Default: enabled
one_per_file = true      # Default: enabled

[tool.structure-lint.line_limits]
max_lines = 150
search_paths = ["src"]

[tool.structure-lint.one_per_file]
search_paths = ["src"]

[tool.structure-lint.structure]
src_root = "src"
standard_folders = ["types", "utils", "constants", "tests"]
general_folder = "general"
free_form_roots = []
allowed_files = ["__init__.py", "README.md"]
ignored_folders = ["__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".hypothesis", ".tox", ".coverage", "*.egg-info"]
```

For detailed configuration options, see [docs/configuration.md](docs/configuration.md).

### Example Configurations

Example configurations are available in the `docs/examples/` directory:

- [`minimal_config.toml`](docs/examples/minimal_config.toml) - Bare minimum configuration
- [`full_config.toml`](docs/examples/full_config.toml) - All options with defaults
- [`custom_structure.toml`](docs/examples/custom_structure.toml) - Custom structure validation setup

## Command-Line Interface

### Basic Usage

```bash
structure-lint                    # Run in current directory
structure-lint --verbose          # Show detailed output
structure-lint --version          # Show version
structure-lint --help             # Show help message
```

### Advanced Options

```bash
# Specify project root explicitly
structure-lint --project-root /path/to/project

# Use a specific pyproject.toml file
structure-lint --config /path/to/pyproject.toml

# Verbose output (shows project root and detailed progress)
structure-lint --verbose
```

## Exit Codes

The CLI returns different exit codes for automation and CI/CD integration:

- `0` - All validations passed
- `1` - One or more validations failed
- `2` - Configuration error or unexpected error

## Usage in CI/CD

### GitHub Actions

Add to your `.github/workflows/ci.yml`:

```yaml
name: CI

on: [push, pull_request]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: actions/setup-python@v4
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          pip install kdaquila-structure-lint
      - name: Run structure linter
        run: structure-lint
```

### Pre-commit Hook

Add to your `.pre-commit-config.yaml`:

```yaml
repos:
  - repo: local
    hooks:
      - id: structure-lint
        name: structure-lint
        entry: structure-lint
        language: system
        pass_filenames: false
```

### GitLab CI

Add to your `.gitlab-ci.yml`:

```yaml
structure-lint:
  image: python:3.11
  script:
    - pip install kdaquila-structure-lint
    - structure-lint
```

## Development

### Running Tests

```bash
pip install -e ".[dev]"
pytest
```

### Type Checking

```bash
mypy src/features
```

### Linting

```bash
ruff check src/features tests
```

## Documentation

- [Configuration Reference](docs/configuration.md) - Complete schema and options
- [Validator Details](docs/validators.md) - In-depth validator documentation
- [Examples](docs/examples/) - Sample configurations

## Philosophy

This linter enforces opinions about code organization based on these principles:

1. **Modularity** - Files should be small and focused
2. **Discoverability** - One definition per file makes code easier to find
3. **Consistency** - Predictable structure reduces cognitive load
4. **Flexibility** - All rules are configurable and can be disabled

The structure validator is opt-in because it's highly opinionated. The other validators (line limits and one-per-file) represent more universally accepted best practices.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Author

Created by kdaquila

## Links

- [GitHub Repository](https://github.com/kdaquila/kdaquila-structure-lint)
- [Issue Tracker](https://github.com/kdaquila/kdaquila-structure-lint/issues)
- [PyPI Package](https://pypi.org/project/kdaquila-structure-lint/)
