import sys
from contextlib import contextmanager
from unittest.mock import patch, MagicMock

import pytest
from pkg_resources import iter_entry_points


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


class _EntryPointWrapper:
    def __init__(self, x):
        self.__x = x

    def load(self):
        return self.__x


@contextmanager
def with_potc_plugins(*plugins):
    def _my_func(group):
        if group == 'potc_plugin':
            yield from map(_EntryPointWrapper, plugins)
        else:
            yield from iter_entry_points(group=group)

    with patch('pkg_resources.iter_entry_points', MagicMock(side_effect=_my_func)):
        yield


@pytest.fixture(autouse=True)
def no_plugin():
    with with_potc_plugins():
        yield
