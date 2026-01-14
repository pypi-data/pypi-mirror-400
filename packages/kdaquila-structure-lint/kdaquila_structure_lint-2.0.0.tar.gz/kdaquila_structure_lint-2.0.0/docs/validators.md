# Validator Reference

This document provides detailed information about each validator in `kdaquila-structure-lint`, including rules, rationale, examples, and customization options.

## Overview

The package includes three validators:

1. **Line Limits Validator** - Enforces maximum lines per file (enabled by default)
2. **One-Per-File Validator** - Ensures single definition per file (enabled by default)
3. **Structure Validator** - Enforces folder organization (opt-in only)

## Line Limits Validator

### Purpose

Enforces a maximum number of lines per Python file to encourage modular, focused code.

### Rationale

Files with hundreds of lines often:
- Violate single responsibility principle
- Are harder to test in isolation
- Create merge conflicts in version control
- Are intimidating for new contributors
- Indicate opportunities for refactoring

The default limit of 150 lines strikes a balance between being permissive enough for real-world code while encouraging good practices.

### Rules

1. Count total lines in each Python file (including blank lines and comments)
2. Report files exceeding `max_lines` threshold
3. Search only in configured `search_paths`
4. Automatically exclude common directories:
   - `.venv/`, `venv/`
   - `__pycache__/`
   - `.git/`, `.hg/`, `.svn/`
   - `node_modules/`

### Configuration

```toml
[tool.structure-lint.validators]
line_limits = true  # Enable/disable

[tool.structure-lint.line_limits]
max_lines = 150       # Default
search_paths = ["src"]  # Default
```

### Examples

#### Passing Example

File with 145 lines:

```python
# src/features/auth/login.py (145 lines)
"""User login functionality."""

from typing import Optional
from .types import User, Credentials

def authenticate_user(credentials: Credentials) -> Optional[User]:
    """Authenticate user with credentials."""
    # ... implementation (140 more lines)
    pass
```

Output:
```
✅ All Python files are within 150 line limit!
```

#### Failing Example

File with 187 lines:

```python
# src/features/auth/user_manager.py (187 lines)
"""User management with too many responsibilities."""

class UserManager:
    def create_user(self): ...
    def update_user(self): ...
    def delete_user(self): ...
    def authenticate(self): ...
    def authorize(self): ...
    def send_email(self): ...
    def generate_report(self): ...
    # ... 180 more lines
```

Output:
```
❌ Found 1 file(s) exceeding 150 line limit:

  • src/features/auth/user_manager.py: 187 lines (exceeds 150 line limit)

💡 Consider splitting large files into smaller, focused modules.
```

### Customization Options

#### Adjust Line Limit

For legacy projects or different conventions:

```toml
[tool.structure-lint.line_limits]
max_lines = 200  # More lenient
```

Or more strict:

```toml
[tool.structure-lint.line_limits]
max_lines = 100  # Forces very small modules
```

#### Change Search Paths

Only check specific directories:

```toml
[tool.structure-lint.line_limits]
search_paths = ["src"]  # Only src/, ignore scripts/
```

Or check additional directories:

```toml
[tool.structure-lint.line_limits]
search_paths = ["src", "lib", "tests"]
```

#### Disable Temporarily

```toml
[tool.structure-lint.validators]
line_limits = false
```

### Migration Strategy

For existing projects with violations:

1. **Start High**: Set `max_lines = 500` to establish baseline
2. **Track Progress**: Gradually lower limit as you refactor
3. **Incremental**: Lower by 50 lines every sprint/release
4. **Target**: Aim for 150 lines eventually

Example progression:
```toml
# Week 1: Establish baseline
max_lines = 500

# Month 1: First reduction
max_lines = 300

# Month 2: Getting closer
max_lines = 200

# Month 3: Target reached
max_lines = 150
```

---

## One-Per-File Validator

### Purpose

Ensures each Python file contains at most one top-level function or class definition.

### Rationale

