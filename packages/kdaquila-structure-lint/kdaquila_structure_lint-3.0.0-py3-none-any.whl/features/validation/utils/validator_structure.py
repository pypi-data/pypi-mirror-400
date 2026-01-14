"""Validates project folder structure conventions.

Validates strict_format_roots which have base_folders (apps, features) with structured rules.

See utils/structure/ modules for detailed validation logic.
"""

import sys

from features.config import Config
from features.validation.utils.structure_src_tree import validate_src_tree


def validate_structure(config: Config) -> int:
    """Run validation on all strict_format_roots and return exit code."""
    project_root = config.project_root
    strict_format_roots = config.structure.strict_format_roots
    all_errors: list[str] = []

    # Require at least one strict_format_root
    if not strict_format_roots:
        print("Error: strict_format_roots is empty. At least one root is required.")
        return 1

    validated_count = 0

    # Validate each strict_format_root
    for root_name in sorted(strict_format_roots):
        root_path = project_root / root_name
        if not root_path.exists():
            print(f"Warning: {root_name}/ not found, skipping")
            continue

        print(f"Validating {root_name}/ tree...")
        root_errors = validate_src_tree(root_path, config)
        # Make paths relative to project root for cleaner error messages
        root_errors = [
            error.replace(str(project_root) + "\\", "").replace(str(project_root) + "/", "")
            for error in root_errors
        ]
        all_errors.extend(root_errors)
        validated_count += 1

    # Report results
    if all_errors:
        print(f"\nFound {len(all_errors)} validation error(s):\n")
        for error in all_errors:
            print(f"  - {error}")
        return 1

    if validated_count == 0:
        print("Warning: No strict_format_roots directories found to validate")

    print("All folder structures are valid!")
    return 0


if __name__ == "__main__":
    from features.config import load_config

    config = load_config()
    sys.exit(validate_structure(config))
