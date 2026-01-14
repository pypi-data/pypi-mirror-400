"""
HoloCell — Mode 1: Fixed Focus

Standard GEP evolution with fixed terminals.
Evolve expression for a single physics constant using T(16)=136 as seed.

This is the baseline mode that established the crystallized expressions.
"""

import time
from dataclasses import dataclass
from typing import List, Dict, Optional

from gepevolver import evolve_with_glyphs, EvolutionResult as GEPResult

from .targets import CORE_TARGETS, CANDIDATE_SEEDS, get_target, Target
from .glyphs import holocell_glyphs, seed_test_glyphs
from .operators import get_holocell_operators


@dataclass
class EvolutionResult:
    """Result from fixed-focus evolution."""
    target_name: str
    target_value: float
    computed_value: float
    expression: str
    error_percent: float
    fitness: float
    generations: int
    elapsed_seconds: float
    seed_used: int

    def __repr__(self):
        return (
            f"EvolutionResult({self.target_name})\n"
            f"  Expression: {self.expression}\n"
            f"  Computed:   {self.computed_value}\n"
            f"  Target:     {self.target_value}\n"
            f"  Error:      {self.error_percent:.2e}%"
        )


def evolve_constant(
    target_name: str,
    seed_value: int = 136,
    pop_size: int = 300,
    head_len: int = 12,
    generations: int = 1000,
    verbose: bool = True,
    random_seed: int = None,
) -> EvolutionResult:
    """
    Mode 1: Evolve an expression for a single physics constant.

    Uses fixed terminals from the architectural glyph set.
    The seed (default T(16)=136) is a privileged terminal.

    Args:
        target_name: Constant name ("alpha", "proton", "muon", "weinberg", "rydberg")
        seed_value: Seed to use as privileged terminal (default: 136)
        pop_size: Population size
        head_len: Gene head length
        generations: Maximum generations
        verbose: Print progress
        random_seed: For reproducibility

    Returns:
        EvolutionResult with expression and statistics
    """
    target = get_target(target_name)
    glyphs = holocell_glyphs(seed=seed_value)
    operators = get_holocell_operators()

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"MODE 1: FIXED FOCUS — {target.symbol} ({target.name})")
        print(f"Target: {target.value}")
        print(f"Seed: {seed_value}")
        print(f"{'=' * 60}\n")

    start = time.time()

    result, population, engine = evolve_with_glyphs(
        glyph_set=glyphs,
        target=target.value,
        pop_size=pop_size,
        head_len=head_len,
        generations=generations,
        operators=operators,
        verbose=verbose,
        seed=random_seed,
    )

    elapsed = time.time() - start
    error_pct = abs(result.value - target.value) / target.value * 100

    if verbose:
        print(f"\n{'=' * 60}")
        print(f"RESULT: {target.symbol}")
        print(f"Expression: {result.expression}")
        print(f"Computed:   {result.value}")
        print(f"Target:     {target.value}")
        print(f"Error:      {error_pct:.2e}%")
        print(f"Time:       {elapsed:.1f}s")
        print(f"{'=' * 60}\n")

    return EvolutionResult(
        target_name=target_name,
        target_value=target.value,
        computed_value=result.value,
        expression=result.expression,
        error_percent=error_pct,
        fitness=result.fitness,
        generations=result.generations_run,
        elapsed_seconds=elapsed,
        seed_used=seed_value,
    )


@dataclass
class SeedTestResult:
    """Result from testing a candidate seed."""
    seed: int
    total_error: float
    individual_errors: Dict[str, float]
    rank: int

    def __repr__(self):
        return f"SeedTestResult(seed={self.seed}, total_error={self.total_error:.2e}, rank={self.rank})"


def test_seeds(
    seeds: List[int] = None,
    targets: List[str] = None,
    generations_per_target: int = 500,
    pop_size: int = 200,
    verbose: bool = True,
) -> List[SeedTestResult]:
    """
    Test candidate seeds to find the unified eigenvalue.

    For each seed, evolves expressions for all target constants
    and measures total error. Ranks seeds by total error.

    Args:
        seeds: Candidate seeds to test (default: CANDIDATE_SEEDS)
        targets: Constants to test (default: core 5)
        generations_per_target: Generations per evolution
        pop_size: Population size
        verbose: Print progress

    Returns:
        List of SeedTestResult, sorted by total error (best first)
    """
    if seeds is None:
        seeds = CANDIDATE_SEEDS
    if targets is None:
        targets = list(CORE_TARGETS.keys())

    operators = get_holocell_operators()
    results = []

    if verbose:
        print("\n" + "=" * 70)
        print("MODE 1: SEED TESTING")
        print(f"Testing {len(seeds)} seeds against {len(targets)} constants")
        print("=" * 70 + "\n")

    for seed in seeds:
        if verbose:
            print(f"\n--- Testing seed: {seed} ---")

        individual_errors = {}
        total_error = 0.0

        for target_name in targets:
            target = get_target(target_name)
            glyphs = seed_test_glyphs(seed=seed)

            result, _, _ = evolve_with_glyphs(
                glyph_set=glyphs,
                target=target.value,
                pop_size=pop_size,
                head_len=10,
                generations=generations_per_target,
                operators=operators,
                verbose=False,
            )

            error = abs(result.value - target.value) / target.value * 100
            individual_errors[target_name] = error
            total_error += error

            if verbose:
                print(f"  {target.symbol}: {error:.2e}%")

        results.append(SeedTestResult(
            seed=seed,
            total_error=total_error,
            individual_errors=individual_errors,
            rank=0,
        ))

        if verbose:
            print(f"  TOTAL: {total_error:.2e}%")

    # Sort and assign ranks
    results.sort(key=lambda r: r.total_error)
    for i, r in enumerate(results):
        r.rank = i + 1

    if verbose:
        print("\n" + "=" * 70)
        print("SEED RANKING")
        print("=" * 70)
        for r in results[:5]:
            print(f"  #{r.rank}: seed={r.seed:>3d} | total_error={r.total_error:.2e}%")
        print("=" * 70 + "\n")

    return results
