from typing import List, Dict, TypeVar

import pytest

from potc.testing import transobj_assert

try:
    from typing import TypingMeta
except ImportError:
    is_3_6 = False
else:
    is_3_6 = True

try:
    _ = list[int]
except TypeError:
    is_3_9 = False
else:
    is_3_9 = True

only_3_6 = pytest.mark.unittest if is_3_6 else pytest.mark.ignore
only_3_9 = pytest.mark.unittest if is_3_9 else pytest.mark.ignore


class TestRuleNativeTyping:
    @pytest.mark.unittest
    def test_collection_types(self):
        with transobj_assert(List) as (obj, name):
            assert obj == List
            assert name == ('typing_items' if not is_3_6 else 'builtin_type')

        with transobj_assert(Dict) as (obj, name):
            assert obj == Dict
            assert name == ('typing_items' if not is_3_6 else 'builtin_type')

    @pytest.mark.unittest
    def test_simple_collections(self):
        with transobj_assert(List[int]) as (obj, name):
            assert obj == List[int]
            assert name == 'typing_wrapper'

        with transobj_assert(Dict[int, List[int]]) as (obj, name):
            assert obj == Dict[int, List[int]]
            assert name == 'typing_wrapper'

    @only_3_9
    def test_advanced_general_alias(self):
        with transobj_assert(list[int]) as (obj, name):
            assert obj == list[int]
            assert name == 'typing_wrapper'

        with transobj_assert(dict[int, list[int]]) as (obj, name):
            assert obj == dict[int, list[int]]
            assert name == 'typing_wrapper'

    @pytest.mark.unittest
    def test_typevar(self):
        K = TypeVar('K', bound=int)
        V = TypeVar('V', int, str)

        with transobj_assert(K) as (obj, name):
            assert isinstance(obj, TypeVar)
            assert obj.__name__ == 'K'
            assert obj.__constraints__ == ()
            assert obj.__bound__ == int
            assert name == 'typing_typevar'

        with transobj_assert(V) as (obj, name):
            assert isinstance(obj, TypeVar)
            assert obj.__name__ == 'V'
            assert obj.__constraints__ == (int, str)
            assert obj.__bound__ is None
            assert name == 'typing_typevar'

        with transobj_assert(Dict[K, V]) as (obj, name):
            assert obj.__origin__ == (Dict if is_3_6 else dict)
            _k, _v = obj.__args__
            assert isinstance(_k, TypeVar)
            assert _k.__name__ == 'K'
            assert _k.__constraints__ == ()
            assert _k.__bound__ == int
            assert isinstance(_v, TypeVar)
            assert _v.__name__ == 'V'
            assert _v.__constraints__ == (int, str)
            assert _v.__bound__ is None
            assert name == 'typing_wrapper'
