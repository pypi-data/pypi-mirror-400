import sys
import pathlib
import importlib


def validate_subtool(subtool: str):
    """Validate and load the subtool module. Returns module or None on failure."""
    try:
        mod = importlib.import_module(f"inspectr.{subtool}")
    except ModuleNotFoundError:
        print(f"Unknown subtool: {subtool}")
        return None

    if not hasattr(mod, "main"):
        print(f"Subtool '{subtool}' does not define a main(args) function")
        return None

    return mod


def main():
    if len(sys.argv) < 2:
        print("Usage: inspectr <subtool> [options] [files...]")
        sys.exit(1)

    subtool = sys.argv[1]
    remaining_args = sys.argv[2:]

    mod = validate_subtool(subtool)
    if mod is None:
        sys.exit(1)

    files = []
    kwargs = {}
    
    # convert --option style options into keyword arguments
    i = 0
    while i < len(remaining_args):
        arg = remaining_args[i]
        if arg.startswith("--"):
            option_name = arg[2:].replace("-", "_")
            has_value = (
                i + 1 < len(remaining_args)
                and not remaining_args[i + 1].startswith("--")
            )
            if has_value:
                value = remaining_args[i + 1]
                try:
                    kwargs[option_name] = int(value)
                except ValueError:
                    kwargs[option_name] = value
                i += 2
            else:
                kwargs[option_name] = True
                i += 1
        else:
            files.append(pathlib.Path(arg))
            i += 1
    
    mod.main(files, **kwargs)


if __name__ == "__main__":
    main()
