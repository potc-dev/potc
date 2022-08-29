import types

import pkg_resources

from ..fixture import is_rule

_RULES_TAG = '__rules__'


def _autoload_plugin(plg):
    if isinstance(plg, types.ModuleType):
        if hasattr(plg, _RULES_TAG):
            return _autoload_plugin(getattr(plg, _RULES_TAG))
        else:
            raise ImportError(f'Not a module with rules inside - {repr(plg.__name__)}.')
    elif is_rule(plg) or isinstance(plg, (tuple, list)):
        return plg
    else:
        raise TypeError(f'Not a valid rule object, link or group - {repr(plg)}.')


POTC_PLUGIN_GROUP = 'potc_plugin'


def _iter_plugins():
    for ep in pkg_resources.iter_entry_points(group=POTC_PLUGIN_GROUP):
        yield ep.load()


def _load_plugins():
    return [_autoload_plugin(item) for item in _iter_plugins()]


def installed_loader():
    """
    Overview:
        Load rules from installed potc plugins.

    Returns:
        - rules: Rules from installed plugins.
    """
    return _load_plugins()
