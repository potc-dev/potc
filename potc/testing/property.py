import math
import types
from functools import partial
from typing import NamedTuple, NoReturn, List, Set, Dict, Tuple, Callable, Any, TypeVar

from dill import source

from .trans import transobj_assert, transvars_assert


class _LocalType:
    pass


class _MySet(set):
    pass


class _MyList(list):
    pass


class _MyTuple(tuple):
    pass


class _MyNamedTuple(NamedTuple):
    first: object
    second: object


class _MyDict(dict):
    pass


class _MyPair:
    def __init__(self, x, y):
        self.__x = x
        self.__y = y

    def __getstate__(self):
        return self.__x, self.__y

    def __setstate__(self, state):
        self.__x, self.__y = state

    def __eq__(self, other):
        return (other is self) or (type(other) == type(self) and self.__getstate__() == other.__getstate__())


class _WrapperClass:
    class _MyInnerPair(_MyPair):
        pass

    class _MyInnerPair(_MyPair):
        pass


def provement(trans=None):
    """
    Overview:
        Create a test class containing the tests of the basic properties.

    Arguments:
        - trans: Translator object to be used.

    Examples:

        >>> import pytest
        >>> from potc_dict.plugin import __rules__  # load rules from plugin potc_dict
        >>>
        >>> from potc.testing import provement
        >>> from potc.translate import BlankTranslator
        >>>
        >>>
        >>> @pytest.mark.unittest
        >>> class TestPlugin(provement(BlankTranslator(__rules__))):
        ...     def test_pretty_dict(self):
        ...         with self.transobj_assert({'a': 1}) as (obj, name):
        ...             assert obj == {'a': 1}
        ...             assert name == 'pretty_dict'
        ...         with self.transobj_assert({}) as (obj, name):
        ...             assert obj == {}
        ...             assert name == 'pretty_dict'
        ...         with self.transobj_assert({1: 2}) as (obj, name):
        ...             assert obj == {1: 2}
        ...             assert name == 'builtin_dict'
        ...
        ...         with self.transvars_assert({'a': {'b': 1}}) as (vars_, code):
        ...             assert vars_ == {'a': {'b': 1}}
        ...             assert 'dict(b=1)' in code

    """

    class _ProvementMeta(type):
        def __init__(cls, name, basis, attrs):
            type.__init__(cls, name, basis, attrs)
            cls.transobj_assert = partial(transobj_assert, trans=trans)
            cls.transvars_assert = partial(transvars_assert, trans=trans)

    # noinspection PyMethodMayBeStatic
    class _Provement(metaclass=_ProvementMeta):
        def test_str(self):
            with self.transobj_assert('') as (obj, name):
                assert obj == ''
            with self.transobj_assert('str') as (obj, name):
                assert obj == 'str'
            with self.transobj_assert('str' * 1000) as (obj, name):
                assert obj == 'str' * 1000

        def test_int(self):
            with self.transobj_assert(0) as (obj, name):
                assert obj == 0
            with self.transobj_assert(123) as (obj, name):
                assert obj == 123
            with self.transobj_assert(-3249) as (obj, name):
                assert obj == -3249

        def test_float(self):
            with self.transobj_assert(123.0) as (obj, name):
                assert obj == 123.0

            with self.transobj_assert(float('nan')) as (obj, name):
                assert math.isnan(obj)
            with self.transobj_assert(float('+inf')) as (obj, name):
                assert obj == math.inf
            with self.transobj_assert(float('-inf')) as (obj, name):
                assert obj == -math.inf

            with self.transobj_assert(math.e) as (obj, name):
                assert obj == math.e
            with self.transobj_assert(math.pi) as (obj, name):
                assert obj == math.pi
            with self.transobj_assert(math.tau) as (obj, name):
                assert obj == math.tau

        def test_none(self):
            with self.transobj_assert(None) as (obj, name):
                assert obj is None

        def test_bytes(self):
            with self.transobj_assert(b'') as (obj, name):
                assert obj == b''
                assert isinstance(obj, bytes)
            with self.transobj_assert(b'lsdjkflpisdjgp89erdjpo9\x00\x11') as (obj, name):
                assert obj == b'lsdjkflpisdjgp89erdjpo9\x00\x11'
                assert isinstance(obj, bytes)

            with self.transobj_assert(bytearray()) as (obj, name):
                assert obj == bytearray()
                assert isinstance(obj, bytearray)
            with self.transobj_assert(bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')) as (obj, name):
                assert obj == bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')
                assert isinstance(obj, bytearray)

        def test_type(self):
            with self.transobj_assert(int) as (obj, name):
                assert obj == int

            with self.transobj_assert(_LocalType) as (obj, name):
                assert obj == _LocalType

            with self.transobj_assert(_WrapperClass._MyInnerPair) as (obj, name):
                assert obj == _WrapperClass._MyInnerPair

            with self.transobj_assert(types.ModuleType) as (obj, name):
                assert obj is types.ModuleType

        def test_func(self):
            with self.transobj_assert(lambda x: x ** x) as (obj, name):
                assert obj(2) == 4
                assert obj(3) == 27

        def test_list(self):
            with self.transobj_assert([1, 2, 3]) as (obj, name):
                assert obj == [1, 2, 3]

            with self.transobj_assert([1, 'klsdfj', -1.15, lambda x: x ** x]) as (obj, name):
                assert obj[:3] == [1, 'klsdfj', -1.15]
                assert obj[3](2) == 4
                assert obj[3](3) == 27

            with self.transobj_assert([]) as (obj, name):
                assert obj == []

            with self.transobj_assert([1]) as (obj, name):
                assert obj == [1]

            with self.transobj_assert(_MyList([1, 2, 3])) as (obj, name):
                assert isinstance(obj, _MyList)
                assert obj == _MyList([1, 2, 3])

        def test_tuple(self):
            with self.transobj_assert(()) as (obj, name):
                assert obj == ()

            with self.transobj_assert((1,)) as (obj, name):
                assert obj == (1,)

            with self.transobj_assert((1, 2, 3)) as (obj, name):
                assert obj == (1, 2, 3)

            with self.transobj_assert((1, 'klsdfj', -1.15, lambda x: x ** x)) as (obj, name):
                assert obj[:3] == (1, 'klsdfj', -1.15)
                assert obj[3](2) == 4
                assert obj[3](3) == 27

            with transobj_assert(_MyNamedTuple(1, 2)) as (obj, name):
                assert isinstance(obj, _MyNamedTuple)
                assert obj == _MyNamedTuple(1, 2)

            with self.transobj_assert(_MyTuple((1, 2, 3))) as (obj, name):
                assert isinstance(obj, _MyTuple)
                assert obj == _MyTuple((1, 2, 3))

        def test_set(self):
            with self.transobj_assert(set()) as (obj, name):
                assert isinstance(obj, set)
                assert obj == set()

            with self.transobj_assert({1, 2, 3}) as (obj, name):
                assert isinstance(obj, set)
                assert obj == {1, 2, 3}

            with self.transobj_assert(_MySet({1, 2, 3})) as (obj, name):
                assert isinstance(obj, _MySet)
                assert obj == _MySet({1, 2, 3})

            with self.transobj_assert(frozenset({1, 2, 3})) as (obj, name):
                assert isinstance(obj, frozenset)
                assert obj == frozenset({1, 2, 3})

        def test_dict(self):
            with self.transobj_assert({}) as (obj, name):
                assert obj == {}

            with self.transobj_assert({'a': 1}) as (obj, name):
                assert obj == {'a': 1}

            with self.transobj_assert({'a': 1, 3: 'klsdfgj'}) as (obj, name):
                assert obj == {'a': 1, 3: 'klsdfgj'}

            with self.transobj_assert(_MyDict()) as (obj, name):
                assert isinstance(obj, _MyDict)
                assert obj == _MyDict()

            with self.transobj_assert(_MyDict(a=1)) as (obj, name):
                assert isinstance(obj, _MyDict)
                assert obj == _MyDict(a=1)

        def test_object(self):
            with self.transobj_assert(_MyPair(1, 2)) as (obj, name):
                assert obj == _MyPair(1, 2)

            with self.transobj_assert(_WrapperClass._MyInnerPair(1, 2)) as (obj, name):
                assert obj == _WrapperClass._MyInnerPair(1, 2)

        def test_module(self):
            with self.transobj_assert(source) as (obj, name):
                assert obj is source

        def test_ellipsis(self):
            with self.transobj_assert(...) as (obj, name):
                assert obj is Ellipsis

        def test_range(self):
            with self.transobj_assert(range(10)) as (obj, name):
                assert obj == range(10)

            with self.transobj_assert(range(-1, 6)) as (obj, name):
                assert obj == range(-1, 6)

            with self.transobj_assert(range(-1, 6, 2)) as (obj, name):
                assert obj == range(-1, 6, 2)

        def test_slice(self):
            with self.transobj_assert(slice(10)) as (obj, name):
                assert obj == slice(10)

            with self.transobj_assert(slice(-5, 10)) as (obj, name):
                assert obj == slice(-5, 10)

            with self.transobj_assert(slice(-5, 10, -4)) as (obj, name):
                assert obj == slice(-5, 10, -4)

        def test_builtin_items(self):
            with self.transobj_assert(min) as (obj, name):
                assert obj is min
                assert obj(1, 2, -1) == -1

            with self.transobj_assert(NotImplemented) as (obj, name):
                assert obj is NotImplemented

        def test_builtin_complex(self):
            with self.transobj_assert(2 + 3j) as (obj, name):
                assert obj == 2 + 3j

            with self.transobj_assert(-4j) as (obj, name):
                assert obj == 0 - 4j

            with self.transobj_assert(2 - 0j) as (obj, name):
                assert obj == 2 - 0j

        def test_mixed_case(self):
            with self.transobj_assert({
                'a': 1,
                1: {'ab', 1, 2, (), (1, 'dkls')},
                'feat': [None, type, int, 233, 'sdfkl', (5, 6, -3 + 1j), {}, set(), []],
            }) as (obj, name):
                assert obj == {
                    'a': 1,
                    1: {'ab', 1, 2, (), (1, 'dkls')},
                    'feat': [None, type, int, 233, 'sdfkl', (5, 6, -3 + 1j), {}, set(), []],
                }

        def test_typing(self):
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

    return _Provement
