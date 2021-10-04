import dill
import pytest
from easydict import EasyDict

from potc.utils import try_import_info

OBJ = 1
P_1 = 2
P_2 = 3
P_3 = 4
QQ3 = EasyDict(
    P_1=P_1,
    P_2=P_2,
    P_3=P_3,
)


@pytest.mark.unittest
class TestUtilsImports:
    def test_imports(self):
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