Single-definition files provide:
- **Discoverability**: Clear file naming (file name = what it contains)
- **Predictability**: Easy to find where something is defined
- **Modularity**: Natural boundaries for code organization
- **Testability**: Easier to write focused unit tests
- **Refactoring**: Simpler to move and reorganize code

### Rules

1. Count top-level functions and classes in each Python file
2. Ignore:
   - Imports
   - Module-level constants
   - Helper functions inside classes
   - Nested functions
   - `__init__.py` files (allowed to have 0 or multiple definitions)
3. Allow 0 definitions (empty files or only constants)
4. Allow 1 definition (pass)
5. Report files with 2+ definitions (fail)

### Configuration

```toml
[tool.structure-lint.validators]
one_per_file = true  # Enable/disable

[tool.structure-lint.one_per_file]
search_paths = ["src"]  # Default
```

### Examples

#### Passing Examples

**Single class:**
```python
# src/features/auth/user.py
"""User model."""

from dataclasses import dataclass

MAX_USERNAME_LENGTH = 50  # Constants OK

@dataclass
class User:
    """User model."""
    username: str
    email: str

    def validate(self):  # Methods inside class OK
        """Validate user data."""
        return len(self.username) <= MAX_USERNAME_LENGTH
```

**Single function:**
```python
# src/utils/formatters/date_formatter.py
"""Format dates for display."""

from datetime import datetime

DEFAULT_FORMAT = "%Y-%m-%d"  # Constants OK

def format_date(date: datetime, format: str = DEFAULT_FORMAT) -> str:
    """Format a date for display."""
    return date.strftime(format)
```

**Empty file or constants only:**
```python
# src/constants/api_keys.py
"""API configuration."""

API_BASE_URL = "https://api.example.com"
API_TIMEOUT = 30
MAX_RETRIES = 3
```

#### Failing Examples

**Multiple classes:**
```python
# src/models/models.py  # BAD: Multiple models
"""User and authentication models."""

class User:
    """User model."""
    pass

class Session:  # Second class - violation!
    """Session model."""
    pass

class Token:  # Third class - violation!
    """Token model."""
    pass
```

Output:
```
❌ Found 1 file(s) with multiple definitions:

  • src/models/models.py: 3 definitions (expected 1)
    - User (class)
    - Session (class)
    - Token (class)

💡 Consider splitting into separate files for better modularity.
```

**Better approach:**
```
src/models/
├── user.py      # Only User class
├── session.py   # Only Session class
└── token.py     # Only Token class
```

**Multiple functions:**
```python
# src/utils/helpers.py  # BAD: Grab-bag of utilities
"""Various helper functions."""

def format_date(date): ...   # First function
def parse_date(string): ...  # Second function - violation!
def validate_email(email): ... # Third function - violation!
```

**Better approach:**
```
src/utils/
├── date_formatter.py      # Only format_date
├── date_parser.py         # Only parse_date
└── email_validator.py     # Only validate_email
```

### Special Cases

#### `__init__.py` Files

`__init__.py` files are **exempt** from this rule. They commonly contain:
- Multiple imports
- Package-level constants
- Re-exports
- Initialization code

```python
# src/features/auth/__init__.py
"""Authentication package."""

from .user import User
from .session import Session
from .login import login
from .logout import logout

__all__ = ["User", "Session", "login", "logout"]
```

#### Type Aliases and Protocols

Type aliases count as definitions:

```python
# src/types/user_types.py
"""User-related types."""

from typing import Protocol

class Authenticatable(Protocol):  # This counts as 1 definition
    """Protocol for authenticatable objects."""
    def authenticate(self) -> bool: ...
```

### Customization Options

#### Change Search Paths

```toml
[tool.structure-lint.one_per_file]
search_paths = ["src"]  # Only check src/
```

#### Disable Temporarily

```toml
[tool.structure-lint.validators]
one_per_file = false
```

### Migration Strategy

For projects with violations:

1. **Identify**: Run validator to find all violations
2. **Prioritize**: Start with files that have 2-3 definitions (easier wins)
3. **Refactor**: Split files and update imports
4. **Test**: Ensure tests still pass after splitting
5. **Repeat**: Tackle larger files

