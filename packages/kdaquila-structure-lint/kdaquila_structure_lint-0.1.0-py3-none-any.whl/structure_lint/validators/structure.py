"""Validates project folder structure conventions with support for multiple trees.

Trees:
- src tree: Has base_folders (apps, features) with structured rules
- scripts tree: Free-form custom folders with limited nesting

See utils/structure/ modules for detailed validation logic.
"""


from structure_lint.config import Config
from structure_lint.utils.structure.scripts_tree import validate_scripts_tree
from structure_lint.utils.structure.src_tree import validate_src_tree


def validate_structure(config: Config) -> int:
    """Run validation on all trees and return exit code."""
    project_root = config.project_root
    src_root = config.structure.src_root
    scripts_root = config.structure.scripts_root
    all_errors: list[str] = []

    # Validate src tree
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

    # Validate scripts tree
    scripts_path = project_root / scripts_root
    if scripts_path.exists():
        print(f"🔍 Validating {scripts_root}/ tree...")
        scripts_errors = validate_scripts_tree(scripts_path, config)
        # Make paths relative to project root for cleaner error messages
        scripts_errors = [
            error.replace(str(project_root) + "\\", "").replace(str(project_root) + "/", "")
            for error in scripts_errors
        ]
        all_errors.extend(scripts_errors)

    # Report results
    if all_errors:
        print(f"\n❌ Found {len(all_errors)} validation error(s):\n")
        for error in all_errors:
            print(f"  • {error}")
        return 1
    else:
        print("✅ All folder structures are valid!")
        return 0


if __name__ == "__main__":
    from structure_lint.config import load_config
    config = load_config()
    exit(validate_structure(config))
