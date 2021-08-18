import pytest

from potc.fixture import rule, Addons, is_rule, UnprocessableError


@pytest.mark.unittest
class TestFixtureCommon:
    def test_rule(self):
        @rule()
        def r1(v, addon: Addons):
            pt = addon.obj(pytest)
            if v < 0:
                raise RuntimeError
            else:
                return f'pytest-{v}'

        assert is_rule(r1)
        assert r1.__rule__.name == 'r1'

        add = Addons()
        assert not add.import_items
        with pytest.raises(RuntimeError):
            r1(-1, add)
        assert not add.import_items

        r1(1, add)
        assert list(map(str, add.import_items)) == [
            'import pytest'
        ]

        a2 = rule('a2', type_=int)(r1)
        assert a2.__rule__.name == 'a2'
        assert a2.__rule__.origin is r1.__rule__.origin

        add = Addons()
        assert not add.import_items
        with pytest.raises(RuntimeError):
            a2(-1, add)
        assert not add.import_items

        a2(1, add)
        assert list(map(str, add.import_items)) == [
            'import pytest'
        ]

        with pytest.raises(UnprocessableError):
            a2(1.0, add)
        assert list(map(str, add.import_items)) == [
            'import pytest'
        ]

        a2(2, add)
        assert list(map(str, add.import_items)) == [
            'import pytest',
            'import pytest',
        ]
