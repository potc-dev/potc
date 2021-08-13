import dill as xdill
import numpy
import pytest
from numpy import ndarray

from potc.translate.addons.addons import Addons


@pytest.mark.unittest
class TestTranslateAddonsAddons:
    def test_addons(self):
        addons = Addons()
        with addons.transaction() as add:
            add.obj(xdill)
            add.obj(xdill, 'xdill')
            add.obj(numpy)
            add.obj(ndarray, 'nda')

        assert [str(i) for i in addons.import_items] == [
            'import dill',
            'import dill as xdill',
            'import numpy',
            'from numpy import ndarray as nda',
        ]

    def test_addons_with_failure(self):
        addons = Addons()
        with addons.transaction() as add:
            add.obj(xdill)
            add.obj(xdill, 'xdill')
        assert [str(i) for i in addons.import_items] == [
            'import dill',
            'import dill as xdill',
        ]

        with pytest.raises(RuntimeError):
            with addons.transaction() as add:
                add.obj(numpy)
                add.obj(ndarray, 'nda')
                raise RuntimeError
        assert [str(i) for i in addons.import_items] == [
            'import dill',
            'import dill as xdill',
        ]
