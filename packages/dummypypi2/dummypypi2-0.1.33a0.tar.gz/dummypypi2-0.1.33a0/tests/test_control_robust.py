"""Docstring for tests.test_control_robust"""

import pytest
import numpy as np

import dummypypi2 as dp


def test_frob_norm():
    matrix = np.array([[1, 2], [3, 4]])
    expected_norm = np.sqrt(1 ** 2 + 2 ** 2 + 3 ** 2 + 4 ** 2)
    assert dp.control.frob_norm(matrix) == pytest.approx(expected_norm)