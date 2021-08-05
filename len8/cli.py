import argparse
import re

from .errors import InvalidFile, BadLines
from .checker import check


def handle_when_file(args):
    matches = re.match(
        "^([~?\.\/\w].*)\/(\w+\.pyw?)$|^(\w+\.pyw?)$", args.path
    )

    if not matches:
        return InvalidFile(args.path)

    groups = matches.groups()

    if groups[2]:
        args.path = "."
        file = groups[2]

    else:
        args.path = groups[0]
        file = groups[1]

    return args.path, file


def gather_excludes(e):
    excludes = [".venv", "venv"]
    excludes.extend(e.split(","))
    return excludes


def main():
    parser = argparse.ArgumentParser(
        description=(
            "a utility for keeping line lengths within PEP 8 standards"
        ),
    )
    parser.add_argument("path")
    parser.add_argument(
        "-f",
        "--file",
        help="parse only files with a certain name.",
        default=False,
        action="store_true",
    )
    parser.add_argument(
        "-x",
        metavar="filepath",
        type=gather_excludes,
        nargs=1,
        default=[".venv", "venv"],
        help="comma separated list of files/dirs to exclude",
    )
    parser.add_argument(
        "-l",
        "--length",
        help="increase acceptable line length to 99",
        default=False,
        action="store_true",
    )

    args = parser.parse_args()

    if len(args.x) == 1:
        args.x = args.x[0]

    if args.file:
        handler = handle_when_file(args)

        if isinstance(handler, InvalidFile):
            return handler

        path, file = handler

    else:
        path = args.path
        file = ""

    try:
        check(path, exclude=args.x, extend=args.length, file_=file)
    except (BadLines, InvalidFile) as e:
        print(e)


if __name__ == "__main__":
    main()
