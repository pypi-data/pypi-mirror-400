import ast
import pathlib
import sys
from typing import List


def validate_inputs(files: List[pathlib.Path]) -> bool:
    """Validate that files list is not empty and all files exist."""
    if not files:
        print("Usage: inspectr with_open <file1> [file2 ...]")
        return False

    for f in files:
        if not f.exists():
            print(f"Error: File does not exist: {f}")
            return False
        if not f.is_file():
            print(f"Error: Not a file: {f}")
            return False
    return True


def main(files: List[pathlib.Path], **kwargs) -> None:
    if not validate_inputs(files):
        sys.exit(1)

    for filepath in files:
        tree = ast.parse(filepath.read_text(), filename=str(filepath))
        for node in ast.walk(tree):
            if (
                isinstance(node, ast.Call)
                and getattr(node.func, "id", "") == "open"
            ):
                is_in_with = any(
                    isinstance(p, ast.With) and node in ast.walk(p)
                    for p in ast.walk(tree)
                )
                if not is_in_with:
                    print(f"{filepath}:{node.lineno}: open() outside with")
