"""This is a dummy implementation of various robust control algorithms"""

import numpy as np
import numpy.typing as npt


def frob_norm(matrix: npt.ArrayLike) -> float:
    """Compute the Frobenius norm of a matrix"""
    return np.linalg.norm(matrix, 'fro').item()