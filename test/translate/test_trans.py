import random

import pytest
from yapf.yapflib.yapf_api import FormatCode

from potc.fixture import rule
from potc.testing import transobj_assert, transvars_assert
from potc.translate import Translator, BaseTranslator, TranslationFailed


@pytest.mark.unittest
class TestTranslateTrans:
    def test_translator(self):
        with transobj_assert(1, trans=Translator) as (obj, name):
            assert obj == 1
            assert name == 'builtin_int'

        _trans = Translator().transobj([1, 2, (1, float('-inf'))])
        assert _trans.code == '[1, 2, (1, -math.inf)]'
        assert list(map(str, _trans.addon.import_items)) == [
            'import math',
        ]
        assert _trans.trace == 'builtin_list'
        assert list(map(str, _trans.imports)) == [
            'import math',
        ]
        assert str(_trans) == '[1, 2, (1, -math.inf)]'
        _code, _addon, _trace = _trans
        assert _code == '[1, 2, (1, -math.inf)]'
        assert _trace == 'builtin_list'

    def test_base_translator(self):
        with pytest.raises(TranslationFailed) as ei:
            with transobj_assert(1, trans=BaseTranslator):
                pytest.fail('Should not reach here.')
        err = ei.value
        assert err.obj == 1

        with pytest.raises(TranslationFailed) as ei:
            with transobj_assert(1, trans=BaseTranslator()):
                pytest.fail('Should not reach here.')
        err = ei.value
        assert err.obj == 1

    def test_diy_translator(self):
        @rule(type_=int)
        def int_support(v):
            return repr(v)

        @rule(alias='fs', type_=float)
        def float_support(v):
            return repr(v)

        class MyTranslator(BaseTranslator):
            def __init__(self):
                BaseTranslator.__init__(self, [int_support, float_support])

        with transobj_assert(1, trans=MyTranslator()) as (obj, name):
            assert obj == 1
            assert name == 'int_support'
        with transobj_assert(1.0, trans=MyTranslator()) as (obj, name):
            assert obj == 1.0
            assert name == 'fs'
        with pytest.raises(TranslationFailed) as ei:
            with transobj_assert('str', trans=MyTranslator()):
                pytest.fail('Should not reach here.')
        err = ei.value
        assert err.obj == 'str'

    def test_transvars(self):
        with transvars_assert({
            'a': 233,
            'b': [1, 2, 3, {'x': 1}],
        }) as (vars_, code):
            assert vars_ == {
                'a': 233,
                'b': [1, 2, 3, {'x': 1}],
            }
            assert 'import' not in code

        _result = Translator().transvars({
            'a': 233,
            'b': [1, 2, 3, {'x': 1}],
        })
        assert 'import' not in _result.code
        assert 'a = 233' in _result.code
        assert "b = [1, 2, 3, {'x': 1}]" in _result.code
        assert {'a', 'b', '__all__'} == set(_result.addons.keys())
        assert str(_result) == _result.code
        _code, _addons = _result
        assert _code == str(_result)
        assert {'a', 'b', '__all__'} == set(_addons.keys())

        with pytest.raises(NameError):
            with transvars_assert({
                'a': 233,
                ' b': [1, 2, 3, {'x': 1}],
            }):
                pytest.fail("Should not reach here.")

    def test_transvars_reformat(self):
        li = [random.randint(1, 5) for _ in range(200)]
        with transvars_assert({
            'a': li,
        }) as (vars_, code):
            assert vars_ == {
                'a': li,
            }
            assert 'import' not in code
            assert len(code.splitlines()) == 2

        with transvars_assert({
            'a': li,
        }, reformat='pep8') as (vars_, code):
            assert vars_ == {
                'a': li,
            }
            assert 'import' not in code
            assert len(code.splitlines()) == 11

        with transvars_assert({
            'a': li,
        }, reformat='google') as (vars_, code):
            assert vars_ == {
                'a': li,
            }
            assert 'import' not in code
            assert len(code.splitlines()) == 11

        _pep8 = lambda x: FormatCode(x, style_config='pep8')[0]
        with transvars_assert({
            'a': li,
        }, reformat=_pep8) as (vars_, code):
            assert vars_ == {
                'a': li,
            }
            assert 'import' not in code
            assert len(code.splitlines()) == 11
