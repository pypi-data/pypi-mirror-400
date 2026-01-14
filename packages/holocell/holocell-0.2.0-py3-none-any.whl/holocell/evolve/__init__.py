"""
HoloCell Evolution Engine

Gene Expression Programming integration for methodology replication.
Enables trivial reproduction of each discovery stage.

METHODOLOGY STAGES:
1. evolve_constant() - Evolve expression for single constant
2. test_seeds() - Compare candidate seeds (finds T(16)=136)
3. replicate_methodology() - Full discovery replication

Usage:
    from holocell.evolve import evolve_constant, test_seeds
    
    # Stage 1: Evolve single constant
    result = evolve_constant("alpha", generations=1000)
    
    # Stage 2: Test unified seeds
    ranking = test_seeds([136, 137, 66, 36])
    
    # Stage 3: Full replication
    results = replicate_methodology()
"""

from .glyphs import GlyphSet, Glyph
from .engine import GlyphGEP, evolve_with_glyphs
from .targets import TARGETS, TARGET_NAMES
from .methodology import (
    evolve_constant,
    test_seeds,
    replicate_methodology,
    SeedTestResult,
    EvolutionResult,
)

__all__ = [
    # Glyphs
    "GlyphSet",
    "Glyph",
    # Engine
    "GlyphGEP",
    "evolve_with_glyphs",
    # Targets
    "TARGETS",
    "TARGET_NAMES",
    # Methodology
    "evolve_constant",
    "test_seeds",
    "replicate_methodology",
    "SeedTestResult",
    "EvolutionResult",
]
