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

from .errors import BadLines, InvalidFile


def check(path, exclude=[], extend=False, file_=""):
    bad_lines = []
    checked = False

    for subdir, _, files in os.walk(path):
        if not any(e for e in exclude if e in subdir):
            for file in filter(
                lambda f: f.endswith(file_ if file_ else (".py", ".pyw"))
                and (subdir == path if file_ else True)
                and f not in exclude,
                files,
            ):
                if not checked:
                    checked = True

                bad_lines = validate_file(subdir, file, extend, bad_lines)

    if bad_lines:
        raise BadLines(
            ("%d line(s) are too long:\n" % len(bad_lines))
            + "\n".join(
                "- %s, line %d (%d/%d)" % (file, line, chars, limit)
                for file, line, chars, limit in bad_lines
            )
        )

    if not checked and file_:
        raise InvalidFile("/".join((path, file_)))

    return True


def validate_file(subdir, file, extend, bad_lines):
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

        limit = 72 if in_docs or ls.startswith("#") else (99 if extend else 79)
        chars = len(rs)
        if chars > limit:
            bad_lines.append(("%s/%s" % (subdir, file), i + 1, chars, limit))

        if rs.endswith('"""'):
            in_docs = False

    io.close()

    return bad_lines
