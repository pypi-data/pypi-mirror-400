import pytest
import numpy as np

import dummypypi2 as dp

@pytest.mark.parametrize("number, expected", [
    (2, True),
    (3, True),
    (4, False),
    (17, True),
    (18, False),
    (19, True),
    (20, False),
    (1, False),
    (0, False),
    (-5, False),
])


def test_is_prime(number, expected):
    assert dp.is_prime(number) == expected, f"is_prime({number}) should be {expected}"


def test_get_signed_angle():
    a, b = np.array([1, 0, 0]), np.array([0, 1, 2])
    look = np.array([0, 0, 1])
    assert np.degrees(dp.get_signed_angle(a, b, look=look)) == pytest.approx(90)
    assert np.degrees(dp.get_signed_angle(a, b, np.cross(a, b))) == pytest.approx(90)


def test_get_signed_angle_argument_swap():
    a, b = np.array([1, 0, 0]), np.array([0, 1, 2])
    look = np.array([0, 0, 1])
    assert np.degrees(dp.get_signed_angle(a, b, look=look)) == pytest.approx(90), "Angle from a to b should be 90 degrees counter-clockwise (which is positive in the look=[0, 0, 1] direction)"
    assert np.degrees(dp.get_signed_angle(b, a, look=look)) == pytest.approx(-90), "Swapping the arguments should yield -90 degrees, as dg.get_signed_angle(a, b, ...) = -dg.get_signed_angle(b, a, ...)"
    

def test_divide():
    assert dp.divide(4, 2) == 2.0, "4 divided by 2 should be 2"
    with pytest.raises(ValueError):
        dp.divide(1, 0)