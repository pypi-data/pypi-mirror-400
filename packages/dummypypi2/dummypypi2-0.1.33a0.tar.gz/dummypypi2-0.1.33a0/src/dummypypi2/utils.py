"""
Script which contains various utility functions.

NOTE: As a convention, all vectors of length n are 1D vectors of shape (n,) which means no distinction is made between column and row vectors
FROM: https://python-control.readthedocs.io/en/0.9.4/conventions.html  # nopep8

NOTE: To remove all comments marked "#:" use the following steps: 1) Find the maximum number of indentations n, i.e. tabs (equivelant to four spaces), 2) Using "find and replace" (CTRL + R), search for "<n x 4 spaces>#:.*$\n" and replace with nothing, 3) Repeat step 2 for n - 1 indentations until n = 1
FROM: https://stackoverflow.com/questions/69060850/intellij-how-to-delete-all-line-containing-annotation  # nopep8
FROM: https://intellij-support.jetbrains.com/hc/en-us/community/posts/115000142590-How-can-you-find-delete-lines-not-just-replace-with-nothing-  # nopep8
"""

from functools import cache, wraps
from typing import TypeVar, TypeAlias, Callable, Any, Literal
import warnings

import numpy as np
import numpy.typing as npt

from . import _config as cfg


def get_signed_angle(v_1: npt.NDArray[np.float64], v_2: npt.NDArray[np.float64], look: npt.NDArray[np.float64]) -> float:
    """
    FROM: https://github.com/lace/vg/blob/main/vg/core.py  #nopep8
    """

    #: Compute the dot product (normalized)
    dot_products_normalized = np.dot(v_1, v_2) / np.linalg.norm(v_1, ord=2) / np.linalg.norm(v_2, ord=2)
    #: Compute the unsigned angle
    angle = np.arccos(np.clip(dot_products_normalized, -1.0, 1.0))  # Clipping is needed due to numerical issues
    #: The sign of (A x B) dot look gives the sign of the angle. Here, angle > 0 means clockwise, angle < 0 is counterclockwise.
    sign = np.array(np.sign(np.cross(v_1, v_2).dot(look)))
    #: An angle of 0 means collinear: 0 or 180. Let's call that clockwise.
    sign[sign == 0] = 1
    #: Compute the signed angle
    signed_angle = sign * angle
    #: Return the result
    return float(signed_angle)


def is_prime(n: int) -> bool:
    """Check if a number is prime"""
    if n <= 1:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True


def divide(a: float, b: float) -> float:
    """Divide two numbers, returning np.inf if division by zero occurs"""
    if np.isclose(b, 0.0):
        raise ValueError("Denominator is too close to zero.")
    return a / b


def is_close(a: float, b: float) -> bool:
    """Check if two floating-point numbers are close within global tolerances"""
    return np.isclose(a, b, rtol=cfg.RTOL, atol=cfg.ATOL).item()


def main() -> None:
    a = 0.9
    b = 1.0

    print(is_close(a, b))


if __name__ == "__main__":
    main()