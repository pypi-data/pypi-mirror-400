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

#### `structure.strict_format_roots`

**Type**: `list[str]` (converted to set internally)
**Default**: `["src"]`

List of root directories to validate with the structure validator. Only directories listed here are validated - this is an opt-in model.

```toml
[tool.structure-lint.structure]
strict_format_roots = ["src", "lib"]  # Validate both src/ and lib/
```

**Behavior**:
- At least one root must be specified (empty list is an error)
- Missing roots are warned and skipped (don't cause validation failure)
- Each root is validated independently using the same rules

**Example**:
```
project/
├── src/              # Validated (in strict_format_roots)
├── lib/              # Validated (in strict_format_roots)
├── scripts/          # Not validated (not in strict_format_roots)
└── experiments/      # Not validated (not in strict_format_roots)
```

#### `structure.folder_depth`

**Type**: `int`
**Default**: `2`

Maximum nesting depth for arbitrary-named (custom) folders within a base folder. The `general` folder is also subject to this depth limit.

```toml
[tool.structure-lint.structure]
folder_depth = 3  # Allow deeper nesting
```

**Example with depth=2**:
```
src/features/authentication/     # depth 0 (base folder)
├── services/                    # depth 1 (custom folder)
│   └── oauth/                   # depth 2 (at limit)
│       └── providers/           # depth 3 - ERROR: exceeds limit
```

**Rationale**: Limits folder nesting to prevent overly deep hierarchies that become hard to navigate.

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

#### `structure.files_allowed_anywhere`

**Type**: `list[str]` (converted to set internally)
**Default**: `["__init__.py"]`

List of Python files that are allowed in any directory, even those that normally shouldn't contain files directly.

**Important**: The structure validator only validates `.py` files. Non-Python files (like `README.md`, `.gitkeep`, `py.typed`, etc.) are automatically ignored and do not need to be listed here.

```toml
[tool.structure-lint.structure]
files_allowed_anywhere = ["__init__.py", "conftest.py"]
```

**Note**: In v2.0.0, `internally_allowed_files` was merged into this setting (previously called `allowed_files`). The setting was renamed to `files_allowed_anywhere` to better reflect its purpose now that non-.py files are automatically ignored.

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
strict_format_roots = ["src"]
standard_folders = ["types", "utils", "tests"]
folder_depth = 2
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
strict_format_roots = ["lib"]  # Only validate lib/
standard_folders = ["models", "views", "controllers", "tests"]
general_folder = "common"
folder_depth = 3
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
strict_format_roots = ["src"]  # Validate src/ only
standard_folders = ["types", "utils", "constants", "tests"]
general_folder = "general"
folder_depth = 2
files_allowed_anywhere = ["__init__.py"]
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
4. **Opt-In Validation**: Only directories in `strict_format_roots` are validated - leave out directories you don't want to enforce structure on
5. **Document Choices**: Add comments in `pyproject.toml` explaining your configuration choices

## Migration from v1.x

Version 2.0.0 introduces breaking changes to the structure validation configuration. Here's how to migrate:

### Configuration Changes

| v1.x Field | v2.0.0 Field | Notes |
|------------|--------------|-------|
| `src_root = "src"` | `strict_format_roots = ["src"]` | Now a list, supports multiple roots |
| `free_form_roots = ["experiments"]` | (removed) | Just don't include in `strict_format_roots` |
| (new) | `folder_depth = 2` | Configurable max nesting depth |

### Migration Examples

**Before (v1.x)**:
```toml
[tool.structure-lint.structure]
src_root = "src"
free_form_roots = ["experiments", "legacy"]
standard_folders = ["types", "utils", "tests"]
```

**After (v2.0.0)**:
```toml
[tool.structure-lint.structure]
strict_format_roots = ["src"]  # Only validate src/
# experiments/ and legacy/ are NOT validated (opt-in model)
standard_folders = ["types", "utils", "tests"]
folder_depth = 2
```

### Behavioral Changes

1. **Opt-in Model**: In v1.x, `src_root` was validated and `free_form_roots` were exempted. In v2.0.0, only roots listed in `strict_format_roots` are validated. Everything else is ignored.

2. **Multiple Roots**: You can now validate multiple source directories:
   ```toml
   strict_format_roots = ["src", "lib", "packages"]
   ```

3. **Missing Roots**: If a root in `strict_format_roots` doesn't exist, v2.0.0 warns and continues (v1.x would fail).

4. **Empty Roots Error**: `strict_format_roots` cannot be empty - at least one root is required.

5. **Depth Limits**: The new `folder_depth` setting applies to both custom folders and the `general` folder.

6. **Mutual Exclusivity**: At any folder level, you cannot mix:
   - Standard folders with custom (arbitrary-named) folders
   - General folder with standard folders

## See Also

- [Validator Details](validators.md) - Detailed rules for each validator
- [Examples](examples/) - Sample configuration files
- [README](../README.md) - Main documentation
