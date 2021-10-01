import dill
import pytest
from easydict import EasyDict

from potc.utils import import_object, quick_import_object, iter_import_objects, try_import_info

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

    def test_import_object(self):
        assert import_object('OBJ', 'test.utils.test_imports') == 1
        assert import_object('zip') == zip

    def test_quick_import_object(self):
        assert quick_import_object('test.utils.test_imports.OBJ') == (1, 'test.utils.test_imports', 'OBJ')
        assert quick_import_object('zip') == (zip, '', 'zip')
        assert quick_import_object('zip.__dict__') == (zip.__dict__, '', 'zip.__dict__')
        assert quick_import_object('z*') == (zip, '', 'zip')
        assert quick_import_object('test.utils.test_imports.P_?') == (P_1, 'test.utils.test_imports', 'P_1')
        assert quick_import_object('test.utils.test_imports.???.*') == (P_1, 'test.utils.test_imports', 'QQ3.P_1')

        with pytest.raises(ImportError):
            quick_import_object('p233')
        with pytest.raises(ImportError):
            quick_import_object('zip.no_such_attr')

    def test_iter_import_objects(self):
        assert list(iter_import_objects('test.utils.test_imports.P_*')) == [
            (P_1, 'test.utils.test_imports', 'P_1'),
            (P_2, 'test.utils.test_imports', 'P_2'),
            (P_3, 'test.utils.test_imports', 'P_3'),
        ]
        assert list(iter_import_objects('test.utils.test_imports.???.*')) == [
            (P_1, 'test.utils.test_imports', 'QQ3.P_1'),
            (P_2, 'test.utils.test_imports', 'QQ3.P_2'),
            (P_3, 'test.utils.test_imports', 'QQ3.P_3'),
        ]
