import pytest

from potc.testing import obj_translate_assert
from potc.translate import Translator, BaseTranslator, TranslationFailed


@pytest.mark.unittest
class TestTranslateTrans:
    def test_translator(self):
        with obj_translate_assert(1, trans=Translator) as (obj, name):
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
            with obj_translate_assert(1, trans=BaseTranslator):
                pytest.fail('Should not reach here.')
        err = ei.value
        assert err.obj == 1
