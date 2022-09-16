from contextlib import contextmanager

from hbutils.testing import isolated_entry_points

from ..rules.installed import POTC_PLUGIN_GROUP


@contextmanager
def mock_potc_plugins(*plugins, clear=False):
    """
    Overview:
        Mock potc plugins for unittest.

    :param plugins: String of plugin module, such as ``potc_dict.plugin``, which can be auto-imported.
    :param clear: Only use the mocked plugins. Default is ``False``, which means the installed plugins will be kept.

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
    with isolated_entry_points(POTC_PLUGIN_GROUP, [*plugins], clear=clear):
        yield
