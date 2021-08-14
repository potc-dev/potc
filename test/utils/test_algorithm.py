import pytest

from potc.utils import topological


@pytest.mark.unittest
class TestUtilsAlgorithm:
    def test_topological(self):
        assert topological(0, []) == []
        assert topological(3, []) == [0, 1, 2]
        assert topological(3, [(0, 1), (2, 1)]) == [0, 2, 1]

        with pytest.raises(ArithmeticError):
            topological(3, [(0, 1), (2, 1), (1, 0)])
