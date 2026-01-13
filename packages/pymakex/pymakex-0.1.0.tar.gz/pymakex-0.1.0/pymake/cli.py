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
        description="A Python compiler for building MCU firmware",
        epilog="Example: pymake -f Makefile.py --target=release --config=debug",
        allow_abbrev=False,
    )

    parser.add_argument(
        "-f",
        "--file",
        default="Makefile.py",
        help="Specify the command file to execute (default: Makefile.py)",
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
        "-v", "-V", "--version", action="version", version=f"pymakex {__version__}"
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
