from contextlib import contextmanager
from functools import wraps
from unittest.mock import patch, MagicMock

import pkg_resources
from hbutils.reflection import quick_import_object

from ..rules.installed import POTC_PLUGIN_GROUP


class FakeEntryPoint:
    def __init__(self, name, *, dist=None, dist_name=None):
        self.name = name
        if not dist and dist_name:
            self.dist, _, _ = quick_import_object(dist_name)
        else:
            self.dist = dist

    def load(self):
        return self.dist


_UNTITLED_ID = -1


def _next_plugin_id():
    global _UNTITLED_ID
    _UNTITLED_ID += 1
    return f'_untitled_plugin_{_UNTITLED_ID}'
    pass


def _to_plugin(v) -> FakeEntryPoint:
    if isinstance(v, FakeEntryPoint):
        return v  # pragma: no cover
    elif isinstance(v, tuple):
        name, dist = v
        if isinstance(dist, str):
            return FakeEntryPoint(name, dist_name=dist)
        else:
            return FakeEntryPoint(name, dist=dist)
    else:
        return _to_plugin((_next_plugin_id(), v))


@contextmanager
def mock_potc_plugins(*plugins):
    """
    Overview:
        Mock potc plugins for unittest.

    :param plugins: String of plugin module, such as ``potc_dict.plugin``, which can be auto-imported.

    Examples::
        >>> from potc import transobj
        >>> from potc.testing import mock_potc_plugins
        >>>
        >>> # potc-dict is installed
        >>> print(transobj({'a': 1, 'b': [3, 'dfgk']}))
        dict(a=1, b=[3, 'dfgk'])
        >>>
        >>> with mock_potc_plugins():  # mock as no plugins
        ...     print(transobj({'a': 1, 'b': [3, 'dfgk']}))
        {'a': 1, 'b': [3, 'dfgk']}
        >>>
        >>> print(transobj({'a': 1, 'b': [3, 'dfgk']}))  # again
        dict(a=1, b=[3, 'dfgk'])
    """

    @wraps(pkg_resources.iter_entry_points)
    def _new_iter_func(group, name=None):
        if group == POTC_PLUGIN_GROUP:
            yield from filter(lambda x: (name is None or x.name == name), map(_to_plugin, plugins))
        else:
            yield from pkg_resources.iter_entry_points(group, name)  # pragma: no cover

    with patch('pkg_resources.iter_entry_points', MagicMock(side_effect=_new_iter_func)):
        yield
