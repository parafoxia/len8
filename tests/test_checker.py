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


@pytest.fixture()
def default_checker() -> len8.Checker:
    return len8.Checker()


@pytest.fixture()
def custom_checker() -> len8.Checker:
    return len8.Checker(exclude=["custom"], extend=True, strict=True)


def test_default_init(default_checker: len8.Checker) -> None:
    assert isinstance(default_checker, len8.Checker)
    assert default_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
    ]
    assert default_checker.extend is False
    assert default_checker.bad_lines is None
    assert default_checker.strict is False


def test_custom_init(custom_checker: len8.Checker) -> None:
    assert isinstance(custom_checker, len8.Checker)
    assert custom_checker.exclude == [
        Path(".nox"),
        Path(".venv"),
        Path("venv"),
        Path("custom"),
    ]
    assert custom_checker.extend is True
    assert custom_checker.bad_lines is None
    assert custom_checker.strict is True
