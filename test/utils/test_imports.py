import dill
import pytest

from potc.translate.translate import translate_object, _translate_vars
from potc.utils import try_import_info


@pytest.mark.unittest
class TestUtilsImports:
    def test_imports(self):
        assert try_import_info(translate_object) == ('from', 'potc', 'import', 'translate_object')
        assert try_import_info(_translate_vars) == ('from', 'potc.translate.translate', 'import', '_translate_vars')
        assert try_import_info(_translate_vars, 'at3') == (
            'from', 'potc.translate.translate', 'import', '_translate_vars', 'as', 'at3')
        assert try_import_info(dill) == ('import', 'dill')
        assert try_import_info(dill, 'dx') == ('import', 'dill', 'as', 'dx')
        assert try_import_info(dill.source) == ('from', 'dill', 'import', 'source')
        assert try_import_info(dill.source, 'src') == ('from', 'dill', 'import', 'source', 'as', 'src')

        with pytest.raises(TypeError):
            try_import_info(1)

        p = lambda x: x + 1
        p.__module__ = 'dill'
        p.__name = 'p'
        with pytest.raises(TypeError):
            try_import_info(p)
