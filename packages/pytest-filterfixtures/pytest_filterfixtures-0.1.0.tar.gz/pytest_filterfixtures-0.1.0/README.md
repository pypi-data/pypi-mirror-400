# pytest-filterfixtures

`pytest-filterfixtures` is a `pytest` plugin to filter tests based on their fixtures.

This is particularly useful in large test codebases when fixtures require changes/refactoring, or a specific fixture stops wokring due to external reasons. You can work on modifying the fixture(s) and have better control over which tests should run.

## Installation
Install with pip
```
pip install pytest-filterfixtures
```

## Usage
`pytest-filterfixtures` adds the following command line options:
- `--include-fixtures` to execute all tests that use at least one of the specified fixtures as part of their setup/teardown
- `--exclude-fixtures` to deselect all tests that use at least one of the specified fixtures as part of their setup/teardown

### Example
Given the following test file
```py
@pytest.fixture()
def fixt1():
    return 1

@pytest.fixture()
def fixt2():
    return 2

@pytest.fixture()
def fixt3(fixt1):
    return fixt1 + 1

def test1(fixt1):
    ...

def test2(fixt2):
    ...

def test3(fixt3):
    ...
```

- `pytest --include-fixtures fixt1 fixt2` executes `test1, test2, test3`
- `pytest --include-fixtures fixt3` executes `test3`
- `pytest --exclude-fixtures fixt1` executes `test2`
- `pytest --exclude-fixtures fixt3 --include-fixtures fixt1` executes `test1`
