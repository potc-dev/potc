import warnings
from functools import lru_cache

import pkg_resources

_GROUP_NAME = 'potc_plugin'


def _loaded_process(l):
    if isinstance(l, list):
        return l
    else:
        return [l]


@lru_cache()
def _load_plugins():
    _plugins = []
    _names = set()
    for ep in pkg_resources.iter_entry_points(group=_GROUP_NAME):
        if ep.name in _names:
            warnings.warn(f'Duplicate plugin resource name found - {repr(ep.name)}.')
        else:
            _names.add(ep.name)

        for _item in _loaded_process(ep.load()):
            _plugins.append(_item)

    return _plugins


plugins_ = _load_plugins()
