import dill
import pytest

from potc.fixture.imports import FromImport, DirectImport, ImportPool, try_import_info


@pytest.mark.unittest
class TestFixtureImports:
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

    def test_from_import(self):
        _import = FromImport('treevalue.utils').import_('int_enums').as_('my_int_enums')
        assert str(_import) == 'from treevalue.utils import int_enums as my_int_enums'
        assert _import.target == 'my_int_enums'
        assert repr(_import) == "<FromImport 'from treevalue.utils import int_enums as my_int_enums'>"
        assert _import.key == ('treevalue.utils.int_enums', 1, 'my_int_enums')

        with pytest.raises(ValueError):
            _import.as_('****')
        with pytest.raises(ValueError):
            _import.import_(None)

        assert _import == FromImport('treevalue.utils').import_('int_enums').as_('my_int_enums')
        assert hash(_import) == hash(FromImport('treevalue.utils').import_('int_enums').as_('my_int_enums'))
        assert _import == _import
        assert _import != 1

        _import = FromImport('treevalue.utils').import_('int_enums')
        assert str(_import) == 'from treevalue.utils import int_enums'
        assert _import.target == 'int_enums'
        assert repr(_import) == "<FromImport 'from treevalue.utils import int_enums'>"
        assert _import.key == ('treevalue.utils.int_enums', 1, 'int_enums')

    def test_direct_import(self):
        _import = DirectImport('treevalue.utils.int_enums').as_('my_int_enums')
        assert str(_import) == 'import treevalue.utils.int_enums as my_int_enums'
        assert _import.target == 'my_int_enums'
        assert repr(_import) == "<DirectImport 'import treevalue.utils.int_enums as my_int_enums'>"
        assert _import.key == ('treevalue.utils.int_enums', 0, 'my_int_enums')

        with pytest.raises(ValueError):
            _import.as_('****')

        assert _import == DirectImport('treevalue.utils.int_enums').as_('my_int_enums')
        assert hash(_import) == hash(DirectImport('treevalue.utils.int_enums').as_('my_int_enums'))
        assert _import == _import
        assert _import != 1

        _import = DirectImport('treevalue.utils.int_enums')

        assert str(_import) == 'import treevalue.utils.int_enums'
        assert _import.target == 'int_enums'
        assert repr(_import) == "<DirectImport 'import treevalue.utils.int_enums'>"
        assert _import.key == ('treevalue.utils.int_enums', 0, 'int_enums')

    def test_import_pool(self):
        pool = ImportPool()
        assert pool.imports == ()

        pool.import_('treevalue.utils').as_('tutils')
        pool.from_('trevalue.utils').import_('int_enums_loads')
        pool.import_('treevalue.config')
        pool.from_('trevalue.utils').import_('int_enums_loads').as_('my_int_enums_loads')

        assert [str(i) for i in pool.imports] == [
            'import treevalue.utils as tutils',
            'from trevalue.utils import int_enums_loads',
            'import treevalue.config',
            'from trevalue.utils import int_enums_loads as my_int_enums_loads',
        ]
