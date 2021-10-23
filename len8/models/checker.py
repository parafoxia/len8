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
        exclude=[".nox", ".venv", "venv"],
        extend=False,
        strict=True
    ):
        self._bad_lines = []
        self._exclude = exclude
        self._extend = extend
        self._strict = strict

    @property
    def bad_lines(self):
        """A formatted string containing the lines that were too long
        during the last check, or None if there were none.
        """
        if not self._bad_lines:
            return

        return (
            "%d line(s) are too long:\n" % len(self._bad_lines)
        ) + "\n".join(
            "- %s, line %d (%d/%d)" % (file, line, chars, limit)
            for file, line, chars, limit in self._bad_lines
        )

    @property
    def exclude(self):
        """A list of paths to exclude from checking."""
        return self._exclude

    @property
    def extend(self):
        """If True, increase acceptable line length to 99."""
        return self._extend

    @property
    def strict(self):
        """If True, raises an error if the check method fails for any
        reason.
        """
        return self._strict

    def check(self, *path):
        """Checks to ensure line lengths conform to PEP 8 standards.

        Args:
            path: str
                The path or paths to check. This arg is greedy.

        Raises:
            len8.InvalidPath:
                If the given path does not exist. Can be disabled by
                setting strict mode to False.

        Returns:
            str | None:
                A formatted string containing the lines that were too
                long, or None if there were none.
        """
        for p in path:
            if not os.path.exists(p) and self.strict:
                raise errors.InvalidPath(p)

            if os.path.isfile(p):
                self._check_file(p)
            else:
                self._check_dir(p)

        if self._bad_lines and self.strict:
            raise errors.BadLines(self.bad_lines)

        return self.bad_lines

    def _check(self, subdir, file):
        io = open("%s/%s" % (subdir, file))
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
                    (
                        "%s/%s" % (os.path.abspath(subdir), file),
                        i + 1,
                        chars,
                        limit,
                    )
                )

            if rs.endswith('"""'):
                in_docs = False

        io.close()

    def _check_dir(self, path):
        for subdir, _, files in os.walk(path):
            for file in filter(
                lambda f: self._filter(os.path.abspath(subdir), f), files
            ):
                self._check(subdir, file)

    def _check_file(self, path):
        subdir, file = self._split_path(path)

        if self._filter(subdir, file):
            self._check(subdir, file)

    def _filter(self, subdir, file):
        if not file.endswith((".py", ".pyw")):
            return False

        for e in self.exclude:
            e_subdir, e_file = self._split_path(e)

            if subdir.startswith(e_subdir) and e_file in subdir:
                return False

            if (subdir, file) == (e_subdir, e_file):
                return False

        return True

    def _split_path(self, path):
        return os.path.split(os.path.abspath(path))
