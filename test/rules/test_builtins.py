import math
import types

import easydict
import pytest
from dill import source
from easydict import EasyDict

from potc.fixture import rule, Addons
from potc.testing import obj_translate_assert


class _LocalType:
    pass


class _MySet(set):
    pass


class _MyList(list):
    pass


class _MyTuple(tuple):
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
        if other is self:
            return True
        elif type(other) == type(self):
            return self.__getstate__() == other.__getstate__()
        else:
            return False

    def __hash__(self):
        return hash(self.__getstate__())


@pytest.mark.unittest
class TestRulesBuiltins:
    def test_str(self):
        with obj_translate_assert('str') as (obj, name):
            assert obj == 'str'
            assert name == 'builtin_str'

        with obj_translate_assert('str' * 1000) as (obj, name):
            assert obj == 'str' * 1000
            assert name == 'builtin_str'

    def test_int(self):
        with obj_translate_assert(123) as (obj, name):
            assert obj == 123
            assert name == 'builtin_int'

        with obj_translate_assert(-3249) as (obj, name):
            assert obj == -3249
            assert name == 'builtin_int'

    def test_float(self):
        with obj_translate_assert(123.0) as (obj, name):
            assert obj == 123.0
            assert name == 'builtin_float'

        with obj_translate_assert(float('nan')) as (obj, name):
            assert math.isnan(obj)
            assert name == 'builtin_float'
        with obj_translate_assert(float('+inf')) as (obj, name):
            assert obj == math.inf
            assert name == 'builtin_float'
        with obj_translate_assert(float('-inf')) as (obj, name):
            assert obj == -math.inf
            assert name == 'builtin_float'

        with obj_translate_assert(math.e) as (obj, name):
            assert obj == math.e
            assert name == 'builtin_float'
        with obj_translate_assert(math.pi) as (obj, name):
            assert obj == math.pi
            assert name == 'builtin_float'
        with obj_translate_assert(math.tau) as (obj, name):
            assert obj == math.tau
            assert name == 'builtin_float'

    def test_none(self):
        with obj_translate_assert(None) as (obj, name):
            assert obj is None
            assert name == 'builtin_none'

    def test_bytes(self):
        with obj_translate_assert(b'lsdjkflpisdjgp89erdjpo9\x00\x11') as (obj, name):
            assert obj == b'lsdjkflpisdjgp89erdjpo9\x00\x11'
            assert isinstance(obj, bytes)
            assert name == 'builtin_bytes'

        with obj_translate_assert(bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')) as (obj, name):
            assert obj == bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')
            assert isinstance(obj, bytearray)
            assert name == 'builtin_bytes'

    def test_type(self):
        with obj_translate_assert(int) as (obj, name):
            assert obj == int
            assert name == 'builtin_type'

        with obj_translate_assert(_LocalType) as (obj, name):
            assert obj == _LocalType
            assert name == 'builtin_type'

        with obj_translate_assert(self._MyInnerPair) as (obj, name):
            assert obj == self._MyInnerPair
            assert name == 'builtin_type'

        with obj_translate_assert(types.ModuleType) as (obj, name):
            assert obj is types.ModuleType
            assert name == 'builtin_type'

    def test_func(self):
        with obj_translate_assert(lambda x: x ** x) as (obj, name):
            assert obj(2) == 4
            assert obj(3) == 27
            assert name == 'builtin_func'

    def test_list(self):
        with obj_translate_assert([1, 2, 3]) as (obj, name):
            assert obj == [1, 2, 3]
            assert name == 'builtin_list'

        with obj_translate_assert([1, 'klsdfj', -1.15, lambda x: x ** x]) as (obj, name):
            assert obj[:3] == [1, 'klsdfj', -1.15]
            assert obj[3](2) == 4
            assert obj[3](3) == 27
            assert name == 'builtin_list'

        with obj_translate_assert([]) as (obj, name):
            assert obj == []
            assert name == 'builtin_list'

        with obj_translate_assert([1]) as (obj, name):
            assert obj == [1]
            assert name == 'builtin_list'

        with obj_translate_assert(_MyList([1, 2, 3])) as (obj, name):
            assert isinstance(obj, _MyList)
            assert obj == _MyList([1, 2, 3])
            assert name == 'builtin_list'

    def test_tuple(self):
        with obj_translate_assert(()) as (obj, name):
            assert obj == ()
            assert name == 'builtin_tuple'

        with obj_translate_assert((1,)) as (obj, name):
            assert obj == (1,)
            assert name == 'builtin_tuple'

        with obj_translate_assert((1, 2, 3)) as (obj, name):
            assert obj == (1, 2, 3)
            assert name == 'builtin_tuple'

        with obj_translate_assert((1, 'klsdfj', -1.15, lambda x: x ** x)) as (obj, name):
            assert obj[:3] == (1, 'klsdfj', -1.15)
            assert obj[3](2) == 4
            assert obj[3](3) == 27
            assert name == 'builtin_tuple'

        with obj_translate_assert(_MyTuple((1, 2, 3))) as (obj, name):
            assert isinstance(obj, _MyTuple)
            assert obj == _MyTuple((1, 2, 3))
            assert name == 'builtin_tuple'

    def test_set(self):
        with obj_translate_assert(set()) as (obj, name):
            assert isinstance(obj, set)
            assert obj == set()
            assert name == 'builtin_set'

        with obj_translate_assert({1, 2, 3}) as (obj, name):
            assert isinstance(obj, set)
            assert obj == {1, 2, 3}
            assert name == 'builtin_set'

        with obj_translate_assert(_MySet({1, 2, 3})) as (obj, name):
            assert isinstance(obj, _MySet)
            assert obj == _MySet({1, 2, 3})
            assert name == 'builtin_set'

        with obj_translate_assert(frozenset({1, 2, 3})) as (obj, name):
            assert isinstance(obj, frozenset)
            assert obj == frozenset({1, 2, 3})
            assert name == 'builtin_set'

    def test_dict(self):
        with obj_translate_assert({}) as (obj, name):
            assert obj == {}
            assert name == 'builtin_dict'

        with obj_translate_assert({'a': 1}) as (obj, name):
            assert obj == {'a': 1}
            assert name == 'builtin_dict'

        with obj_translate_assert({'a': 1, 3: 'klsdfgj'}) as (obj, name):
            assert obj == {'a': 1, 3: 'klsdfgj'}
            assert name == 'builtin_dict'

        with obj_translate_assert(EasyDict()) as (obj, name):
            assert isinstance(obj, EasyDict)
            assert obj == EasyDict()
            assert name == 'builtin_dict'

        with obj_translate_assert(EasyDict(a=1)) as (obj, name):
            assert isinstance(obj, EasyDict)
            assert obj == EasyDict(a=1)
            assert name == 'builtin_dict'

    class _MyInnerPair(_MyPair):
        pass

    def test_object(self):
        with obj_translate_assert(_MyPair(1, 2)) as (obj, name):
            assert obj == _MyPair(1, 2)
            assert name == 'builtin_object'

        with obj_translate_assert(self._MyInnerPair(1, 2)) as (obj, name):
            assert obj == self._MyInnerPair(1, 2)
            assert name == 'builtin_object'

    def test_with_rules(self):
        @rule(type_=dict)
        def _my_dict_rule(v, addon):
            return addon.rule((set(v.keys()), set(v.values())))

        with obj_translate_assert({'a': 1}, [_my_dict_rule]) as (obj, name):
            assert obj == ({'a'}, {1})
            assert name == '_my_dict_rule'

        class _MyDictK(dict):
            pass

        class _MyDictV(dict):
            pass

        @rule('keys', type_=_MyDictK)
        def _my_dict_rule_k(v, addon):
            return addon.rule(set(v.keys()))

        @rule('values', type_=_MyDictV)
        def _my_dict_rule_v(v, addon):
            return addon.rule([set(v.values()), 2, addon.obj(math).cos(len(v))])

        with obj_translate_assert(_MyDictK({'a': 1}), [_my_dict_rule_k, _my_dict_rule_v]) as (obj, name):
            assert obj == {'a'}
            assert name == 'keys'

        with obj_translate_assert(_MyDictV({'a': 1}), [_my_dict_rule_k, _my_dict_rule_v]) as (obj, name):
            assert obj == [{1}, 2, math.cos(1)]
            assert name == 'values'

        with pytest.raises(NameError):
            @rule('values892759834574(*)(&*(^&', type_=_MyDictV)
            def _my_dict_rule_t1(v, addon):
                return addon.rule(set(v.values()))

        @rule('builtin_dict', type_=_MyDictV)
        def _my_dict_rule_t3(v, addon):
            return addon.rule(set(v.values()))

        with pytest.raises(KeyError):
            with obj_translate_assert({}, [_my_dict_rule_t3]):
                pass

    def test_module(self):
        with obj_translate_assert(easydict) as (obj, name):
            assert obj is easydict
            assert name == 'builtin_module'

        with obj_translate_assert(source) as (obj, name):
            assert obj is source
            assert name == 'builtin_module'

    def test_ellipsis(self):
        with obj_translate_assert(...) as (obj, name):
            assert obj is Ellipsis
            assert name == 'builtin_ellipsis'

    def test_range(self):
        with obj_translate_assert(range(10)) as (obj, name):
            assert obj == range(10)
            assert name == 'builtin_range'

        with obj_translate_assert(range(-1, 6)) as (obj, name):
            assert obj == range(-1, 6)
            assert name == 'builtin_range'

        with obj_translate_assert(range(-1, 6, 2)) as (obj, name):
            assert obj == range(-1, 6, 2)
            assert name == 'builtin_range'

    def test_slice(self):
        with obj_translate_assert(slice(10)) as (obj, name):
            assert obj == slice(10)
            assert name == 'builtin_slice'

        with obj_translate_assert(slice(-5, 10)) as (obj, name):
            assert obj == slice(-5, 10)
            assert name == 'builtin_slice'

        with obj_translate_assert(slice(-5, 10, -4)) as (obj, name):
            assert obj == slice(-5, 10, -4)
            assert name == 'builtin_slice'

    def test_new_addon_getitem(self):
        @rule(type_=tuple)
        def my_rule(v, addon: Addons):
            return addon.obj(list)(list(reversed(v)))[::-2]

        with obj_translate_assert((1, 2, 3, 4, 5), extend_rules=[my_rule]) as (obj, name):
            assert obj == [1, 3, 5]
            assert name == 'my_rule'

        @rule(type_=tuple)
        def my_rule_2(v, addon: Addons):
            return addon.obj(list)(list(reversed(v)))[-2]

        with obj_translate_assert((1, 2, 3, 4, 5), extend_rules=[my_rule_2]) as (obj, name):
            assert obj == 2
            assert name == 'my_rule_2'

    def test_builtin_items(self):
        with obj_translate_assert(min) as (obj, name):
            assert obj is min
            assert obj(1, 2, -1) == -1
            assert name == 'builtin_items'

        with obj_translate_assert(NotImplemented) as (obj, name):
            assert obj is NotImplemented
            assert name == 'builtin_items'