Example refactoring:

**Before:**
```python
# src/utils/string_utils.py (3 definitions)
def capitalize_words(s): ...
def snake_to_camel(s): ...
def truncate_string(s, length): ...
```

**After:**
```
src/utils/
├── word_capitalizer.py   # capitalize_words
├── case_converter.py     # snake_to_camel
└── string_truncator.py   # truncate_string
```

---

## Structure Validator (Opt-in)

### Purpose

Enforces an opinionated folder structure based on feature-driven development and screaming architecture principles.

### Rationale

Consistent structure provides:
- **Navigability**: Predictable location for code
- **Scalability**: Clear patterns for adding features
- **Onboarding**: New developers know where things go
- **Separation**: Clear boundaries between features/modules

**Note**: This is **opt-in by default** because it's highly opinionated. Only enable if your team agrees to this structure.

### Architecture Principles

The structure validator enforces feature/module-based organization within your source tree (`src/`).

### Source Tree Rules

#### Base Structure

```
src/
├── features/          # Base folder (configurable)
│   ├── feature1/
│   ├── feature2/
│   └── ...
└── [other bases]/     # Additional base folders if configured
```

**Rules**:
- `src/` must only contain base folders (no files except `README.md`)
- Base folders (any subdirectories under src/) are automatically validated
- Files not allowed in `src/` root

#### Feature/Module Organization

Each feature/module must follow this structure:

```
src/features/authentication/
├── types/           # Type definitions, protocols, type aliases
├── utils/           # Helper functions and utilities
├── constants/       # Configuration and constants
├── tests/           # Tests for this feature
├── general/         # Miscellaneous code (see below)
└── custom_name/     # Domain-specific folders (see below)
```

**Standard Folders** (configurable via `standard_folders`):
- `types/` - Type definitions, protocols, dataclasses
- `utils/` - Helper functions and utilities
- `constants/` - Configuration values and constants
- `tests/` - Unit and integration tests

**General Folder** (configurable via `general_folder`):
- Special folder that can contain Python files directly
- For code that doesn't fit into standard categories
- Example: `general/login.py` (main login logic)

**Custom Folders**:
- Domain-specific organization
- Must contain standard folders or general folder
- Cannot contain Python files directly
- Example:
  ```
  src/features/authentication/
  └── services/        # Custom folder
      ├── types/
      ├── utils/
      └── general/
  ```

#### Free-Form Roots

Exempt entire top-level directories at project root from all structure validation:

```toml
[tool.structure-lint.structure]
free_form_roots = ["experiments", "legacy"]
```

These directories are completely skipped during validation:
```
project_root/
├── src/            # Structure enforced
├── experiments/    # Completely skipped
└── legacy/         # Completely skipped
```

**Note**: Unlike the old `free_form_bases` which only exempted folders within `src/`, `free_form_roots` operates at the project root level and completely exempts those directories from all validation.

### Configuration

```toml
[tool.structure-lint.validators]
structure = true  # Must opt-in explicitly

[tool.structure-lint.structure]
src_root = "src"
standard_folders = ["types", "utils", "constants", "tests"]
general_folder = "general"
free_form_roots = []
allowed_files = ["README.md"]
```

### Examples

#### Valid Structure

```
project/
├── src/
│   └── features/
│       ├── authentication/
│       │   ├── types/
│       │   │   └── user.py
│       │   ├── utils/
│       │   │   └── hash_password.py
│       │   ├── constants/
│       │   │   └── config.py
│       │   ├── tests/
│       │   │   └── test_login.py
│       │   └── general/
│       │       └── login.py
│       └── reporting/
│           ├── types/
│           ├── utils/
│           └── general/
```

#### Invalid Examples

**Files in src root:**
```
src/
├── main.py          # ❌ Files not allowed in src/
└── features/
```

Error: `src/: Files not allowed in root: ['main.py']`

**Missing base folder:**
```
src/
└── authentication/  # ❌ Should be under features/
```

Error: `src/: Unexpected folders: {'authentication'}`

