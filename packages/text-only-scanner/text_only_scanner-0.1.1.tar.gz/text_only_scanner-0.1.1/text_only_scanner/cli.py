import argparse
import sys
import os
from .detector import filter_text_files


def _expand_paths(paths, recursive: bool):
    files = []
    for p in paths:
        if os.path.isdir(p):
            if recursive:
                for dirpath, _, filenames in os.walk(p):
                    for fn in filenames:
                        files.append(os.path.join(dirpath, fn))
            else:
                print(f"Directory given but --recursive not set: {p}", file=sys.stderr)
                raise SystemExit(2)
        elif os.path.isfile(p):
            files.append(p)
        else:
            print(f"Path not found: {p}", file=sys.stderr)
            raise SystemExit(2)
    return files


def main(argv=None) -> int:
    argv = argv if argv is not None else sys.argv[1:]
    parser = argparse.ArgumentParser(description="Reject files that are not plain text.")
    parser.add_argument("paths", nargs="+", help="Files or directories to check")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recurse into directories")
    args = parser.parse_args(argv)

    paths = _expand_paths(args.paths, args.recursive)

    accepted, rejected = filter_text_files(paths)

    for a in accepted:
        print(a)

    if rejected:
        print("\nRejected files:", file=sys.stderr)
        for r in rejected:
            print(r, file=sys.stderr)
        return 2

    return 0


if __name__ == "__main__":
    raise SystemExit(main())


def cli_entry():
    """Entry point for console_scripts; exits with the main return code."""
    raise SystemExit(main())
