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

import os
import typing as t

from len8 import errors


class Checker:
    """An object used to check line lengths.

    Args:
        exclude: list[str]
            A list of paths to exclude from checking. Defaults to
            [".nox", ".venv", "venv"].
        extend: bool
            Whether or not to increase acceptable line length to 99.
            Defaults to False.
        strict: bool
            If True, raises an error if the check method fails. Defaults
            to True.
    """

    def __init__(
        self,
        exclude: t.List[str] = [".nox", ".venv", "venv"],
        extend: bool = False,
        strict: bool = True,
    ) -> None:
        self._exclude = exclude
        self._extend = extend
        self._strict = strict
        self._bad_lines: t.List[
            t.Tuple[str, int, int, t.Literal[72, 79, 99]]
        ] = []

    @property
    def bad_lines(self) -> t.Union[str, None]:
        """A formatted string containing the lines that were too long
        during the last check, or None if there were none.
        """
        if not self._bad_lines:
            return

        return f"{len(self._bad_lines)} line(s) are too long:\n" + "\n".join(
            f"- {file}, line {line} ({chars}/{limit})"
            for file, line, chars, limit in self._bad_lines
        )

    @property
    def exclude(self) -> t.List[str]:
        """A list of paths to exclude from checking."""
        return self._exclude

    @property
    def extend(self) -> bool:
        """If True, increase acceptable line length to 99."""
        return self._extend

    @property
    def strict(self) -> bool:
        """If True, raises an error if the check method fails for any
        reason.
        """
        return self._strict

    def check(self, *paths: str) -> t.Optional[str]:
        """Checks to ensure line lengths conform to PEP 8 standards.

        Args:
            *paths: str
                The path or paths to check.

        Raises:
            len8.InvalidPath:
                If strict mode is set to True and the given path does
                not exist.
            len8.BadLines:
                If strict mode is set to True and the files that were
                checked contained lines that were too long.

        Returns:
            str | None:
                A formatted string containing the lines that were too
                long, or None if there were none.
        """
        for p in paths:
            if not os.path.exists(p) and self.strict:
                raise errors.InvalidPath(p)

            if os.path.isfile(p):
                self._check_file(p)
            else:
                self._check_dir(p)

        if self._bad_lines and self.strict:
            raise errors.BadLines(self.bad_lines)

        return self.bad_lines

    def _check(self, subdir: str, file: str) -> None:
        io = open(f"{subdir}/{file}")
        in_docs = False
        in_license = True

        for i, line in enumerate(io):
            ls = line.lstrip()
            rs = line.rstrip()

            if in_license:
                if ls.startswith("#"):
                    continue

                in_license = False

            if ls.startswith(('"""', 'r"""')):
                in_docs = True

            chars = len(rs)
            limit = (
                72
                if in_docs or ls.startswith("#")
                else (99 if self.extend else 79)
            )

            if chars > limit:
                self._bad_lines.append(
                    (f"{os.path.abspath(subdir)}/{file}", i + 1, chars, limit)
                )

            if rs.endswith('"""'):
                in_docs = False

        io.close()

    def _check_dir(self, path: str) -> None:
        for subdir, _, files in os.walk(path):
            for file in filter(
                lambda f: self._filter(os.path.abspath(subdir), f, path), files
            ):
                self._check(subdir, file)

    def _check_file(self, path: str) -> None:
        subdir, file = self._split_path(path)

        if self._filter(subdir, file, path):
            self._check(subdir, file)

    def _filter(self, subdir: str, file: str, path: str) -> bool:
        if not file.endswith((".py", ".pyw")):
            return False

        for e in self.exclude:
            e_subdir, e_file = self._split_path(e)

            if f"{e_subdir}/{e_file}" in subdir:
                return False

            if f"{path}/{e_file}" in subdir:
                return False

            if (subdir, file) == (e_subdir, e_file):
                return False

        return True

    def _split_path(self, path: str) -> t.Tuple[str, str]:
        return os.path.split(os.path.abspath(path))
