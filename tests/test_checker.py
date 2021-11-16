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

from pathlib import Path

import pytest  # type: ignore

import len8
from len8.errors import BadLines, InvalidPath

TEST_FILE = Path(__file__).parent / "testdata.py"
TEST_NON_VALID = TEST_FILE.parent / "nsx_simple_app.nsx"


@pytest.fixture()
def default_checker() -> len8.Checker:
    return len8.Checker()


@pytest.fixture()
def extended_checker() -> len8.Checker:
    return len8.Checker(
        exclude=["custom", Path("another")], extend=2, strict=True
    )


@pytest.fixture()
def custom_checker() -> len8.Checker:
    return len8.Checker(max_code_length=100, max_docs_length=80)


def test_default_init(default_checker: len8.Checker) -> None:
    assert isinstance(default_checker, len8.Checker)
    assert default_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
    ]
    assert default_checker.extend == 0
    assert default_checker.bad_lines is None
    assert default_checker.strict is False
    assert default_checker.code_length == 79
    assert default_checker.docs_length == 72


def test_extended_init(extended_checker: len8.Checker) -> None:
    assert isinstance(extended_checker, len8.Checker)
    assert extended_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
        Path("custom"),
        Path("another"),
    ]
    assert extended_checker.extend == 2
    assert extended_checker.bad_lines is None
    assert extended_checker.strict is True
    assert extended_checker.code_length == 99
    assert extended_checker.docs_length == 72


def test_custom_init(custom_checker: len8.Checker) -> None:
    assert isinstance(custom_checker, len8.Checker)
    assert custom_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
    ]
    assert custom_checker.extend == 0
    assert custom_checker.bad_lines is None
    assert custom_checker.strict is False
    assert custom_checker.code_length == 100
    assert custom_checker.docs_length == 80


def test_bad_inits(default_checker: len8.Checker) -> None:
    with pytest.raises(ValueError) as exc:
        len8.Checker(extend=5)
    assert f"{exc.value}" == "'extend' should be between 0 and 2 inclusive"

    with pytest.raises(ValueError) as exc:
        len8.Checker(max_code_length=-1)
    assert f"{exc.value}" == "line lengths cannot be less than 0"

    with pytest.raises(ValueError) as exc:
        len8.Checker(max_docs_length=-1)
    assert f"{exc.value}" == "line lengths cannot be less than 0"

    with pytest.raises(ValueError) as exc:
        default_checker.extend = 5
    assert f"{exc.value}" == "'extend' should be between 0 and 2 inclusive"


def test_setting_lengths(default_checker: len8.Checker) -> None:
    default_checker.set_lengths(code=100, docs=80)
    assert default_checker.code_length == 100
    assert default_checker.docs_length == 80

    default_checker.set_lengths(docs=50)
    assert default_checker.code_length == 100
    assert default_checker.docs_length == 50

    default_checker.set_lengths(code=None)
    assert default_checker.code_length == 79
    assert default_checker.docs_length == 50


def test_non_strict_output(default_checker: len8.Checker) -> None:
    output = (
        "3 line(s) are too long:\n"
        f"- {TEST_FILE}, line 4 (76/72)\n"
        f"- {TEST_FILE}, line 5 (83/79)\n"
        f"- {TEST_FILE}, line 11 (78/72)"
    )
    assert default_checker.check(TEST_FILE) == output


def test_non_strict_output_extended(default_checker: len8.Checker) -> None:
    default_checker.extend = True
    output = (
        "2 line(s) are too long:\n"
        f"- {TEST_FILE}, line 4 (76/72)\n"
        f"- {TEST_FILE}, line 11 (78/72)"
    )
    assert default_checker.check(TEST_FILE) == output
    assert default_checker.check(TEST_FILE.parent) == output


def test_strict_output(default_checker: len8.Checker) -> None:
    default_checker.strict = True
    output = (
        "3 line(s) are too long:\n"
        f"- {TEST_FILE}, line 4 (76/72)\n"
        f"- {TEST_FILE}, line 5 (83/79)\n"
        f"- {TEST_FILE}, line 11 (78/72)"
    )
    with pytest.raises(BadLines) as exc:
        assert default_checker.check(TEST_FILE) == output
    assert f"{exc.value}" == output


def test_update_excludes(default_checker: len8.Checker) -> None:
    default_checker.exclude = [Path("custom"), Path("another")]
    assert default_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
        Path("custom"),
        Path("another"),
    ]


def test_file_validation(default_checker: len8.Checker) -> None:
    assert default_checker._is_valid(TEST_FILE)
    assert not default_checker._is_valid(Path("README.md"))

    default_checker.exclude = [Path(__file__).parent]
    assert default_checker._is_valid(Path("len8").absolute())
    assert not default_checker._is_valid(Path("tests").absolute())

    default_checker.exclude = [Path("testdata.py")]
    assert default_checker._is_valid(Path("checker.py"))
    assert not default_checker._is_valid(Path("testdata.py"))


def test_pathlib_conversion_on_check(default_checker: len8.Checker) -> None:
    output = (
        "3 line(s) are too long:\n"
        f"- {TEST_FILE}, line 4 (76/72)\n"
        f"- {TEST_FILE}, line 5 (83/79)\n"
        f"- {TEST_FILE}, line 11 (78/72)"
    )
    assert default_checker.check(f"{TEST_FILE}") == output

    default_checker.strict = True
    with pytest.raises(InvalidPath) as exc:
        assert default_checker.check(f"invalid_dir") == output
    assert f"{exc.value}" == f"Error: 'invalid_dir' is not a valid path."


def test_skip_invalid_files(default_checker: len8.Checker) -> None:
    try:
        default_checker.check(TEST_NON_VALID)
    except UnicodeDecodeError:
        pytest.fail()
