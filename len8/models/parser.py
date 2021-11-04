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
import typing as t
from pathlib import Path


class Parser:
    """Parser used when len8 is invoked from the command line."""

    def __init__(self) -> None:
        self._parser = argparse.ArgumentParser(
            description=(
                "a utility for keeping line lengths within PEP 8 standards"
            ),
        )
        self._parse()

    @property
    def exclude(self) -> t.List[Path]:
        """The list of files/dirs to exclude.

        Returns:
            ``list[pathlib.Path]``
        """
        return t.cast(t.List[Path], self._args.exclude)

    @property
    def extend(self) -> bool:
        """Whether or not to increase acceptable line length to 99.

        Returns:
            ``bool``
        """
        return t.cast(bool, self._args.length)

    @property
    def paths(self) -> t.List[str]:
        """The list of paths to check.

        Returns:
            ``list[str]``
        """
        return t.cast(t.List[str], self._args.paths)

    def _as_paths(self, value: str) -> t.List[Path]:
        if not value:
            return []

        return [Path(p) for p in value.split(",")]

    def _parse(self) -> None:
        self._parser.add_argument("paths", type=Path, nargs="+")
        self._parser.add_argument(
            "-x",
            "--exclude",
            help="comma separated list of files/dirs to exclude",
            metavar="filepath",
            default="",
            type=self._as_paths,
        )
        self._parser.add_argument(
            "-l",
            "--length",
            help="increase acceptable line length to 99",
            default=False,
            action="store_true",
        )
        self._args = self._parser.parse_args()
