# Copyright (c) 2021-2022, Ethan Henderson, Jonxslays
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

import re
import typing as t
from pathlib import Path

import toml

from len8 import errors

TRIPLE_QUOTE_PATTERN = re.compile(r'[bfr]?"""[^.]')


class Config:
    """A ``len8`` configuration generated from a toml file."""

    __slots__: t.Sequence[str] = (
        "_code_length",
        "_docs_length",
        "_include",
        "_exclude",
        "_is_configured",
        "_strict",
    )

    def __init__(self, path: t.Union[str, Path]) -> None:
        self._include: t.Optional[t.List[str]] = None
        self._exclude: t.Optional[t.List[str]] = None
        self._code_length: t.Optional[int] = None
        self._docs_length: t.Optional[int] = None
        self._strict: bool = False
        self._is_configured: bool = False

        if not isinstance(path, Path):
            path = Path(path)

        if not path.is_file():
            raise errors.ConfigurationError(
                f"'{path}' is not a valid configuration file."
            )

        with open(path) as f:
            try:
                len8 = toml.loads(f.read())["tool"]["len8"]
            except toml.TomlDecodeError as e:
                raise errors.ConfigurationError(
                    f"Failed to parse configuration file\n{e}"
                ) from None
            except KeyError:
                return None

        self._include = len8.get("include")
        self._exclude = len8.get("exclude")
        self._code_length = len8.get("code-length")
        self._docs_length = len8.get("docs-length")
        self._strict = len8.get("strict", False)
        self._is_configured = True

    @property
    def include(self) -> t.Optional[t.List[str]]:
        """The optional paths to include in checking."""
        return self._include

    @property
    def exclude(self) -> t.Optional[t.List[str]]:
        """The optional paths to exclude from checking."""
        return self._exclude

    @property
    def code_length(self) -> t.Optional[int]:
        """The optional maximum length for code."""
        return self._code_length

    @property
    def docs_length(self) -> t.Optional[int]:
        """The optional maximum length for docs."""
        return self._docs_length

    @property
    def strict(self) -> bool:
        """If True, raises an error if the check method fails. Defaults
        to ``False`` for ``Config``.
        """
        return self._strict

    @property
    def is_configured(self) -> bool:
        """Whether or not this ``Config`` was successfully
        configured."""
        return self._is_configured


