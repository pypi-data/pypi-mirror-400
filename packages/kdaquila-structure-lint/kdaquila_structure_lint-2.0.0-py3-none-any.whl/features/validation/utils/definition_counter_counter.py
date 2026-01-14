"""Count top-level definitions in Python files."""

import ast
from pathlib import Path


def count_top_level_definitions(file_path: Path) -> tuple[int, list[str]] | None:
    """Count top-level functions and classes. Returns (count, names) or None on error."""
    try:
        with file_path.open(encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=str(file_path))
    except (OSError, SyntaxError, UnicodeDecodeError):
        return None

    definitions = []
    for node in ast.iter_child_nodes(tree):
        if isinstance(node, ast.FunctionDef | ast.AsyncFunctionDef | ast.ClassDef):
            definitions.append(node.name)

    return len(definitions), definitions
