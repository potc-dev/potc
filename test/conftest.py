import sys
from contextlib import contextmanager

import pytest


@contextmanager
def with_pythonpath(*path: str):
    oldpath = sys.path
    try:
        sys.path = [*path, *oldpath]
        yield
    finally:
        sys.path = oldpath


@pytest.fixture()
def potc_dict_plugin():
    with with_pythonpath('plugins/dict'):
        import potc_dict.plugin
        yield potc_dict.plugin
