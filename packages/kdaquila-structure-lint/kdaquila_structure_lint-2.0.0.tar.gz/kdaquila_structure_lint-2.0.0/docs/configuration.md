# Configuration Reference

This document provides a complete reference for all configuration options available in `kdaquila-structure-lint`.

## Configuration Location

Configuration is stored in your project's `pyproject.toml` file under the `[tool.structure-lint]` section:

```toml
[tool.structure-lint]
enabled = true
# ... additional configuration
```

## Configuration Loading

The configuration system uses a **deep merge** strategy:

1. Load default values for all settings
2. Search for `pyproject.toml` (or use `--config` path if provided)
3. Merge user settings with defaults
4. Any missing field uses the default value

This means you only need to specify the settings you want to change from the defaults.

## Complete Schema

### Master Switch

#### `enabled`

**Type**: `bool`
**Default**: `true`

Master switch to enable/disable the entire linter. Useful for temporarily disabling without removing configuration.

```toml
[tool.structure-lint]
enabled = false  # Disables all validation
```

### Validator Toggles

Control which validators are enabled. Each can be toggled independently.

#### `validators.structure`

**Type**: `bool`
**Default**: `false` (opt-in)

Enable the opinionated structure validator. This is disabled by default because it enforces a specific folder organization pattern.

```toml
[tool.structure-lint.validators]
structure = true  # Opt-in to structure validation
```

#### `validators.line_limits`

**Type**: `bool`
**Default**: `true`

Enable the line limits validator that enforces maximum lines per file.

```toml
[tool.structure-lint.validators]
line_limits = false  # Disable line limit checking
```

#### `validators.one_per_file`

**Type**: `bool`
**Default**: `true`

Enable the one-per-file validator that ensures single top-level definition per file.

```toml
[tool.structure-lint.validators]
one_per_file = false  # Disable one-per-file checking
```

### Line Limits Configuration

Settings for the line limits validator.

#### `line_limits.max_lines`

**Type**: `int`
**Default**: `150`

Maximum number of lines allowed per Python file.

```toml
[tool.structure-lint.line_limits]
max_lines = 200  # Allow up to 200 lines
```

**Rationale**: The default of 150 lines encourages modular code without being overly restrictive. Files beyond this size often indicate opportunities for refactoring.

#### `line_limits.search_paths`

**Type**: `list[str]`
**Default**: `["src"]`

List of directories to search for Python files, relative to project root.

```toml
[tool.structure-lint.line_limits]
search_paths = ["src", "lib", "tools"]  # Custom search paths
```

**Note**: The tool automatically excludes common non-source directories like `.venv`, `__pycache__`, `.git`, etc.

### One-Per-File Configuration

Settings for the one-per-file validator.

#### `one_per_file.search_paths`

**Type**: `list[str]`
**Default**: `["src"]`

List of directories to search for Python files, relative to project root.

```toml
[tool.structure-lint.one_per_file]
search_paths = ["src"]  # Only check src/ directory
```

### Structure Validation Configuration

Settings for the opinionated structure validator.

#### `structure.src_root`

**Type**: `str`
**Default**: `"src"`

Name of the source code root directory.

```toml
[tool.structure-lint.structure]
src_root = "lib"  # Use lib/ instead of src/
```

#### `structure.standard_folders`

**Type**: `list[str]` (converted to set internally)
**Default**: `["types", "utils", "constants", "tests"]`

List of standard folder names that can appear in feature/module directories. These represent common supporting code categories.

```toml
[tool.structure-lint.structure]
standard_folders = ["types", "utils", "constants", "tests", "models", "views"]
```

**Example Structure**:
```
src/features/authentication/
├── types/
├── utils/
├── constants/
└── tests/
```

#### `structure.general_folder`

**Type**: `str`
**Default**: `"general"`

Name of the special "general" folder that can contain Python files directly (without organizing into standard folders).

```toml
[tool.structure-lint.structure]
general_folder = "common"  # Use common/ instead of general/
```

**Purpose**: Provides a place for miscellaneous code that doesn't fit into other categories.

#### `structure.free_form_roots`

**Type**: `list[str]` (converted to set internally)
**Default**: `[]` (empty)

List of top-level directories at project root that are exempted from all structure validation.

```toml
[tool.structure-lint.structure]
free_form_roots = ["experiments", "legacy"]
```

**Use Case**: Useful for areas like experiments or legacy code where you don't want to enforce any structure rules.

**Example Structure**:
```
project_root/
├── src/             # Structure enforced
├── experiments/     # Free-form, no validation
└── legacy/          # Free-form, no validation
```

**Note**: This operates at the project root level, not within src/. Directories listed here are completely skipped during validation.

#### `structure.allowed_files`

**Type**: `list[str]` (converted to set internally)
**Default**: `["__init__.py", "README.md"]`

List of files allowed in directories that normally shouldn't contain files directly. This includes Python package files like `__init__.py` and documentation files.

