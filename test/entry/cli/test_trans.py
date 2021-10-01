import math

import pytest
from click.testing import CliRunner

from potc.entry.cli import potc_cli
from potc.fixture import rule, Addons
from potc.rules import builtin_int

F_INT = 2345
F_TUPLE = (1, '94', [4, 5, -6, 9, math.e])


@rule(type_=int)
def int_sep(v, addon: Addons):
    items = []
    if v < 0:
        items.append(-1)
        v = -v
    elif v == 0:
        items.append(0)

    i = 1
    while v > 1:
        i += 1
        while v % i == 0:
            items.append(i)
            v //= i

    if not items:
        items.append(1)
    return ' * '.join(map(repr, items))


__rules__ = [
    (int_sep, builtin_int)
]


@pytest.mark.unittest
class TestEntryCliTrans:
    def test_simple_trans_int(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_INT'])

        assert result.exit_code == 0
        assert '2345' in result.stdout

    def test_simple_trans_tuple(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_TUPLE'])

        assert result.exit_code == 0
        assert "(1, '94', [4, 5, -6, 9, math.e])" in result.stdout

    def test_simple_trans_int_info(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_INT', '-I'])

        assert result.exit_code == 0

        assert 'Object Information:' in result.stdout
        assert 'Module : test.entry.cli.test_trans' in result.stdout
        assert 'Name : F_INT' in result.stdout
        assert 'Type : int' in result.stdout

        assert 'Import Statements' not in result.stdout

        assert 'Expression:' in result.stdout
        assert '2345' in result.stdout

    def test_simple_trans_tuple_info(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_TUPLE', '-I'])

        assert result.exit_code == 0

        assert 'Object Information:' in result.stdout
        assert 'Module : test.entry.cli.test_trans' in result.stdout
        assert 'Name : F_TUPLE' in result.stdout
        assert 'Type : tuple' in result.stdout

        assert 'Import Statements' in result.stdout
        assert 'import math'

        assert 'Expression:' in result.stdout
        assert "(1, '94', [4, 5, -6, 9, math.e])" in result.stdout

    def test_simple_trans_int_info_rules(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_INT', '-I',
                                               '-r', 'test.entry.cli.test_trans.__rules__'])

        assert result.exit_code == 0

        assert 'Object Information:' in result.stdout
        assert 'Module : test.entry.cli.test_trans' in result.stdout
        assert 'Name : F_INT' in result.stdout
        assert 'Type : int' in result.stdout
        assert 'External Rules :' in result.stdout
        assert '[[(<int_sep> --> <builtin_int>)]]' in result.stdout

        assert 'Import Statements' not in result.stdout

        assert 'Expression:' in result.stdout
        assert '5 * 7 * 67' in result.stdout

    def test_simple_trans_tuple_info_rules(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_TUPLE', '-I',
                                               '-r', 'test.entry.cli.test_trans.__rules__'])

        assert result.exit_code == 0

        assert 'Object Information:' in result.stdout
        assert 'Module : test.entry.cli.test_trans' in result.stdout
        assert 'Name : F_TUPLE' in result.stdout
        assert 'Type : tuple' in result.stdout
        assert 'External Rules :' in result.stdout
        assert '[[(<int_sep> --> <builtin_int>)]]' in result.stdout

        assert 'Import Statements' in result.stdout
        assert 'import math'

        assert 'Expression:' in result.stdout
        assert "(1, '94', [2 * 2, 5, -1 * 2 * 3, 3 * 3, math.e])" in result.stdout

    def test_simple_trans_input_error(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_TUPL'])

        assert result.exit_code == 2
        assert "Error: Invalid value for 'INPUT_': " \
               "Cannot import object 'test.entry.cli.test_trans.F_TUPL'." in result.output

    def test_simple_trans_rules_error(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['trans', 'test.entry.cli.test_trans.F_TUPLE', '-I',
                                               '-r', 'test.entry.cli.test_trans.__rules_'])

        assert result.exit_code == 2
        assert "Error: Invalid value for '-r' / '--rules': " \
               "Cannot import object 'test.entry.cli.test_trans.__rules_'." in result.output
