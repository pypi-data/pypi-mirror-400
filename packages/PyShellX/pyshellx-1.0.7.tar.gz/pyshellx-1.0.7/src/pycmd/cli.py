#!/usr/bin/env python
import os
from pathlib import Path
import sys
import argparse


__version__ = "1.0.0"
__file_dir__ = os.path.dirname(os.path.abspath(__file__))


def execute_file(
    filepath: str,
    verbose: bool = False,
    silent: bool = False,
    dry_run: bool = False,
    custom_args: dict = None,
):
    if not os.path.exists(filepath):
        if not silent:
            print(f"Error: File {filepath} not found")
        sys.exit(1)

    if verbose and not silent:
        print(f"Executing file: {filepath}")

    if dry_run and not silent:
        print(f"Dry run mode - would execute: {filepath}")
        return

    global_vars = {
        "__name__": "__main__",
        "__file__": filepath,
        "VERBOSE": verbose,
        "SILENT": silent,
        "DRY_RUN": dry_run,
        "ARGS": custom_args or {},
    }

    # print(f" open : {filepath}")
    fil = Path(str(filepath))

    with open(filepath, "r", encoding="utf-8") as f:
        code = f.read()

    try:
        exec(code, global_vars)
    except Exception as e:
        if not silent:
            print(f"Error executing {filepath}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        prog="pycmd",
        description="A SCons-like build tool for executing Python command files",
        epilog="Example: pycmd -f Command.py --target=release --config=debug",
        allow_abbrev=False,
    )

    parser.add_argument(
        "-f",
        "--file",
        default="Command.py",
        help="Specify the command file to execute (default: Command.py)",
    )

    parser.add_argument(
        "-s",
        "--silent",
        action="store_true",
        help="Silent mode - suppress all output except errors",
    )

    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose mode - show detailed execution information",
    )

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Dry run mode - show what would be executed without actually running",
    )

    parser.add_argument(
        "-i",
        "--internal",
        # action="store_true",
        help="interanl file for run, such as powershell_test.py, cmd_test.py, install_wsl.py",
    )

    # parser.add_argument(
    #     "--linux",
    #     action="store_true",
    #     help="interanl file for run, such as vscode.py vscode_server.py",
    # )

    parser.add_argument(
        "-v", "-V", "--version", action="version", version=f"pycmd {__version__}"
    )

    args, unknown = parser.parse_known_args()

    custom_args = {}
    for arg in unknown:
        if arg.startswith("--"):
            if "=" in arg:
                key, value = arg[2:].split("=", 1)
                custom_args[key] = value
            else:
                custom_args[arg[2:]] = True
        elif arg.startswith("-"):
            custom_args[arg[1:]] = True
        else:
            if "positional" not in custom_args:
                custom_args["positional"] = []
            custom_args["positional"].append(arg)

    if args.internal:
        internal_file = (
            args.internal if args.internal.endswith(".py") else f"{args.internal}.py"
        )

        if "/" in internal_file or "\\" in internal_file:
            relative_path = internal_file
        else:
            platform_type = "windows" if os.name.lower() == "nt" else "linux"
            relative_path = os.path.join(platform_type, internal_file)

        package_root = os.path.join(__file_dir__)
        package_internal = os.path.join(package_root, relative_path)
        package_internal = os.path.abspath(package_internal)

        entry_point_root = os.path.abspath(os.path.dirname(sys.argv[0]))
        entry_internal = os.path.join(entry_point_root, relative_path)
        entry_internal = os.path.abspath(entry_internal)

        p_root = os.path.join(__file_dir__)

        if os.path.exists(entry_internal):
            args.file = entry_internal
        elif os.path.exists(package_internal):
            args.file = package_internal
        else:
            args.file = relative_path

        if not args.silent:
            print(f"Executing internal file: {args.file}")
    else:
        args.file = args.file if args.file.endswith(".py") else f"{args.file}.py"

    execute_file(
        args.file,
        # str(os.path.abspath(args.file)),
        verbose=args.verbose,
        silent=args.silent,
        dry_run=args.dry_run,
        custom_args=custom_args,
    )


if __name__ == "__main__":
    main()
