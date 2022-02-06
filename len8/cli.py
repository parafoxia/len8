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

import sys
import typing as t
from pathlib import Path

import click

from len8 import Checker, Config
from len8.errors import BadLines, ConfigurationError, InvalidPath


def _as_paths(value: str) -> t.Tuple[Path, ...]:
    if not value:
        return ()

    return tuple(Path(p) for p in value.split(","))


@click.command()
@click.version_option()
@click.argument("paths", type=Path, required=False, nargs=-1)
@click.option(
    "-x",
    "--exclude",
    type=_as_paths,
    default="",
    metavar="FILEPATH",
    help="Comma-separated list of files/dirs to exclude.",
)
@click.option(
    "-l",
    "--extend-length",
    count=True,
    help=(
        "Increase line length for code. Option is additive, and can be used "
        "up to 2 times (corresponding to 88 and 99; omit for 79)"
    ),
)
@click.option(
    "-c",
    "--code-length",
    type=int,
    metavar="CHARS",
    help="Custom line length for code. Overrides --extend-length if set.",
)
@click.option(
    "-d",
    "--docs-length",
    type=int,
    metavar="CHARS",
    help="Custom line length for comments and docstrings.",
)
@click.option(
    "--config",
    type=Path,
    metavar="PATH",
    default=Path("./pyproject.toml"),
    help="The path to the toml configuration file to use.",
)
def len8(
    paths: t.Tuple[Path, ...],
    exclude: t.Tuple[Path, ...],
    extend_length: int,
    code_length: t.Optional[int],
    docs_length: t.Optional[int],
    config: Path,
) -> None:
    cfg: t.Optional[Config] = None

    try:
        cfg = Config(config)

    except ConfigurationError as e:
        checker = Checker(
            exclude=exclude,
            extend=min(extend_length, 2),
            max_code_length=code_length,
            max_docs_length=docs_length,
            strict=True,
        )

    else:
        checker = Checker.from_config(cfg)
        checker.strict = True
        checker.extend = extend_length
        checker.set_lengths(code=code_length or -1, docs=docs_length or -1)

        if exclude:
            checker.exclude = list(exclude)

    try:
        if paths:
            checker.check(*paths)

        else:
            if cfg and cfg.include:
                checker.check(*cfg.include)

            else:
                print(f"Error: Missing argument 'PATHS...'.")
                sys.exit(1)

    except (BadLines, InvalidPath) as e:
        print(e)
        sys.exit(1)
