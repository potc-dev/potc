import sys
from contextlib import contextmanager

import pytest

from potc.testing import mock_potc_plugins


@contextmanager
def with_pythonpath(*path: str):
    oldpath = sys.path
    try:
        sys.path = [*path, *oldpath]
        yield
    finally:
        sys.path = oldpath


@pytest.fixture(autouse=True)
def no_plugin():
    with mock_potc_plugins():
        yield
