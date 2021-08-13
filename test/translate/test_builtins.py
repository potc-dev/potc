import math
import types

import easydict
import pytest
from dill import source
from easydict import EasyDict

from potc.testing import obj_translate_assert
from potc.translate import rule_rename


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
class TestTranslateBuiltins:
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

    def test_bytearray(self):
        with obj_translate_assert(bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')) as (obj, name):
            assert obj == bytearray(b'lsdjkflpisdjgp89erdjpo9\x00\x11')
            assert isinstance(obj, bytearray)
            assert name == 'builtin_bytearray'

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
        def _my_dict_rule(v, addon):
            addon.is_type(v, dict)
            return addon.rule((set(v.keys()), set(v.values())))

        with obj_translate_assert({'a': 1}, [_my_dict_rule]) as (obj, name):
            assert obj == ({'a'}, {1})
            assert name == '_my_dict_rule'

        class _MyDictK(dict):
            pass

        class _MyDictV(dict):
            pass

        @rule_rename('keys')
        def _my_dict_rule_k(v, addon):
            addon.is_type(v, _MyDictK)
            return addon.rule(set(v.keys()))

        @rule_rename('values')
        def _my_dict_rule_v(v, addon):
            addon.is_type(v, _MyDictV)
            return addon.rule(set(v.values()))

        with obj_translate_assert(_MyDictK({'a': 1}), [_my_dict_rule_k, _my_dict_rule_v]) as (obj, name):
            assert obj == {'a'}
            assert name == 'keys'

        with obj_translate_assert(_MyDictV({'a': 1}), [_my_dict_rule_k, _my_dict_rule_v]) as (obj, name):
            assert obj == {1}
            assert name == 'values'

        with pytest.raises(NameError):
            @rule_rename('values892759834574(*)(&*(^&')
            def _my_dict_rule_t1(v, addon):
                addon.is_type(v, _MyDictV)
                return addon.rule(set(v.values()))

        with pytest.raises(NameError):
            @rule_rename('globals')
            def _my_dict_rule_t2(v, addon):
                addon.is_type(v, _MyDictV)
                return addon.rule(set(v.values()))

        @rule_rename('builtin_dict')
        def _my_dict_rule_t3(v, addon):
            addon.is_type(v, _MyDictV)
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
