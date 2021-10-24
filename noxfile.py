import typing as t

import nox


def parse_requirements(path: str) -> t.List[str]:
    with open(path, mode="r", encoding="utf-8") as f:
        deps = (d.strip() for d in f.readlines())
        return [d for d in deps if not d.startswith(("#", "-r", "."))]


DEPS = {
    dep.split("==")[0]: dep
    for dep in [
        *parse_requirements("./requirements-dev.txt"),
        *parse_requirements("./requirements-test.txt"),
    ]
}


@nox.session(reuse_venv=True)
def tests(session: nox.Session) -> None:
    session.install("-U", "-r", "./requirements-test.txt")
    session.run("pytest", "-s", "--verbose", "--log-level=INFO")


@nox.session(reuse_venv=True)
def check_formatting(session: nox.Session) -> None:
    session.install("-U", DEPS["black"])
    session.run("black", ".", "--check")


@nox.session(reuse_venv=True)
def check_typing(session: nox.Session) -> None:
    session.install("-U", DEPS["pyright"])
    session.run("pyright")
