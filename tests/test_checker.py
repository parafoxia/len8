import pytest

import len8


@pytest.fixture()
def default_checker() -> len8.Checker:
    return len8.Checker()


@pytest.fixture()
def custom_checker() -> len8.Checker:
    return len8.Checker(exclude=["custom"], extend=True, strict=True)


def test_default_init(default_checker: len8.Checker) -> None:
    assert isinstance(default_checker, len8.Checker)
    assert default_checker.exclude == [".nox", ".venv", "venv"]
    assert default_checker.extend is False
    assert default_checker.bad_lines is None
    assert default_checker.strict is False


def test_custom_init(custom_checker: len8.Checker) -> None:
    assert isinstance(custom_checker, len8.Checker)
    assert custom_checker.exclude == [".nox", ".venv", "venv", "custom"]
    assert custom_checker.extend is True
    assert custom_checker.bad_lines is None
    assert custom_checker.strict is True