**Python files in custom folder:**
```
src/features/auth/
├── services/
│   └── login.py     # ❌ Should be in services/general/login.py
```

Error: `src/features/auth/services/: Python files not allowed directly in custom folder`

**Unknown standard folder:**
```
src/features/auth/
└── models/          # ❌ Not in standard_folders
```

Error: `src/features/auth/: Unexpected folder 'models' (not in standard folders or custom)`

### Customization Options

#### Different Base Folders

Any subdirectories under `src/` are automatically accepted as base folders:
```
src/
├── features/
├── services/
└── components/
```

All base folders are validated according to the same structure rules.

#### Different Standard Folders

```toml
[tool.structure-lint.structure]
standard_folders = ["models", "views", "controllers", "tests"]
```

Enables MVC-style organization:
```
src/features/authentication/
├── models/
├── views/
├── controllers/
└── tests/
```

#### Custom Root Names

```toml
[tool.structure-lint.structure]
src_root = "lib"
general_folder = "common"
```

Results in:
```
lib/features/auth/common/login.py
```

#### Free-Form Zones

```toml
[tool.structure-lint.structure]
free_form_roots = ["legacy", "experiments"]
```

```
project_root/
├── src/
│   └── features/    # Strict structure enforced
├── legacy/          # Completely skipped from validation
└── experiments/     # Completely skipped from validation
```

### Migration Strategy

Adopting the structure validator for existing projects:

#### 1. Assess Current State

Run with structure validation enabled to see violations:

```bash
structure-lint --verbose
```

#### 2. Choose Approach

**Option A: Gradual Migration**
- Use `free_form_roots` to exclude legacy code
- Apply structure to new features only
- Gradually migrate old code

```toml
[tool.structure-lint.structure]
free_form_roots = ["legacy"]  # Completely skip legacy directory
```

**Option B: Full Reorganization**
- Plan complete restructure
- Create new structure alongside old
- Migrate in phases
- Update imports
- Run tests continuously

#### 3. Customize to Fit

Don't fight the tool - customize it:

```toml
[tool.structure-lint.structure]
# Match your team's conventions
standard_folders = ["types", "models", "services", "utils", "tests"]
general_folder = "core"
```

#### 4. Document Decisions

Add comments to your config explaining choices:

```toml
[tool.structure-lint.structure]
# Added "services" as standard folder for our microservice architecture
standard_folders = ["types", "services", "utils", "tests"]

# Legacy code exempted until Q3 2026 refactor
free_form_roots = ["legacy"]
```

### When to Use Structure Validation

**Use when**:
- Starting a new project
- Team agrees on structure conventions
- Project is growing and needs organization
- Onboarding new developers frequently

**Don't use when**:
- Small projects (< 5 files)
- Exploratory/prototype phase
- Team hasn't agreed on structure
- Legacy project with different conventions

---

## Common Questions

### Can I disable validators temporarily?

Yes, use the `enabled` master switch:

```toml
[tool.structure-lint]
enabled = false  # Disables everything
```

Or disable individual validators:

```toml
[tool.structure-lint.validators]
line_limits = false
one_per_file = false
structure = false
```

### Can I exclude specific files or folders?

Currently, validators skip these directories automatically:
- `.venv/`, `venv/`
- `__pycache__/`
- `.git/`, `.hg/`, `.svn/`
- `node_modules/`

For more specific exclusions, adjust `search_paths`:

```toml
[tool.structure-lint.line_limits]
search_paths = ["src"]  # Doesn't check scripts/
```

### What if I disagree with the defaults?

All rules are configurable! Adjust to fit your team:

```toml
[tool.structure-lint.line_limits]
max_lines = 300  # Your choice

[tool.structure-lint.validators]
one_per_file = false  # Disable if not relevant
```

### How do I run only one validator?

Disable the others:

```toml
[tool.structure-lint.validators]
line_limits = true    # Only this enabled
one_per_file = false
structure = false
```

---

## See Also

- [Configuration Reference](configuration.md) - All configuration options
- [Examples](examples/) - Sample configurations
- [README](../README.md) - Main documentation
