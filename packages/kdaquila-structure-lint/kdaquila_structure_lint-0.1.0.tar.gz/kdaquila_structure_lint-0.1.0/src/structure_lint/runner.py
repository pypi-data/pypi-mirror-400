"""Main orchestrator that runs enabled validators."""

from structure_lint.config import Config
from structure_lint.validators.structure import validate_structure
from structure_lint.validators.line_limits import validate_line_limits
from structure_lint.validators.one_per_file import validate_one_per_file


def run_validations(config: Config, verbose: bool = False) -> int:
    """Run all enabled validators and return combined exit code.

    Strategy: Run ALL enabled validators (don't stop on first failure),
    then aggregate results. This shows users all issues at once.

    Args:
        config: Configuration object
        verbose: Enable verbose output

    Returns:
        0 if all pass, 1 if any fail
    """
    if not config.enabled:
        print("ℹ️  structure-lint is disabled in configuration")
        return 0

    results = []

    # Run structure validation if enabled
    if config.validators.structure:
        if verbose:
            print(f"📁 Project root: {config.project_root}")
        print("=" * 60)
        print("Running structure validation...")
        print("=" * 60)
        results.append(validate_structure(config))

    # Run line limits validation if enabled
    if config.validators.line_limits:
        print("\n" + "=" * 60)
        print("Running line limit validation...")
        print("=" * 60)
        results.append(validate_line_limits(config))

    # Run one-per-file validation if enabled
    if config.validators.one_per_file:
        print("\n" + "=" * 60)
        print("Running one-per-file validation...")
        print("=" * 60)
        results.append(validate_one_per_file(config))

    # Check if any validators ran
    if not results:
        print("⚠️  Warning: No validators are enabled")
        print("💡 Enable validators in pyproject.toml [tool.structure-lint.validators]")
        return 0

    # Report overall results
    if all(r == 0 for r in results):
        print("\n" + "=" * 60)
        print("✓ All validations passed!")
        print("=" * 60)
        return 0
    else:
        print("\n" + "=" * 60)
        print("✗ Some validations failed")
        print("=" * 60)
        return 1
