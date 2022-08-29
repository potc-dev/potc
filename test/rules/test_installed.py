from typing import NoReturn, List, Dict, Set, Tuple, Callable, Any, TypeVar

import pytest

import test
from potc.testing import transobj_assert, mock_potc_plugins
from ..conftest import with_pythonpath


@pytest.fixture()
def potc_dict_installed():
    with with_pythonpath('plugins/dict'):
        with mock_potc_plugins('potc_dict.plugin'):
            yield


@pytest.fixture()
def potc_typing_installed():
    with with_pythonpath('plugins/typing'):
        with mock_potc_plugins('potc_typing.plugin'):
            yield


@pytest.fixture()
def potc_invalid_plugin_1_installed():
    with mock_potc_plugins(test):  # module without __rules__
        yield


@pytest.fixture()
def potc_invalid_plugin_2_installed():
    with mock_potc_plugins(233):  # invalid type
        yield


@pytest.mark.unittest
class TestRulesInstalled:
    @classmethod
    def __with_pkg(cls, pkgs):
        pass

    def test_without_potc_dict(self):
        with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
            assert obj == {'a': 1, 'b': 2}
            assert name == 'builtin_dict'

    def test_potc_dict_installed(self, potc_dict_installed):
        with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
            assert obj == {'a': 1, 'b': 2}
            assert name == 'pretty_dict'

    def test_potc_invalid_plugin_1(self, potc_invalid_plugin_1_installed):
        with pytest.raises(ImportError):
            with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
                pytest.fail('Should not reach here.')

    def test_potc_invalid_plugin_2(self, potc_invalid_plugin_2_installed):
        with pytest.raises(TypeError):
            with transobj_assert({'a': 1, 'b': 2}) as (obj, name):
                pytest.fail('Should not reach here.')

    def test_typing_installed(self, potc_typing_installed):
        with transobj_assert(NoReturn) as (obj, name):
            assert obj is NoReturn

        with transobj_assert(List) as (obj, name):
            assert obj == List
        with transobj_assert(Dict) as (obj, name):
            assert obj == Dict
        with transobj_assert(Set) as (obj, name):
            assert obj == Set
        with transobj_assert(Tuple) as (obj, name):
            assert obj == Tuple
        with transobj_assert(Callable) as (obj, name):
            assert obj == Callable

        with transobj_assert(List[int]) as (obj, name):
            assert obj == List[int]
        with transobj_assert(Dict[int, List[str]]) as (obj, name):
            assert obj == Dict[int, List[str]]
        with transobj_assert(Set[str]) as (obj, name):
            assert obj == Set[str]
        with transobj_assert(Tuple[int, str, List[str]]) as (obj, name):
            assert obj == Tuple[int, str, List[str]]
        with transobj_assert(Callable[..., int]) as (obj, name):
            assert obj == Callable[..., int]
        with transobj_assert(Callable[[], int]) as (obj, name):
            assert obj == Callable[[], int]
        with transobj_assert(Callable[[int, Any], str]) as (obj, name):
            assert obj == Callable[[int, Any], str]
        with transobj_assert(Callable[[int], Any]) as (obj, name):
            assert obj == Callable[[int], Any]

        try:
            _ = list[int]
        except TypeError:
            pass
        else:
            with transobj_assert(list[int]) as (obj, name):
                assert obj == list[int]
            with transobj_assert(dict[int, list[int]]) as (obj, name):
                assert obj == dict[int, list[int]]

        K = TypeVar('K', bound=int, contravariant=True)
        V = TypeVar('V', int, str, covariant=True)

        with transobj_assert(K) as (obj, name):
            assert isinstance(obj, TypeVar)
            assert obj.__name__ == 'K'
            assert obj.__constraints__ == ()
            assert obj.__bound__ == int
            assert not obj.__covariant__
            assert obj.__contravariant__

        with transobj_assert(V) as (obj, name):
            assert isinstance(obj, TypeVar)
            assert obj.__name__ == 'V'
            assert obj.__constraints__ == (int, str)
            assert obj.__bound__ is None
            assert obj.__covariant__
            assert not obj.__contravariant__

        with transobj_assert(Dict[K, V]) as (obj, name):
            assert obj.__origin__ in {Dict, dict}
            _k, _v = obj.__args__
            assert isinstance(_k, TypeVar)
            assert _k.__name__ == 'K'
            assert _k.__constraints__ == ()
            assert _k.__bound__ == int
            assert not _k.__covariant__
            assert _k.__contravariant__

            assert isinstance(_v, TypeVar)
            assert _v.__name__ == 'V'
            assert _v.__constraints__ == (int, str)
            assert _v.__bound__ is None
            assert _v.__covariant__
            assert not _v.__contravariant__
