import builtins
import io
import subprocess
import tempfile
from functools import partial

import pytest
import where
from click.testing import CliRunner

from potc.entry.cli import potc_cli

python = where.first('python')


def reformatter(code: str) -> str:
    with io.StringIO() as sio:
        _print = partial(print, file=sio)

        _print(code)
        _print()

        _print('# This is a mark of reformatter here.')
        _print()

        return sio.getvalue()


# noinspection DuplicatedCode
@pytest.mark.unittest
class TestEntryCliExport:
    def test_export_simple(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=[
            'export',
            '-v', 'test.entry.cli.test_trans.F_INT',
            '-v', 'test.entry.cli.test_trans.F_TUPLE',
        ])

        assert result.exit_code == 0

        assert "F_INT = 2345" in result.stdout
        assert "F_TUPLE = (1, '94', [4, 5, -6, 9, math.e])" in result.stdout

        with tempfile.NamedTemporaryFile('w') as tf:
            _print = partial(builtins.print, file=tf)

            _print(result.stdout)
            _print()

            _print('print("F_INT:", F_INT)')
            _print('print("F_TUPLE:", F_TUPLE)')
            _print()

            tf.flush()

            srun = subprocess.run([python, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            assert srun.returncode == 0
            assert "F_INT: 2345" in srun.stdout
            assert "F_TUPLE: (1, '94', [4, 5, -6, 9, 2.7182818" in srun.stdout

    def test_export_fn(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=[
            'export',
            '-v', 'test.entry.cli.test_trans.F_*',
        ])

        assert result.exit_code == 0
        assert "F_INT = 2345" in result.stdout
        assert "F_TUPLE = (1, '94', [4, 5, -6, 9, math.e])" in result.stdout

        with tempfile.NamedTemporaryFile('w') as tf:
            _print = partial(builtins.print, file=tf)

            _print(result.stdout)
            _print()

            _print('print("F_INT:", F_INT)')
            _print('print("F_TUPLE:", F_TUPLE)')
            _print()

            tf.flush()

            srun = subprocess.run([python, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            assert srun.returncode == 0
            assert "F_INT: 2345" in srun.stdout
            assert "F_TUPLE: (1, '94', [4, 5, -6, 9, 2.7182818" in srun.stdout

    def test_export_fn_rename(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=[
            'export',
            '-v', 'P_$name=test.entry.cli.test_trans.F_*',
        ])

        assert result.exit_code == 0
        assert "P_F_INT = 2345" in result.stdout
        assert "P_F_TUPLE = (1, '94', [4, 5, -6, 9, math.e])" in result.stdout

        with tempfile.NamedTemporaryFile('w') as tf:
            _print = partial(builtins.print, file=tf)

            _print(result.stdout)
            _print()

            _print('print("F_INT:", P_F_INT)')
            _print('print("F_TUPLE:", P_F_TUPLE)')
            _print()

            tf.flush()

            srun = subprocess.run([python, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            assert srun.returncode == 0
            assert "F_INT: 2345" in srun.stdout
            assert "F_TUPLE: (1, '94', [4, 5, -6, 9, 2.7182818" in srun.stdout

    def test_export_fn_rules(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=[
            'export',
            '-v', 'test.entry.cli.test_trans.F_*',
            '-r', 'test.entry.cli.test_trans.__rules__',
        ])

        assert result.exit_code == 0
        assert "F_INT = 5 * 7 * 67" in result.stdout
        assert "F_TUPLE = (1, '94', [2 * 2, 5, -1 * 2 * 3, 3 * 3, math.e])" in result.stdout

        with tempfile.NamedTemporaryFile('w') as tf:
            _print = partial(builtins.print, file=tf)

            _print(result.stdout)
            _print()

            _print('print("F_INT:", F_INT)')
            _print('print("F_TUPLE:", F_TUPLE)')
            _print()

            tf.flush()

            srun = subprocess.run([python, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            assert srun.returncode == 0
            assert "F_INT: 2345" in srun.stdout
            assert "F_TUPLE: (1, '94', [4, 5, -6, 9, 2.7182818" in srun.stdout

    def test_export_fn_reformat(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=[
            'export',
            '-v', 'test.entry.cli.test_trans.F_*',
            '-f', 'test.entry.cli.test_export.reformatter',
        ])

        print(result.output)
        assert result.exit_code == 0
        assert "F_INT = 2345" in result.stdout
        assert "F_TUPLE = (1, '94', [4, 5, -6, 9, math.e])" in result.stdout
        assert '# This is a mark of reformatter here.' in result.stdout

        with tempfile.NamedTemporaryFile('w') as tf:
            _print = partial(builtins.print, file=tf)

            _print(result.stdout)
            _print()

            _print('print("F_INT:", F_INT)')
            _print('print("F_TUPLE:", F_TUPLE)')
            _print()

            tf.flush()

            srun = subprocess.run([python, tf.name], stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                  universal_newlines=True)
            assert srun.returncode == 0
            assert "F_INT: 2345" in srun.stdout
            assert "F_TUPLE: (1, '94', [4, 5, -6, 9, 2.7182818" in srun.stdout