class Checker:
    """An object used to check line lengths.

    Keyword Args:
        exclude: ``list[pathlib.Path | str]``
            A list of paths on top of the defaults (.nox, .venv, and
            venv) to exclude from checking. Defaults to an empty list.
        extend: ``int``
            Increase the line length limit to set figures (pass ``1``
            to increase to 88, and ``2`` to increase to 99). This is
            designed to allow for an additive option in the CLI --
            consider using :obj:`max_code_length` and
            :obj:`max_docs_length` instead.
        max_code_length: ``int`` | ``None``
            Set the maximum length for code.
        max_docs_length: ``int`` | ``None``
            Set the maximum length for comments and documentation.
        strict: ``bool``
            If True, raises an error if the check method fails. Defaults
            to ``True``.
    """

    __slots__: t.Sequence[str] = (
        "_bad_lines",
        "_code_length",
        "_docs_length",
        "_exclude",
        "_extend",
        "_strict",
    )

    def __init__(
        self,
        *,
        exclude: t.Sequence[t.Union[Path, str]] = [],
        extend: int = 0,
        max_code_length: t.Optional[int] = None,
        max_docs_length: t.Optional[int] = None,
        strict: bool = False,
    ) -> None:
        def _ensure_path(value: t.Union[Path, str]) -> Path:
            if isinstance(value, Path):
                return value

            return Path(value)

        if not 0 <= extend <= 2:
            raise ValueError("'extend' should be between 0 and 2 inclusive")

        if max_code_length and max_code_length < 0:
            raise ValueError("line lengths cannot be less than 0")

        if max_docs_length and max_docs_length < 0:
            raise ValueError("line lengths cannot be less than 0")

        self._exclude = [_ensure_path(p) for p in exclude]
        self._extend = extend
        self._code_length = max_code_length
        self._docs_length = max_docs_length
        self._strict = strict
        self._bad_lines: t.List[t.Tuple[str, int, int, int]] = []

    @classmethod
    def from_config(cls, config: t.Union[str, Path, Config]) -> "Checker":
        """Generate a new ``Checker`` from a toml configuration file.

        Args:
            path: ``str`` | ``pathlib.Path`` | ``len8.Config``
                The path to the toml file to load configurations from,
                or the already loaded ``len8.Config`` object.

        Returns:
            ``len8.Checker``
        """
        if not isinstance(config, Config):
            config = Config(config)

        return cls(
            exclude=config.exclude or [],
            max_code_length=config.code_length,
            max_docs_length=config.docs_length,
            strict=config.strict,
        )

    @property
    def bad_lines(self) -> t.Union[str, None]:
        """A formatted string containing the lines that were too long
        during the last check, or ``None`` if there were none.

        Returns:
            ``str`` | ``None``
        """
        if not self._bad_lines:
            return None

        bl = ""

        for file, line, chars, limit in self._bad_lines:
            if file not in bl:
                bl += f"\33[1m{file}\33[0m\n"

            bl += f"  * Line {line} ({chars}/{limit})\n"

        bl += f"\n\33[1m\33[31mFound {len(self._bad_lines):,} problem(s)\33[0m"
        return bl

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
    def extend(self) -> int:
        """The extension factor.

        Returns:
            ``int``
        """
        return self._extend

    @extend.setter
    def extend(self, extend: int) -> None:
        if not 0 <= extend <= 2:
            raise ValueError("'extend' should be between 0 and 2 inclusive")
        self._extend = extend

    @property
    def code_length(self) -> int:
        """The value to use as the maximum line length for code. This
        will return:

        - The custom length, if one was set.
        - 79 if :obj:`extend` equals 0.
        - 88 if :obj:`extend` equals 1.
        - 99 if :obj:`extend` equals 2.
        """
        if self._code_length:
            return self._code_length

        return (79, 88, 99)[self._extend]

    @property
    def docs_length(self) -> int:
        """The value to use as the maximum line length for comments and
        documentation. This will return:

        - The custom length, if one was set.
        - 72 otherwise.
        """
        if self._docs_length:
            return self._docs_length

        return 72

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
        if path.is_file() and path.suffix not in (".py", ".pyw"):
            return False

        for e in self.exclude:
            if path.absolute() == e:
                return False

            if all(x in path.parts for x in e.parts):
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

        try:
            with open(path, encoding="utf-8") as f:
                for i, line in enumerate(f):
                    ls = line.lstrip()
                    rs = line.rstrip()

                    if in_license:
                        if ls.startswith("#"):
                            continue

                        in_license = False

                    if TRIPLE_QUOTE_PATTERN.match(ls):
                        in_docs = True

                    chars = len(rs)
                    limit: int = (
                        self.docs_length
                        if in_docs or ls.startswith("#")
                        else self.code_length
                    )

                    if chars > limit:
                        self._bad_lines.append(
                            (f"{path.resolve()}", i + 1, chars, limit)
                        )

                    if rs.endswith('"""'):
                        in_docs = False

        except (IsADirectoryError, PermissionError):
            # Handle weird directories.
            ...

    def set_lengths(
        self, *, code: t.Optional[int] = -1, docs: t.Optional[int] = -1
    ) -> None:
        """Set the maximum line lengths for code and documentation.

        Keyword Args:
            code: ``int`` | ``None``
                The length to set as the maximum line length for code.
                Passing ``None`` will reset the override, and passing
                a negative integer will preserve the previous value.
                Defaults to -1.
            docs: ``int`` | ``None``
                The length to set as the maximum line length for
                comments and documentation. Passing ``None`` will reset
                the override, and passing a negative integer will
                preserve the previous value. Defaults to -1.
        """
        if not code or code > 0:
            self._code_length = code

        if not docs or docs > 0:
            self._docs_length = docs

    def check(self, *paths: t.Union[Path, str]) -> t.Optional[str]:
        """Check to ensure the line lengths conform to PEP 8 standards.

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
        self._bad_lines = []

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
