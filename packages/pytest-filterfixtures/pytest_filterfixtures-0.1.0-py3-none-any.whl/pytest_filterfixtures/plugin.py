"""pytest plugin to filter tests based on their fixtures."""

import pytest

__version__ = "0.1.0"


def pytest_addoption(parser: pytest.Parser):
    parser.addoption(
        "--exclude-fixtures",
        dest="exclude_fixtures",
        nargs="+",
        required=False,
        help="Ignores tests that use any of the fixtures provided",
    )
    parser.addoption(
        "--include-fixtures",
        dest="include_fixtures",
        nargs="+",
        required=False,
        help="Collects only the tests that use at least one of the fixtures provided",
    )


@pytest.hookimpl(trylast=True)
def pytest_collection_modifyitems(
    session: pytest.Session, config: pytest.Config, items: list[pytest.Item]
):
    tmp_items = items

    if exclude := config.getoption("exclude_fixtures"):
        tmp_items = [
            item
            for item in tmp_items
            if not any(f in exclude for f in getattr(item, "fixturenames", []))
        ]

    if include := config.getoption("include_fixtures"):
        tmp_items = [
            item
            for item in tmp_items
            if any(f in include for f in getattr(item, "fixturenames", []))
        ]

    deselected = [i for i in items if i not in tmp_items]
    config.hook.pytest_deselected(items=deselected)
    items[:] = tmp_items
