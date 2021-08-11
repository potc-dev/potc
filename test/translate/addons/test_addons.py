import dill as xdill
import pytest
from numpy import ndarray as dxx

from potc.translate.addons.addons import Addons


@pytest.mark.unittest
class TestTranslateAddonsAddons:
    def test_addons(self):
        addons = Addons()
        with addons.transaction() as add:
            add.import_('treevalue.utils').as_('tutils')
            add.from_('trevalue.utils').import_('int_enums_loads')
            add.import_('treevalue.config')
            add.from_('trevalue.utils').import_('int_enums_loads').as_('my_int_enums_loads')
            add.quick_import(xdill, 'xdill')
            add.quick_import(dxx, 'dxx')

        assert [str(i) for i in addons.imports] == [
            'import treevalue.utils as tutils',
            'from trevalue.utils import int_enums_loads',
            'import treevalue.config',
            'from trevalue.utils import int_enums_loads as my_int_enums_loads',
            'import dill as xdill',
            'from numpy import ndarray as dxx',
        ]

    def test_addons_with_failure(self):
        addons = Addons()
        with addons.transaction() as add:
            add.import_('treevalue.utils').as_('tutils')
            add.from_('trevalue.utils').import_('int_enums_loads')
            add.quick_import
        assert [str(i) for i in addons.imports] == [
            'import treevalue.utils as tutils',
            'from trevalue.utils import int_enums_loads',
        ]

        with pytest.raises(ValueError):
            with addons.transaction() as add:
                add.import_('treevalue.config')
                add.from_('trevalue.utils').import_('int_enums_loads').as_('my_int_enums_loads')
                add.from_('trevalue.utils').import_('****').as_('my_int_enums_loads')
        assert [str(i) for i in addons.imports] == [
            'import treevalue.utils as tutils',
            'from trevalue.utils import int_enums_loads',
        ]

        with pytest.raises(TypeError):
            with addons.transaction() as add:
                add.quick_import(xdill, 'xdill')
                add.quick_import(1)
        assert [str(i) for i in addons.imports] == [
            'import treevalue.utils as tutils',
            'from trevalue.utils import int_enums_loads',
        ]
