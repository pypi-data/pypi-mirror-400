"""
HoloCell — Target Physics Constants

The five core constants and extended set for methodology validation.
"""

from dataclasses import dataclass
from typing import Dict

# === MEASURED VALUES ===

# Core 5 (from CODATA)
ALPHA_INV = 137.035999084        # Fine structure constant inverse
PROTON_ELECTRON = 1836.15267343  # mp/me
MUON_ELECTRON = 206.7682830      # μ/me  
WEINBERG = 0.23121               # sin²θW
RYDBERG = 1.0973731568160        # R∞ mantissa (×10^7 m⁻¹)

# Extended set for coherent evolution
ELECTRON_G = 2.00231930436256    # Electron g-factor
PLANCK_M = 5.391                 # Planck mass mantissa
PLANCK_EXP = 44                  # Planck mass exponent
RYDBERG_EXP = 7                  # Rydberg exponent
NEUTRON_PROTON = 1.00137841931   # mn/mp
AVOGADRO_LOG = 23.8              # log10(NA)
DIRAC_EXP = 40                   # Dirac large number exponent


@dataclass
class Target:
    """A physics constant target."""
    name: str
    symbol: str
    value: float
    min_bound: float
    max_bound: float


# Core 5 targets
CORE_TARGETS: Dict[str, Target] = {
    "alpha": Target("Fine structure inverse", "α⁻¹", ALPHA_INV, 136.0, 138.0),
    "proton": Target("Proton-electron mass", "mp/me", PROTON_ELECTRON, 1830.0, 1842.0),
    "muon": Target("Muon-electron mass", "μ/me", MUON_ELECTRON, 205.0, 208.5),
    "weinberg": Target("Weinberg angle", "sin²θW", WEINBERG, 0.20, 0.26),
    "rydberg": Target("Rydberg mantissa", "R∞", RYDBERG, 1.05, 1.15),
}

# Extended targets for coherent modes
EXTENDED_TARGETS: Dict[str, Target] = {
    **CORE_TARGETS,
    "electron_g": Target("Electron g-factor", "g_e", ELECTRON_G, 1.99, 2.01),
    "planck_m": Target("Planck mass mantissa", "m_P", PLANCK_M, 5.0, 6.0),
    "planck_exp": Target("Planck mass exponent", "exp_P", PLANCK_EXP, 40, 48),
    "rydberg_exp": Target("Rydberg exponent", "exp_R", RYDBERG_EXP, 5, 9),
    "neutron_proton": Target("Neutron-proton mass", "mn/mp", NEUTRON_PROTON, 0.99, 1.02),
    "avogadro_log": Target("Avogadro log10", "log_NA", AVOGADRO_LOG, 23.0, 24.5),
    "dirac_exp": Target("Dirac exponent", "exp_D", DIRAC_EXP, 38, 42),
}


def get_target(name: str) -> Target:
    """Get target by name, checking both core and extended."""
    if name in CORE_TARGETS:
        return CORE_TARGETS[name]
    if name in EXTENDED_TARGETS:
        return EXTENDED_TARGETS[name]
    raise ValueError(f"Unknown target: {name}")


# Architectural integer set (discovered)
ARCHITECTURE = [1, 7, 9, 11, 16, 28, 36, 44, 60, 66, 666]

# Candidate seeds for testing
CANDIDATE_SEEDS = [136, 137, 66, 36, 120, 45, 55, 78, 91, 105]
