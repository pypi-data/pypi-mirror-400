"""
HoloCell Crystal - The crystallized expressions

These expressions achieve extraordinary precision using T(16) = 136 as seed.
"""

import math
from typing import NamedTuple
from .operators import T, B, S


# Transcendentals
π = math.pi
e = math.e
φ = (1 + math.sqrt(5)) / 2


class CrystalConstant(NamedTuple):
    name: str
    symbol: str
    expression: str
    computed: float
    measured: float
    error_percent: float


# === ARCHITECTURE ===
ARCHITECTURE = [1, 7, 9, 11, 16, 28, 36, 44, 60, 66, 666]

# === THE SEED ===
SEED = T(16)  # = 136

# === TRINITION EXTENSION ===
TRINITION = SEED * 3  # = 408


def _mp_me() -> float:
    """mp/me: T(16) × 3 × (9/2) + (11 - 1/T(16))/72"""
    return T(16) * 3 * (9/2) + (11 - 1/T(16)) / 72


def _rydberg() -> float:
    """R∞: B(T(11) × (√(T(16) + e) + 1/36 + 666)⁻¹)"""
    inner = math.sqrt(T(16) + e) + 1/36 + 666
    return B(T(11) * (1 / inner))


def _alpha_inv() -> float:
    """α⁻¹: T(16) + (((e/36 + T(16)) + π) / (T(16) - φ))"""
    return T(16) + (((e/36 + T(16)) + π) / (T(16) - φ))


def _muon_me() -> float:
    """μ/me: (16 + T(16) + T(16)/28 + 44) + B(S(T(16))/60)"""
    return (16 + T(16) + T(16)/28 + 44) + B(S(T(16))/60)


def _weinberg() -> float:
    """sin²θW: √((28 - (π + 36/T(16))⁻¹ - 9)⁻¹)"""
    inner = 28 - (1 / (π + 36/T(16))) - 9
    return math.sqrt(1 / inner)


# === MEASURED VALUES (CODATA 2018) ===
MEASURED = {
    "mp/me": 1836.15267343,
    "R∞": 1.097373156816,
    "α⁻¹": 137.035999084,
    "μ/me": 206.768283,
    "sin²θW": 0.23121,
}

# === COMPUTED VALUES ===
COMPUTED = {
    "mp/me": _mp_me(),
    "R∞": _rydberg(),
    "α⁻¹": _alpha_inv(),
    "μ/me": _muon_me(),
    "sin²θW": _weinberg(),
}

# === EXPRESSIONS (human readable) ===
EXPRESSIONS = {
    "mp/me": "T(16) × 3 × (9/2) + (11 - 1/T(16))/72",
    "R∞": "B(T(11) × (√(T(16) + e) + 1/36 + 666)⁻¹)",
    "α⁻¹": "T(16) + (((e/36 + T(16)) + π) / (T(16) - φ))",
    "μ/me": "(16 + T(16) + T(16)/28 + 44) + B(S(T(16))/60)",
    "sin²θW": "√((28 - (π + 36/T(16))⁻¹ - 9)⁻¹)",
}


def _error_percent(name: str) -> float:
    """Calculate error percentage for a constant."""
    computed = COMPUTED[name]
    measured = MEASURED[name]
    return abs(computed - measured) / measured * 100


# === THE CRYSTAL ===
CRYSTAL = {
    "mp/me": CrystalConstant(
        name="proton-electron mass ratio",
        symbol="mp/me",
        expression=EXPRESSIONS["mp/me"],
        computed=COMPUTED["mp/me"],
        measured=MEASURED["mp/me"],
        error_percent=_error_percent("mp/me"),
    ),
    "R∞": CrystalConstant(
        name="Rydberg constant mantissa",
        symbol="R∞",
        expression=EXPRESSIONS["R∞"],
        computed=COMPUTED["R∞"],
        measured=MEASURED["R∞"],
        error_percent=_error_percent("R∞"),
    ),
    "α⁻¹": CrystalConstant(
        name="fine structure constant inverse",
        symbol="α⁻¹",
        expression=EXPRESSIONS["α⁻¹"],
        computed=COMPUTED["α⁻¹"],
        measured=MEASURED["α⁻¹"],
        error_percent=_error_percent("α⁻¹"),
    ),
    "μ/me": CrystalConstant(
        name="muon-electron mass ratio",
        symbol="μ/me",
        expression=EXPRESSIONS["μ/me"],
        computed=COMPUTED["μ/me"],
        measured=MEASURED["μ/me"],
        error_percent=_error_percent("μ/me"),
    ),
    "sin²θW": CrystalConstant(
        name="Weinberg angle",
        symbol="sin²θW",
        expression=EXPRESSIONS["sin²θW"],
        computed=COMPUTED["sin²θW"],
        measured=MEASURED["sin²θW"],
        error_percent=_error_percent("sin²θW"),
    ),
}


def verify_constant(name: str, tolerance_percent: float = 0.01) -> bool:
    """
    Verify a crystal constant is within tolerance.
    
    Args:
        name: Constant name (e.g., "mp/me", "α⁻¹")
        tolerance_percent: Maximum allowed error percentage
    
    Returns:
        True if within tolerance
    """
    if name not in CRYSTAL:
        raise ValueError(f"Unknown constant: {name}")
    return CRYSTAL[name].error_percent <= tolerance_percent


def verify_all(tolerance_percent: float = 0.01) -> dict[str, bool]:
    """
    Verify all crystal constants.
    
    Args:
        tolerance_percent: Maximum allowed error percentage
    
    Returns:
        Dict mapping constant names to pass/fail status
    """
    return {name: verify_constant(name, tolerance_percent) for name in CRYSTAL}


def print_crystal():
    """Print all crystal constants with their values and errors."""
    print("=" * 70)
    print("HOLOCELL CRYSTAL - T(16) = 136")
    print("=" * 70)
    print()
    for name, c in CRYSTAL.items():
        print(f"{c.symbol}: {c.name}")
        print(f"  Expression: {c.expression}")
        print(f"  Computed:   {c.computed}")
        print(f"  Measured:   {c.measured}")
        print(f"  Error:      {c.error_percent:.2e}%")
        print()
    print("=" * 70)
    print(f"Seed: T(16) = {SEED}")
    print(f"Trinition: T(16) × 3 = {TRINITION}")
    print(f"Architecture: {ARCHITECTURE}")
    print("=" * 70)
