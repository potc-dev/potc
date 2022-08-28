from unittest import skipUnless
from unittest.mock import patch, MagicMock

import pytest
from hbutils.testing import vpip
from pkg_resources import iter_entry_points

from potc.testing import transobj_assert


class _Wrapper:
    def __init__(self, x):
        self.__x = x

    def load(self):
        return self.__x


@pytest.fixture()
def potc_dict_installed(potc_dict_plugin):
    def _my_func(group):
        if group == 'potc_plugin':
            yield from map(_Wrapper, [potc_dict_plugin])
        else:
            yield from iter_entry_points(group=group)

    with patch('pkg_resources.iter_entry_points', MagicMock(side_effect=_my_func)):
        yield


@skipUnless(not vpip('potc-dict'), 'no potc-dict installed required')
@pytest.mark.unittest
class TestRulesInstalled:
    @classmethod
    def __with_pkg(cls, pkgs):
        pass

    def test_without_potc_dict(self):
        with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
            assert obj == {'a': 1, 'b': 2}
            assert name == 'builtin_dict'

    def test_with_manual_potc_dict(self, potc_dict_plugin):
        with transobj_assert({'a': 1, 'b': 2}, trans=potc_dict_plugin.__rules__) as (obj, name):
            assert obj == {'a': 1, 'b': 2}
            assert name == 'pretty_dict'

    def test_potc_dict_installed(self, potc_dict_installed):
        with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
            assert obj == {'a': 1, 'b': 2}
            assert name == 'pretty_dict'
