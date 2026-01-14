import ast
from pathlib import Path
from collections import defaultdict
from typing import List


def extract_functions(file_path: str) -> List[str]:
    """Return a list of function and method names from a Python file."""
    functions = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except (SyntaxError, FileNotFoundError):
        return functions

    for node in ast.walk(tree):
        if isinstance(node, ast.FunctionDef):
            functions.append(node.name)
        elif isinstance(node, ast.AsyncFunctionDef):
            functions.append(node.name)
    return functions


def compare_functions(dir1: str, dir2: str, rel_files: List[str]) -> None:
    functions_in_dir1 = defaultdict(list)
    functions_in_dir2 = defaultdict(list)

    for rel in rel_files:
        file1 = str(Path(dir1) / rel)
        file2 = str(Path(dir2) / rel)

        funcs1 = extract_functions(file1)
        funcs2 = extract_functions(file2)

        for fn in funcs1:
            functions_in_dir1[fn].append(rel)
        for fn in funcs2:
            functions_in_dir2[fn].append(rel)

        common_set = set(funcs1) & set(funcs2)
        if common_set:
            print(f"\n[{rel}]")
            print("  Common functions/methods:")
            for fn in sorted(common_set):
                count1 = funcs1.count(fn)
                count2 = funcs2.count(fn)
                if count1 > 1 or count2 > 1:
                    print(f"    - {fn} (appears {count1} times in dir1, "
                          f"{count2} times in dir2)")
                else:
                    print(f"    - {fn}")
        else:
            print(f"No functions in common between {dir1} and {dir2} in {rel}")

    # cross-file check: moved functions
    moved = []
    for fn in set(functions_in_dir1.keys()) | set(functions_in_dir2.keys()):
        files1 = set(functions_in_dir1.get(fn, []))
        files2 = set(functions_in_dir2.get(fn, []))
        if files2 and files1 and files1 != files2:
            intersection = files1 & files2
            if not intersection:
                moved.append((fn, files1, files2))

    if moved:
        print("\nFunctions/methods that appear to have moved:")
        for fn, f1, f2 in moved:
            count1 = len(functions_in_dir1[fn])
            count2 = len(functions_in_dir2[fn])
            if count1 > 1 or count2 > 1:
                print(f"  {fn} (appears {count1} times in dir1, "
                      f"{count2} times in dir2): {f1} -> {f2}")
            else:
                print(f"  {fn}: {f1} -> {f2}")
    else:
        print("No functions moved to a different file")


def validate_inputs(files: List[Path]) -> bool:
    """Validate command line inputs for compare_funcs."""
    if len(files) < 3:
        print("Usage: inspectr compare_funcs <files_list.txt> <dir1> <dir2>")
        print("  files_list.txt: text file containing relative paths to "
              "compare, one per line")
        print("  dir1: first directory")
        print("  dir2: second directory")
        return False

    files_list_path = files[0]
    dir1 = files[1]
    dir2 = files[2]

    if not files_list_path.exists():
        print(f"Error: File list does not exist: {files_list_path}")
        return False

    if not files_list_path.is_file():
        print(f"Error: Not a file: {files_list_path}")
        return False

    if not dir1.exists():
        print(f"Error: Directory does not exist: {dir1}")
        return False

    if not dir1.is_dir():
        print(f"Error: Not a directory: {dir1}")
        return False

    if not dir2.exists():
        print(f"Error: Directory does not exist: {dir2}")
        return False

    if not dir2.is_dir():
        print(f"Error: Not a directory: {dir2}")
        return False

    return True


def main(files: List[Path], **kwargs) -> None:
    if not validate_inputs(files):
        return

    files_list_path = files[0]
    dir1 = files[1]
    dir2 = files[2]

    with open(files_list_path, "r", encoding="utf-8") as f:
        rel_files = [line.rstrip("\n") for line in f if line.strip()]

    compare_functions(str(dir1), str(dir2), rel_files)
