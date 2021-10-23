# Copyright (c) 2021, Ethan Henderson, Jonxslays
# All rights reserved.
#
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
#    list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
#    this list of conditions and the following disclaimer in the documentation
#    and/or other materials provided with the distribution.
#
# 3. Neither the name of the copyright holder nor the names of its
#    contributors may be used to endorse or promote products derived from
#    this software without specific prior written permission.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
# AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
# CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
# OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
# OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

import argparse
import re
import sys

from len8 import Checker, BadLines, InvalidPath


def gather_excludes(e):
    excludes = [".venv", "venv", ".nox"]
    excludes.extend(e.split(","))
    return excludes


def main():
    parser = argparse.ArgumentParser(
        description=(
            "a utility for keeping line lengths within PEP 8 standards"
        ),
    )
    parser.add_argument("path", nargs="+")
    parser.add_argument(
        "-x",
        "--exclude",
        metavar="filepath",
        type=gather_excludes,
        nargs=1,
        default=[".venv", "venv", ".nox"],
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

    if len(args.exclude) == 1:
        args.exclude = args.exclude[0]

    try:
        checker = Checker(exclude=args.exclude, extend=args.length)
        checker.check(args.path)

    except (InvalidPath, BadLines) as e:
        print(e)
        sys.exit(1)


if __name__ == "__main__":
    main()
