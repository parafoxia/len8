# len8


[![PyPI pyversions](https://img.shields.io/pypi/pyversions/len8.svg)](https://pypi.python.org/pypi/len8/)

[![PyPI - Implementation](https://img.shields.io/pypi/implementation/len8)](https://pypi.python.org/pypi/len8/)
[![Downloads](https://pepy.tech/badge/len8)](https://pepy.tech/project/len8)
[![PyPi version](https://img.shields.io/pypi/v/len8.svg)](https://pypi.python.org/pypi/len8/)

[![PyPI - Status](https://img.shields.io/pypi/status/len8)](https://pypi.python.org/pypi/len8/)
[![Read the Docs](https://img.shields.io/readthedocs/len8)](https://len8.readthedocs.io/en/latest/index.html)
[![CI](https://github.com/parafoxia/len8/actions/workflows/ci.yml/badge.svg)](https://github.com/parafoxia/len8/actions/workflows/ci.yml)

[![License](https://img.shields.io/github/license/parafoxia/len8.svg)](https://github.com/parafoxia/len8/blob/main/LICENSE)
[![GitHub last commit](https://img.shields.io/github/last-commit/parafoxia/len8)](https://github.com/parafoxia/len8)
[![Maintenance](https://img.shields.io/maintenance/yes/2021)](https://github.com/parafoxia/len8)

A utility for keeping line lengths within [PEP 8](https://www.python.org/dev/peps/pep-0008/#maximum-line-length) standards.

## Features

- An easy-to-use CLI (command-line interface)
- Check a single file, directory, or multiple files and directories
- Exclude files and directories from being checked
- Extend acceptable length to 99 chars situationally
- No dependencies!

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

To get started checking your python projects with len8:

#### Using the terminal

```sh
# Check all files in the cwd
len8 .

# Check all files in `tests` directory and `stats.py` file in cwd
len8 tests stats.py

# Check all files in two particular directories
len8 my_package tests

# Excluding file 'config.py' and directory 'secrets'
# By default '.venv', 'venv', and '.nox' are excluded
len8 -x config.py,secrets .

# Check 'project' dir and increase line length to 99
len8 -l project
len8 -l /home/project

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
checker.extend = True
checker.exclude = ["excluded_dir"]
checker.strict = False

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
