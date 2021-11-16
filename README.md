# len8


[![PyPi version](https://img.shields.io/pypi/v/len8.svg)](https://pypi.python.org/pypi/len8/)
[![PyPI - Status](https://img.shields.io/pypi/status/len8)](https://pypi.python.org/pypi/len8/)
[![Downloads](https://pepy.tech/badge/len8)](https://pepy.tech/project/len8)
[![GitHub last commit](https://img.shields.io/github/last-commit/parafoxia/len8)](https://github.com/parafoxia/len8)
[![License](https://img.shields.io/github/license/parafoxia/len8.svg)](https://github.com/parafoxia/len8/blob/main/LICENSE)

[![CI](https://github.com/parafoxia/len8/actions/workflows/ci.yml/badge.svg)](https://github.com/parafoxia/len8/actions/workflows/ci.yml)
[![Read the Docs](https://img.shields.io/readthedocs/len8)](https://len8.readthedocs.io/en/latest/index.html)
[![Maintainability](https://api.codeclimate.com/v1/badges/9ec0deb12d512a60e6af/maintainability)](https://codeclimate.com/github/parafoxia/len8/maintainability)
[![Test Coverage](https://api.codeclimate.com/v1/badges/9ec0deb12d512a60e6af/test_coverage)](https://codeclimate.com/github/parafoxia/len8/test_coverage)

A utility for keeping line lengths within [PEP 8](https://www.python.org/dev/peps/pep-0008/#maximum-line-length) standards.

## Features

- An easy-to-use CLI (command-line interface)
- Check a single file, directory, or multiple files and directories
- Exclude files and directories from being checked
- Set different maximum lengths for both code and documentation
- Minimal dependencies

## Installation

**You need Python 3.6.0 or greater to run len8.**

To install the latest stable version of len8, use the following command:
```sh
pip install len8
```

You can also install the latest development version using the following command:
```sh
pip install git+https://github.com/parafoxia/len8
```

You may need to prefix these commands with a call to the Python interpreter depending on your OS and Python configuration.

## Quickstart

To get started checking your Python projects with len8:

#### Using the terminal

```sh
# Check all files in the CWD
len8 .

# Check all files in `tests` directory and `stats.py` file in CWD
len8 tests stats.py

# Check all files in two particular directories
len8 my_package tests

# Excluding file 'config.py' and directory 'secrets'
# By default '.venv', 'venv', and '.nox' are excluded
len8 -x config.py,secrets .

# Check 'project' dir and increase maximum allowed line lengths
# Note that line lengths for comments and docs stay at 72
len8 -l project         # Increase to 88 (black's default)
len8 -ll /home/project  # Increase to 99 (max allowed by PEP 8)

# Check using custom line lengths
len8 -c 150 .     # Increase code to 150
len8 -d 100 .     # Increase docs to 100
len8 -ll -d 99 .  # Increase code and docs to 99

# Check only one file 'important.py'
len8 important.py
len8 ./dir/important.py

# Check using multiple flags at once
len8 -lx ignoreme.py ./project_dir
```

#### In a Python script

```py
from len8 import Checker

# Instantiate a new Checker, with strict mode set to True
checker = Checker(strict=True)

# Set attributes after instantiation
checker.extend = 2
checker.exclude = ["excluded_dir"]
checker.strict = False

# Set line lengths after instantiation
checker.set_lengths(code=100, docs=80)

# Checks everything in the cwd
bad_lines = checker.check(".")

# Because strict mode is set to False and no error is raised, we
# print the returned value from the check method
print(bad_lines)
```

## Contributing

len8 is open to contributions. To find out where to get started, have a look at the [contributing guide](https://github.com/parafoxia/len8/blob/main/CONTRIBUTING.md).

## License

The len8 module for Python is licensed under the [BSD 3-Clause License](https://github.com/parafoxia/len8/blob/main/LICENSE).
