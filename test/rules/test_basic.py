import pytest

from potc.testing import provement
from potc.translate import BlankTranslator, Translator


@pytest.mark.unittest
class TestRulesProvementBasic(provement()):
    pass


@pytest.mark.unittest
class TestRulesProvementBlank(provement(BlankTranslator)):
    pass


@pytest.mark.unittest
class TestRulesProvementCommon(provement(Translator)):
    pass