```toml
[tool.structure-lint.structure]
allowed_files = ["__init__.py", "README.md", "py.typed", ".gitkeep"]
```

**Note**: In v2.0.0, `internally_allowed_files` was merged into `allowed_files`. If you were using `internally_allowed_files`, move those entries to `allowed_files`.

#### `structure.ignored_folders`

**Type**: `list[str]` (converted to set internally)
**Default**: `["__pycache__", ".mypy_cache", ".pytest_cache", ".ruff_cache", ".hypothesis", ".tox", ".coverage", "*.egg-info"]`

List of folder name patterns to ignore during structure validation. Supports wildcards (e.g., `*.egg-info` matches `my_package.egg-info`). These are typically cache, build, or tool-generated directories.

```toml
[tool.structure-lint.structure]
ignored_folders = ["__pycache__", ".mypy_cache", ".venv", "build", "dist", "*.egg-info"]
```

**Use Case**: Add project-specific build or cache directories that should not be validated.

## Common Use Cases

### Minimal Configuration

Just enable the tool with all defaults:

```toml
[tool.structure-lint]
enabled = true
```

This gives you:
- Line limits: 150 lines max
- One-per-file: enforced
- Structure: disabled

### Disable All Validators Temporarily

```toml
[tool.structure-lint]
enabled = false
```

### Increase Line Limit

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.line_limits]
max_lines = 200
```

### Only Check Specific Directory

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.line_limits]
search_paths = ["src"]  # Only check src/

[tool.structure-lint.one_per_file]
search_paths = ["src"]  # Only check src/
```

### Enable Structure Validation

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
structure = true  # Opt-in

[tool.structure-lint.structure]
src_base_folders = ["features", "services"]
standard_folders = ["types", "utils", "tests"]
free_form_roots = []
```

### Custom Project Layout

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
structure = true

[tool.structure-lint.line_limits]
max_lines = 200
search_paths = ["lib", "tools"]

[tool.structure-lint.structure]
src_root = "lib"
src_base_folders = ["modules"]
standard_folders = ["models", "views", "controllers", "tests"]
general_folder = "common"
free_form_roots = ["legacy", "experimental"]
```

### Relaxed Configuration

For projects that want basic checks without strict enforcement:

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = false  # Allow multiple definitions
structure = false

[tool.structure-lint.line_limits]
max_lines = 300  # More lenient
```

### Strict Configuration

For projects that want maximum enforcement:

```toml
[tool.structure-lint]
enabled = true

[tool.structure-lint.validators]
line_limits = true
one_per_file = true
structure = true

[tool.structure-lint.line_limits]
max_lines = 100  # Very strict
search_paths = ["src", "tests"]

[tool.structure-lint.one_per_file]
search_paths = ["src", "tests"]

[tool.structure-lint.structure]
src_base_folders = ["features"]
standard_folders = ["types", "utils", "constants", "tests"]
general_folder = "general"
free_form_roots = []  # No exceptions
allowed_files = ["README.md"]
```

## Configuration Validation

The configuration system validates your settings when loading. Common errors:

### Invalid Type

```toml
[tool.structure-lint.line_limits]
max_lines = "150"  # Error: Should be int, not string
```

### Invalid TOML Syntax

```toml
[tool.structure-lint]
enabled = true
validators.structure = true  # Error: Should use [tool.structure-lint.validators]
```

### Missing Required Parent

```toml
[tool.structure-lint.line_limits]
max_lines = 150
# Note: [tool.structure-lint] parent is optional, defaults will be used
```

## Command-Line Overrides

Some settings can be overridden via command-line arguments:

```bash
# Override project root (ignores auto-detection)
structure-lint --project-root /custom/path

# Use different config file
structure-lint --config /path/to/custom-pyproject.toml

# Enable verbose output
structure-lint --verbose
```

Note: Command-line arguments override configuration file settings.

## Environment-Specific Configuration

For different environments (dev, CI, etc.), you can maintain separate configuration files:

```bash
# Development
structure-lint --config pyproject.dev.toml

# CI (strict)
structure-lint --config pyproject.ci.toml
```

Or use the `enabled` flag to disable in specific environments:

```toml
# pyproject.toml
[tool.structure-lint]
enabled = true  # Enabled locally

# Override in CI with a script that modifies this value
```

## Tips

1. **Start Small**: Begin with just line limits and one-per-file, add structure validation later
2. **Incremental Adoption**: Use high line limits initially, gradually decrease as you refactor
3. **Team Alignment**: Discuss and agree on limits before enforcing in CI/CD
4. **Free-Form Zones**: Use `free_form_bases` for legacy code or experiments
5. **Document Choices**: Add comments in `pyproject.toml` explaining your configuration choices

## See Also

- [Validator Details](validators.md) - Detailed rules for each validator
- [Examples](examples/) - Sample configuration files
- [README](../README.md) - Main documentation
