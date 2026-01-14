"""Command-line interface for structure-lint."""

import argparse
import sys
from pathlib import Path

from structure_lint import __version__
from structure_lint.config import load_config
from structure_lint.runner import run_validations


def main(argv: list[str] | None = None) -> int:
    """Main CLI entry point.

    Args:
        argv: Command-line arguments (uses sys.argv if None, for testability)

    Returns:
        Exit code (0 = success, 1 = validation failed, 2 = config error)
    """
    # Ensure UTF-8 encoding for stdout/stderr on Windows
    if sys.platform == "win32":
        try:
            sys.stdout.reconfigure(encoding="utf-8")  # type: ignore
            sys.stderr.reconfigure(encoding="utf-8")  # type: ignore
        except Exception:
            # If reconfigure fails, continue with default encoding
            pass

    parser = argparse.ArgumentParser(
        prog="structure-lint",
        description="Opinionated Python project structure and code quality linter",
    )
    parser.add_argument(
        "--project-root",
        type=Path,
        help="Path to project root (default: auto-detect from pyproject.toml)",
    )
    parser.add_argument(
        "--config",
        type=Path,
        help="Path to pyproject.toml (default: search from current directory)",
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )

    args = parser.parse_args(argv)

    try:
        # Load configuration
        config = load_config(
            project_root=args.project_root,
            config_path=args.config
        )

        # Run validations
        exit_code = run_validations(config, verbose=args.verbose)
        return exit_code

    except FileNotFoundError as e:
        print(f"❌ Error: {e}", file=sys.stderr)
        return 2
    except Exception as e:
        print(f"❌ Unexpected error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 2


if __name__ == "__main__":
    sys.exit(main())
