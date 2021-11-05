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

import typing as t
from pathlib import Path

from len8 import errors


class Checker:
    """An object used to check line lengths.

    Keyword Args:
        exclude: list[pathlib.Path | str]
            A list of paths on top of the defaults (.nox, .venv, and
            venv) to exclude from checking. Defaults to an empty list.
        extend: bool
            Whether or not to increase acceptable line length to 99.
            Defaults to ``False``.
        strict: bool
            If True, raises an error if the check method fails. Defaults
            to ``True``.
    """

    def __init__(
        self,
        *,
        exclude: t.Sequence[t.Union[Path, str]] = [],
        extend: bool = False,
        strict: bool = False,
    ) -> None:
        def _ensure_path(value: t.Union[Path, str]) -> Path:
            if isinstance(value, Path):
                return value

            return Path(value)

        self._exclude = [_ensure_path(p) for p in exclude]
        self._extend = extend
        self._strict = strict
        self._bad_lines: t.List[
            t.Tuple[str, int, int, t.Literal[72, 79, 99]]
        ] = []

    @property
    def bad_lines(self) -> t.Union[str, None]:
        """A formatted string containing the lines that were too long
        during the last check, or ``None`` if there were none.

        Returns:
            ``str`` | ``None``
        """
        if not self._bad_lines:
            return None

        return f"{len(self._bad_lines)} line(s) are too long:\n" + "\n".join(
            f"- {file}, line {line} ({chars}/{limit})"
            for file, line, chars, limit in self._bad_lines
        )

    @property
    def exclude(self) -> t.List[Path]:
        """A list of paths to exclude from checking.

        Returns:
            ``list[pathlib.Path]``
        """
        return [Path(".nox"), Path(".venv"), Path("venv"), *self._exclude]

    @exclude.setter
    def exclude(self, excludes: t.List[Path]) -> None:
        self._exclude = excludes

    @property
    def extend(self) -> bool:
        """If ``True``, increase acceptable line length to 99.

        Returns:
            ``bool``
        """
        return self._extend

    @extend.setter
    def extend(self, extend: bool) -> None:
        self._extend = extend

    @property
    def strict(self) -> bool:
        """If ``True``, raises an error if the check method fails for
        any reason.

        Returns:
            ``bool``
        """
        return self._strict

    @strict.setter
    def strict(self, strict: bool) -> None:
        self._strict = strict

    def _is_valid(self, path: Path) -> bool:
        if path.suffix not in (".py", ".pyw"):
            return False

        for e in self.exclude:
            if path.absolute() == e:
                return False

            if path.is_relative_to(e):
                return False

        return True

    def _check_file(self, path: Path) -> None:
        if self._is_valid(path):
            self._check(path)

    def _check_dir(self, path: Path) -> None:
        for p in path.rglob("*.*"):
            self._check_file(p)

    def _check(self, path: Path) -> None:
        in_docs = False
        in_license = True

        with open(path) as f:
            for i, line in enumerate(f):
                ls = line.lstrip()
                rs = line.rstrip()

                if in_license:
                    if ls.startswith("#"):
                        continue

                    in_license = False

                if ls.startswith(('"""', 'r"""')):
                    in_docs = True

                chars = len(rs)
                limit: t.Literal[72, 79, 99] = (
                    72
                    if in_docs or ls.startswith("#")
                    else (99 if self.extend else 79)
                )

                if chars > limit:
                    self._bad_lines.append(
                        (f"{path.resolve()}", i + 1, chars, limit)
                    )

                if rs.endswith('"""'):
                    in_docs = False

    def check(self, *paths: t.Union[Path, str]) -> t.Optional[str]:
        """Checks to ensure the line lengths conform to PEP 8 standards.

        Args:
            *paths: ``Path`` | ``str``
                The path or paths to check.

        Returns:
            ``str`` | ``None``
                A formatted string containing the lines that were too
                long, or ``None`` if there were none.

        Raises:
            :obj:`InvalidPath`:
                If strict mode is set to ``True`` and the given path
                does not exist.
            :obj:`BadLines`:
                If strict mode is set to ``True`` and the files that
                were checked contained lines what were too long.
        """
        for p in paths:
            if not isinstance(p, Path):
                p = Path(p)

            if not p.exists() and self.strict:
                raise errors.InvalidPath(p)

            if p.is_file():
                self._check_file(p)
            else:
                self._check_dir(p)

        if self._bad_lines and self.strict:
            raise errors.BadLines(self.bad_lines)

        return self.bad_lines
