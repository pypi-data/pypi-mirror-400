"""
HoloCell - Architectural discovery engine for physics constants

T(16) = 136 as the eigenvalue of fundamental physics.
"""

__version__ = "0.1.0"

from .operators import T, B, S, triangular, bilateral, six_nine
from .constants import CRYSTAL, ARCHITECTURE, verify_all, verify_constant
from .magic import (
    FINE_STRUCTURE_INV,
    PROTON_ELECTRON_MASS,
    MUON_ELECTRON_MASS,
    WEINBERG_ANGLE,
    RYDBERG_MANTISSA,
    find_closest_magic,
    nearest_triangular,
)

__all__ = [
    # Operators
    "T", "B", "S",
    "triangular", "bilateral", "six_nine",
    # Constants
    "CRYSTAL", "ARCHITECTURE",
    "verify_all", "verify_constant",
    # Magic numbers
    "FINE_STRUCTURE_INV",
    "PROTON_ELECTRON_MASS",
    "MUON_ELECTRON_MASS",
    "WEINBERG_ANGLE",
    "RYDBERG_MANTISSA",
    "find_closest_magic",
    "nearest_triangular",
]
