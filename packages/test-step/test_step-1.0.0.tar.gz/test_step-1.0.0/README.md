# Test step

**test-step** is a simple extension of the pytest framework that allows defining test steps inside tests, including file
attachments and displaying steps in html reports.

## Requirements

```
Python >=3.11
pip
virtualenv
```

## Setup

```
virtualenv venv -p <name of Python 3 executable>
source ./venv/bin/activate
pip install -e ".[test]"
```

## Run Tests

In order to run tests on the command line

```
source ./venv/bin/activate
pytest
```

## Run lint

In order to run lint on the command line

```
source ./venv/bin/activate
ruff check .
```

To automatically fix some issues, run `ruff check . --fix`.
