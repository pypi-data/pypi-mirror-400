"""
HoloCell - Architectural discovery engine for physics constants

T(16) = 136 as the eigenvalue of fundamental physics.

USAGE:
    from holocell import T, B, S, CRYSTAL, verify_all
    
    # The seed
    print(T(16))  # 136
    
    # Verify all constants
    results = verify_all()
    
    # Access specific constant
    proton = CRYSTAL["mp/me"]
    print(f"Error: {proton.error_percent:.2e}%")

METHODOLOGY REPLICATION:
    from holocell.evolve import evolve_constant, test_seeds, replicate_methodology
    
    # Stage 1: Evolve single constant
    result = evolve_constant("alpha")
    
    # Stage 2: Test unified seeds
    ranking = test_seeds()
    
    # Stage 3: Full replication
    results = replicate_methodology()

CLI:
    holocell verify              # Verify crystallized expressions
    holocell evolve <constant>   # Evolve expression for one constant
    holocell seed-test           # Run unified seed testing
    holocell replicate           # Full methodology replication
"""

__version__ = "0.2.0"

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
