"""
HoloCell Modes — The Five Modes of Sight

Mode 1: Fixed Focus    — Standard GEP with fixed terminals
Mode 2: Coherent Zoom  — Co-evolve integer set itself
Mode 3: Seth Mode      — Dual set partition (archive/transmitted)
Mode 4: Moon Pools     — Multi-pool eigenvalue triangulation
Mode 5: Coherence Test — N-node corruption sweep for fault tolerance

All modes use GEPEvolver for the genetic engine.
"""

from .fixed_focus import evolve_constant, test_seeds, EvolutionResult
from .coherent_zoom import evolve_coherent, CoherentResult
from .seth_mode import evolve_seth, SethResult
from .moon_pools import run_moon_pools, MoonPoolResult
from .coherence_test import run_coherence_sweep, CoherenceSweepResult

__all__ = [
    # Mode 1: Fixed Focus
    "evolve_constant",
    "test_seeds",
    "EvolutionResult",
    # Mode 2: Coherent Zoom
    "evolve_coherent",
    "CoherentResult",
    # Mode 3: Seth Mode
    "evolve_seth",
    "SethResult",
    # Mode 4: Moon Pools
    "run_moon_pools",
    "MoonPoolResult",
    # Mode 5: Coherence Test
    "run_coherence_sweep",
    "CoherenceSweepResult",
]
