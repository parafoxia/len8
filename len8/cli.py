import argparse
import os
import re
import sys

from .errors import InvalidFile, BadLines
from len8 import check


def main():
    parser = argparse.ArgumentParser(
        description=(
            "a utility for keeping line lengths within PEP 8 standards"
        ),
    )

    parser.add_argument("path")
    parser.add_argument(
        "-f", "--file", help="parse only a single file.", default=False,
        action="store_true",
    )
    parser.add_argument(
        "-x", action="extend", metavar="filepath",
        nargs=1, default=[".venv", "venv"],
        help="file to exclude from parsing (accepts 1 file per -x flag)",
    )
    parser.add_argument(
        "-l", "--length", help="increase acceptable line length to 99",
        default=False, action="store_true",
    )

    args = parser.parse_args()

    if args.file:
        matches = re.match(
            "^([\.\/\w].*\/?.*)\/(\w+\.pyw?)|(\w+\.pyw?)$", args.path
        )

        if not matches:
            return print(InvalidFile(args.path))

        groups = matches.groups()
        print(groups)

        if groups[2]:
            exclude = os.listdir(".")
            exclude.remove(groups[2])
            args.x.extend(exclude)
            args.path = os.curdir

        else:
            try:
                exclude = os.listdir(groups[0])
                exclude.remove(groups[1])
                args.x.extend(exclude)
                args.path = groups[0]
                print(args.x)
            except FileNotFoundError as e:
                return print(e)

            print("args path", args.path)

    else:
        pass
        # TODO continue on this line.
        # something is still buggy with the file paths though.



    try:
        check(args.path, exclude=args.x, extend=args.length)
    except BadLines as e:
        print(e)


if __name__ == "__main__":
    main()
