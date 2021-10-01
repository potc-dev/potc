import pytest
from click.testing import CliRunner

from potc.config.meta import __TITLE__, __VERSION__
from potc.entry.cli import potc_cli


@pytest.mark.unittest
class TestEntryCliVersion:
    def test_version(self):
        runner = CliRunner()
        result = runner.invoke(potc_cli, args=['-v'])

        assert result.exit_code == 0
        assert __TITLE__.lower() in result.stdout.lower()
        assert __VERSION__.lower() in result.stdout.lower()
