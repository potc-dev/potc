import pytest

from potc.fixture import rule, build_chain, rules_combine, Addons, UnprocessableError


@pytest.mark.unittest
class TestFixtureChain:
    def test_build_chain(self):
        @rule()
        def r1():
            pass

        @rule()
        def r2():
            pass

        @rule()
        def r3():
            pass

        @rule()
        def r4():
            pass

        @rule()
        def r5():
            pass

        _result = build_chain((
            (r1, r2,),
            [r5, r4],
            r3,
        ))
        assert _result == [r1, r2, r4, r5, r3] or _result == [r1, r2, r5, r4, r3]
        assert build_chain(((r3, r5,), (), (r1, r4), r2)) == [r3, r5, r1, r4, r2]

        with pytest.raises(TypeError):
            build_chain(({r1, r2}))
        with pytest.raises(NameError):
            rt = rule('r2')(lambda: None)
            build_chain(((r3, r5,), (), (r1, r4), r2, rt))
        with pytest.raises(ArithmeticError):
            build_chain(((r3, r5,), (), (r1, r4), r2, r2))

    def test_rules_combine(self):
        with pytest.raises(TypeError):
            rules_combine([1, 2, 3])

        @rule(type_=int)
        def r1(v):
            return repr(v)

        @rule(type_=list)
        def r2(v, addon):
            return '[' + ', '.join(map(lambda x: str(addon.val(x)), v)) + ']'

        with pytest.raises(KeyError):
            rules_combine(r1, r1)

        rc = rules_combine(r1, r2)
        add = Addons(rule=lambda x, a: rc(x, a)[0])
        assert rc(1, add) == ('1', 'r1')
        assert rc(2, add) == ('2', 'r1')
        assert rc(-1, add) == ('-1', 'r1')
        assert rc([], add) == ('[]', 'r2')
        assert rc([1, 2, [3, 4]], add) == ('[1, 2, [3, 4]]', 'r2')
        with pytest.raises(UnprocessableError):
            rc(None, add)
        with pytest.raises(UnprocessableError):
            rc('1223', add)
