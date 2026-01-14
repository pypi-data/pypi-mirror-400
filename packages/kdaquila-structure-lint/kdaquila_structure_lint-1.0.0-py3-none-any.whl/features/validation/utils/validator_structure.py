"""Validates project folder structure conventions.

Validates the src tree which has base_folders (apps, features) with structured rules.

See utils/structure/ modules for detailed validation logic.
"""

import sys

from features.config import Config
from features.validation.utils.structure_src_tree import validate_src_tree


def validate_structure(config: Config) -> int:
    """Run validation on src tree and return exit code."""
    project_root = config.project_root
    src_root = config.structure.src_root
    free_form_roots = config.structure.free_form_roots
    all_errors: list[str] = []

    # Validate src tree (unless src_root itself is in free_form_roots)
    if src_root in free_form_roots:
        print(f"⏭️  Skipping {src_root}/ (in free_form_roots)")
        print("✅ All folder structures are valid!")
        return 0

    src_path = project_root / src_root
    if not src_path.exists():
        print(f"❌ Error: {src_root}/ not found")
        return 1

    print(f"🔍 Validating {src_root}/ tree...")
    src_errors = validate_src_tree(src_path, config)
    # Make paths relative to project root for cleaner error messages
    src_errors = [
        error.replace(str(project_root) + "\\", "").replace(str(project_root) + "/", "")
        for error in src_errors
    ]
    all_errors.extend(src_errors)

    # Report results
    if all_errors:
        print(f"\n❌ Found {len(all_errors)} validation error(s):\n")
        for error in all_errors:
            print(f"  • {error}")
        return 1

    print("✅ All folder structures are valid!")
    return 0


if __name__ == "__main__":
    from features.config import load_config

    config = load_config()
    sys.exit(validate_structure(config))
