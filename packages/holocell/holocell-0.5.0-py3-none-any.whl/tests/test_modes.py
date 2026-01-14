"""Tests for HoloCell modes (Five Modes of Sight)."""

import pytest
from holocell.modes import (
    # Mode 1: Fixed Focus
    evolve_constant,
    test_seeds,
    EvolutionResult,
    # Mode 2: Coherent Zoom
    evolve_coherent,
    CoherentResult,
    # Mode 3: Seth Mode
    evolve_seth,
    SethResult,
    # Mode 4: Moon Pools
    run_moon_pools,
    MoonPoolResult,
    # Mode 5: Coherence Test
    run_coherence_sweep,
    CoherenceSweepResult,
)
from holocell.modes.targets import CORE_TARGETS, CANDIDATE_SEEDS, get_target
from holocell.modes.glyphs import holocell_glyphs, coherent_glyphs
from holocell.modes.operators import get_holocell_operators


class TestTargets:
    """Tests for physics targets."""

    def test_core_targets_count(self):
        assert len(CORE_TARGETS) == 5

    def test_core_targets_have_values(self):
        for name, target in CORE_TARGETS.items():
            assert target.value > 0
            assert target.symbol is not None

    def test_get_target(self):
        target = get_target('alpha')
        assert target.value == pytest.approx(137.036, rel=0.001)

    def test_get_target_aliases(self):
        # Should handle different name formats
        t1 = get_target('alpha')
        t2 = get_target('proton')
        assert t1 is not t2

    def test_candidate_seeds(self):
        assert 136 in CANDIDATE_SEEDS
        assert len(CANDIDATE_SEEDS) >= 5


class TestGlyphs:
    """Tests for HoloCell-specific glyph sets."""

    def test_holocell_glyphs_creation(self):
        glyphs = holocell_glyphs(136)
        assert len(glyphs) > 0
        # Should contain the seed
        # (implementation detail, but seed should be accessible)

    def test_coherent_glyphs_creation(self):
        integers = [11, 16, 28, 36, 66]
        glyphs = coherent_glyphs(integers)
        assert len(glyphs) > 0


class TestOperators:
    """Tests for HoloCell custom operators."""

    def test_get_operators(self):
        ops = get_holocell_operators()
        assert '+' in ops
        assert '-' in ops
        assert 'T' in ops  # Triangular
        assert 'B' in ops  # Bilateral

    def test_triangular_operator(self):
        ops = get_holocell_operators()
        T_op = ops['T']
        assert T_op.arity == 1
        # T(16) = 136
        result = T_op.func(16)
        assert result == 136


class TestMode1FixedFocus:
    """Tests for Mode 1: Fixed Focus evolution."""

    def test_evolve_constant_returns_result(self):
        result = evolve_constant(
            'alpha',
            seed_value=136,
            generations=50,  # Quick test
            pop_size=30,
            verbose=False,
        )
        assert isinstance(result, EvolutionResult)
        assert result.target_name == 'alpha'
        assert result.seed_used == 136

    def test_evolve_constant_finds_reasonable_value(self):
        result = evolve_constant(
            'alpha',
            generations=200,
            pop_size=50,
            verbose=False,
        )
        # Should get within 10% at least
        assert result.error_percent < 10.0

    def test_test_seeds_returns_ranked_list(self):
        results = test_seeds(
            seeds=[136, 66],
            targets=['alpha'],
            generations_per_target=50,
            pop_size=30,
            verbose=False,
        )
        assert len(results) == 2
        # Should be ranked
        assert results[0].rank == 1
        assert results[1].rank == 2


class TestMode2CoherentZoom:
    """Tests for Mode 2: Coherent Zoom evolution."""

    def test_evolve_coherent_returns_result(self):
        result = evolve_coherent(
            integer_set_size=4,
            generations=50,
            pop_size=30,
            verbose=False,
        )
        assert isinstance(result, CoherentResult)
        assert len(result.discovered_integers) == 4

    def test_coherent_discovers_integers(self):
        result = evolve_coherent(
            integer_set_size=5,
            generations=100,
            pop_size=50,
            verbose=False,
        )
        # Should have discovered 5 integers
        assert len(result.discovered_integers) == 5
        # All should be positive
        assert all(i > 0 for i in result.discovered_integers)


class TestMode3SethMode:
    """Tests for Mode 3: Seth Mode evolution."""

    def test_evolve_seth_returns_result(self):
        result = evolve_seth(
            generations=50,
            pop_size=30,
            verbose=False,
        )
        assert isinstance(result, SethResult)
        assert len(result.archive) == 9  # Ennead

    def test_seth_partition(self):
        result = evolve_seth(
            generations=100,
            pop_size=50,
            verbose=False,
        )
        # Transmitted should be subset of archive
        assert len(result.transmitted) <= len(result.archive)
        # All transmitted should be in archive
        for t in result.transmitted:
            assert t in result.archive


class TestMode4MoonPools:
    """Tests for Mode 4: Moon Pools evolution."""

    def test_run_moon_pools_returns_result(self):
        result = run_moon_pools(
            num_pools=2,
            max_runtime_seconds=5,  # Quick test
            verbose=False,
        )
        assert isinstance(result, MoonPoolResult)
        assert result.generations > 0

    def test_moon_pools_has_constants(self):
        result = run_moon_pools(
            num_pools=2,
            max_runtime_seconds=10,
            verbose=False,
        )
        assert len(result.constants) > 0


class TestMode5CoherenceTest:
    """Tests for Mode 5: Coherence Test sweep."""

    def test_run_sweep_returns_result(self):
        result = run_coherence_sweep(
            max_corruption=2,
            trials_per_level=1,
            generations_per_trial=50,
            verbose=False,
        )
        assert isinstance(result, CoherenceSweepResult)
        assert len(result.levels) == 3  # 0, 1, 2

    def test_sweep_has_threshold(self):
        result = run_coherence_sweep(
            max_corruption=3,
            trials_per_level=1,
            generations_per_trial=50,
            verbose=False,
        )
        assert result.fault_tolerance_threshold >= 0
        assert result.baseline_overlap >= 0
