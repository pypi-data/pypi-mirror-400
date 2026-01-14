"""
HoloCell Magic Numbers

Physics constants and helper functions for discovery.
"""

import math
from typing import NamedTuple, Optional


class MagicNumber(NamedTuple):
    name: str
    value: float
    domain: str
    precision: float


# Measured values (CODATA 2018)
FINE_STRUCTURE_INV = MagicNumber("α⁻¹", 137.035999084, "electromagnetic", 1e-4)
PROTON_ELECTRON_MASS = MagicNumber("mp/me", 1836.15267343, "particle", 1e-3)
MUON_ELECTRON_MASS = MagicNumber("μ/me", 206.768283, "particle", 1e-4)
WEINBERG_ANGLE = MagicNumber("sin²θW", 0.23121, "electroweak", 1e-4)
RYDBERG_MANTISSA = MagicNumber("R∞", 1.097373156816, "atomic", 1e-6)

# Mathematical constants
PI = MagicNumber("π", math.pi, "mathematical", 1e-10)
E = MagicNumber("e", math.e, "mathematical", 1e-10)
PHI = MagicNumber("φ", (1 + math.sqrt(5)) / 2, "mathematical", 1e-10)

# Triangular numbers
T_VALUES = [
    MagicNumber("T(8)", 36, "triangular", 0),
    MagicNumber("T(11)", 66, "triangular", 0),
    MagicNumber("T(16)", 136, "triangular", 0),
    MagicNumber("T(36)", 666, "triangular", 0),
]

# Engine architecture
ENGINE_VALUES = [
    MagicNumber("wheel", 16, "engine", 0),
    MagicNumber("spine", 9, "engine", 0),
    MagicNumber("phonemes", 11, "engine", 0),
    MagicNumber("decans", 36, "engine", 0),
    MagicNumber("lunar", 28, "engine", 0),
]

ALL_MAGIC_NUMBERS = [
    FINE_STRUCTURE_INV,
    PROTON_ELECTRON_MASS,
    MUON_ELECTRON_MASS,
    WEINBERG_ANGLE,
    RYDBERG_MANTISSA,
    PI, E, PHI,
    *T_VALUES,
    *ENGINE_VALUES,
]


def find_closest_magic(value: float) -> tuple[MagicNumber, float]:
    """
    Find the magic number closest to a given value.
    
    Args:
        value: The value to match
    
    Returns:
        Tuple of (closest MagicNumber, distance)
    """
    closest = ALL_MAGIC_NUMBERS[0]
    min_dist = abs(value - closest.value)
    
    for magic in ALL_MAGIC_NUMBERS:
        dist = abs(value - magic.value)
        if dist < min_dist:
            min_dist = dist
            closest = magic
    
    return closest, min_dist


def nearest_triangular(value: float) -> tuple[int, int, float]:
    """
    Find the nearest triangular number to a value.
    
    Args:
        value: The value to match
    
    Returns:
        Tuple of (index n, T(n), distance)
    """
    # Solve n(n+1)/2 = value for n
    n = int((-1 + math.sqrt(1 + 8 * value)) / 2)
    
    t1 = n * (n + 1) // 2
    t2 = (n + 1) * (n + 2) // 2
    
    d1 = abs(value - t1)
    d2 = abs(value - t2)
    
    if d1 <= d2:
        return n, t1, d1
    else:
        return n + 1, t2, d2
