import os

from .errors import BadLines


def check(path, exclude=[], extend=False):
    bad_lines = []
    in_docs = False

    for subdir, _, files in os.walk(path):
        if not any((e for e in exclude if e in subdir)):
            for file in filter(
                    lambda f: f.endswith(
                        (".py", ".pyw")
                    ) and f not in exclude, files
            ):
                io = open("%s/%s" % (subdir, file))

                for i, line in enumerate(io):
                    ls = line.lstrip()
                    rs = line.rstrip()

                    if ls.startswith('"""'):
                        in_docs = True

                    limit = 72 if in_docs or ls.startswith("#") else (
                        99 if extend else 79
                    )
                    chars = len(rs)
                    if chars > limit:
                        bad_lines.append(
                            ("%s/%s" % (subdir, file), i + 1, chars, limit)
                        )

                    if rs.endswith('"""'):
                        in_docs = False

                io.close()

    if bad_lines:
        raise BadLines(
            ("%d line(s) are too long:\n" % len(bad_lines))
            + "\n".join(
                "- %s, line %d (%d/%d)" % (file, line, chars, limit)
                for file, line, chars, limit in bad_lines
            )
        )

    return True
