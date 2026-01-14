"""
Target Constants for HoloCell Methodology

CODATA 2018 values for the five fundamental constants.
"""

from typing import NamedTuple


class Target(NamedTuple):
    """A target constant for evolution."""
    name: str
    symbol: str
    value: float
    description: str


# === TARGET CONSTANTS (CODATA 2018) ===

TARGETS = {
    "alpha": Target(
        name="fine structure constant inverse",
        symbol="α⁻¹",
        value=137.035999084,
        description="Electromagnetic coupling strength"
    ),
    "proton": Target(
        name="proton-electron mass ratio",
        symbol="mp/me",
        value=1836.15267343,
        description="Particle mass ratio"
    ),
    "muon": Target(
        name="muon-electron mass ratio",
        symbol="μ/me",
        value=206.7682830,
        description="Lepton mass ratio"
    ),
    "weinberg": Target(
        name="Weinberg angle",
        symbol="sin²θW",
        value=0.23121,
        description="Electroweak mixing parameter"
    ),
    "rydberg": Target(
        name="Rydberg constant mantissa",
        symbol="R∞",
        value=1.0973731568160,
        description="Atomic spectrum constant"
    ),
}

TARGET_NAMES = list(TARGETS.keys())


# === CANDIDATE SEEDS FOR TESTING ===

CANDIDATE_SEEDS = [
    136,   # T(16) — THE WINNER
    137,   # B(T(16)) — commonly cited
    66,    # T(11)
    36,    # T(8)
    11,    # prime
    28,    # T(7)
    21,    # T(6)
    15,    # T(5)
    10,    # T(4)
    6,     # T(3)
    3,     # T(2)
]


def get_target(name: str) -> Target:
    """Get target by name or alias."""
    # Normalize name
    name = name.lower().strip()
    
    # Direct match
    if name in TARGETS:
        return TARGETS[name]
    
    # Aliases
    aliases = {
        "α": "alpha",
        "alpha-1": "alpha",
        "fine structure": "alpha",
        "mp/me": "proton",
        "proton-electron": "proton",
        "μ/me": "muon",
        "muon-electron": "muon",
        "sin2θw": "weinberg",
        "weak angle": "weinberg",
        "r∞": "rydberg",
        "rydberg": "rydberg",
    }
    
    normalized = aliases.get(name, name)
    if normalized in TARGETS:
        return TARGETS[normalized]
    
    raise ValueError(f"Unknown target: {name}. Valid: {TARGET_NAMES}")
