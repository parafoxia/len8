import nox


def parse_requirements(path):
    with open(path, mode="r", encoding="utf-8") as f:
        deps = (d.strip() for d in f.readlines())
        return [d for d in deps if not d.startswith(("#", "-r"))]


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    deps = parse_requirements("./requirements-test.txt")
    session.install(*deps)
    session.run("pytest", "-s", "--verbose", "--log-level=INFO")


@nox.session(reuse_venv=True)
def check_formatting(session: nox.Session) -> None:
    black_version = next(
        filter(
            lambda d: d.startswith("black"),
            parse_requirements("./requirements-dev.txt"),
        )
    ).split("==")[1]
    session.install("black==%s" % black_version)
    session.run("black", ".", "--check")
