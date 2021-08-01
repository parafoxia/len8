import argparse
import re

from .errors import InvalidFile, BadLines
from .checker import check


def handle_when_file(args):
    matches = re.match("^([~?\.\/\w].*)\/(\w+\.pyw?)$|^(\w+\.pyw?)$", args.path)
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


def main():
    parser = argparse.ArgumentParser(
        description=("a utility for keeping line lengths within PEP 8 standards"),
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
        action="extend",
        metavar="filepath",
        nargs=1,
        default=[".venv", "venv"],
        help="file to exclude from parsing (accepts 1 file per -x flag)",
    )
    parser.add_argument(
        "-l",
        "--length",
        help="increase acceptable line length to 99",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    if args.file:
        path, file = handle_when_file(args)
    else:
        path = args.path
        file = ""

    try:
        check(path, exclude=args.x, extend=args.length, file_=file)
    except BadLines as e:
        print(e)


if __name__ == "__main__":
    main()
