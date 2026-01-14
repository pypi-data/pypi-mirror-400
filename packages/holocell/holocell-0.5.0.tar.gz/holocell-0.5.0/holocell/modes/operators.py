"""
HoloCell — Custom Operators for GEPEvolver

Architectural operators: T (triangular), B (bilateral), S (six-nine)
"""

import math
from gepevolver import Operator, DEFAULT_OPERATORS

from ..operators import T as triangular_fn, B as bilateral_fn, S as six_nine_fn


def protected_triangular(n):
    """Protected triangular number."""
    try:
        n = int(abs(n))
        if n > 1000:
            return 0.0
        return triangular_fn(n)
    except:
        return 0.0


def protected_bilateral(x):
    """Protected bilateral covenant."""
    try:
        return bilateral_fn(x)
    except:
        return 0.0


def protected_six_nine(x):
    """Protected six-nine harmonic."""
    try:
        return six_nine_fn(x)
    except:
        return 0.0


def protected_inverse(x):
    """Protected multiplicative inverse."""
    if abs(x) < 1e-10:
        return 0.0
    return 1.0 / x


# HoloCell custom operators
HOLOCELL_OPERATORS = {
    'T': Operator('T', 1, protected_triangular, 'T'),
    'B': Operator('B', 1, protected_bilateral, 'B'),
    'S': Operator('S', 1, protected_six_nine, 'S'),
    'I': Operator('I', 1, protected_inverse, '⁻¹'),
}


def get_holocell_operators():
    """
    Get full operator set: standard + HoloCell architectural.
    """
    ops = DEFAULT_OPERATORS.copy()
    ops.update(HOLOCELL_OPERATORS)
    return ops
