"""
HoloCell Methodology — Trivial Replication Interface

This module provides high-level functions to replicate each methodology stage
described in the HoloCell papers.

STAGES:
    1. evolve_constant() - Evolve expression for a single constant
    2. test_seeds() - Compare candidate seeds to find unified eigenvalue
    3. replicate_methodology() - Full methodology replication

Usage:
    from holocell.evolve import evolve_constant, test_seeds, replicate_methodology
    
    # Stage 1: Evolve single constant
    result = evolve_constant("alpha")
    print(f"Expression: {result.expression}")
    print(f"Error: {result.error_percent:.2e}%")
    
    # Stage 2: Test unified seeds
    ranking = test_seeds()
    print(ranking[0])  # Best seed (T(16)=136)
    
    # Stage 3: Full replication
    results = replicate_methodology()
"""

from dataclasses import dataclass
from typing import List, Dict, Optional
import time

from .glyphs import GlyphSet
from .engine import evolve_with_glyphs
from .targets import TARGETS, TARGET_NAMES, CANDIDATE_SEEDS, get_target


@dataclass
class EvolutionResult:
    """Result from evolving a single constant."""
    target_name: str
    target_value: float
    computed_value: float
    expression: str
    error_percent: float
    fitness: float
    generations: int
    elapsed_seconds: float
    
    def __repr__(self):
        return (
            f"EvolutionResult({self.target_name})\n"
            f"  Expression: {self.expression}\n"
            f"  Computed:   {self.computed_value}\n"
            f"  Target:     {self.target_value}\n"
            f"  Error:      {self.error_percent:.2e}%"
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


# =============================================================================
# STAGE 1: EVOLVE SINGLE CONSTANT
# =============================================================================

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
    Stage 1: Evolve an expression for a single constant.
    
    Parameters:
        target_name: Constant name ("alpha", "proton", "muon", "weinberg", "rydberg")
        seed_value: Seed to use as privileged terminal (default: 136 = T(16))
        pop_size: Population size (default: 300)
        head_len: Gene head length (default: 12)
        generations: Max generations (default: 1000)
        verbose: Print progress (default: True)
        random_seed: For reproducibility (optional)
    
    Returns:
        EvolutionResult with expression and statistics
    
    Example:
        >>> result = evolve_constant("alpha")
        >>> print(result.expression)
        (seed(136) + ((e / 36) + seed(136) + π) / (seed(136) - φ))
    """
    target = get_target(target_name)
    glyphs = GlyphSet.holocell(seed=seed_value)
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"EVOLVING: {target.symbol} ({target.name})")
        print(f"Target value: {target.value}")
        print(f"Seed: {seed_value}")
        print(f"{'='*60}\n")
    
    start = time.time()
    
    (best_fit, best_gene, best_val, best_expr), population, engine = evolve_with_glyphs(
        glyph_set=glyphs,
        target=target.value,
        pop_size=pop_size,
        head_len=head_len,
        generations=generations,
        verbose=verbose,
        seed=random_seed,
    )
    
    elapsed = time.time() - start
    error_pct = abs(best_val - target.value) / target.value * 100
    
    if verbose:
        print(f"\n{'='*60}")
        print(f"RESULT: {target.symbol}")
        print(f"Expression: {best_expr}")
        print(f"Computed:   {best_val}")
        print(f"Target:     {target.value}")
        print(f"Error:      {error_pct:.2e}%")
        print(f"Time:       {elapsed:.1f}s")
        print(f"{'='*60}\n")
    
    return EvolutionResult(
        target_name=target_name,
        target_value=target.value,
        computed_value=best_val,
        expression=best_expr,
        error_percent=error_pct,
        fitness=best_fit,
        generations=generations,
        elapsed_seconds=elapsed,
    )


# =============================================================================
# STAGE 2: TEST UNIFIED SEEDS
# =============================================================================

def test_seeds(
    seeds: List[int] = None,
    targets: List[str] = None,
    generations_per_target: int = 500,
    pop_size: int = 200,
    verbose: bool = True,
) -> List[SeedTestResult]:
    """
    Stage 2: Test candidate seeds to find the unified eigenvalue.
    
    For each seed, evolves expressions for all target constants and
    measures total error. Ranks seeds by total error.
    
    Parameters:
        seeds: Candidate seeds to test (default: CANDIDATE_SEEDS)
        targets: Constants to test (default: all 5)
        generations_per_target: Generations per evolution (default: 500)
        pop_size: Population size (default: 200)
        verbose: Print progress (default: True)
    
    Returns:
        List of SeedTestResult, sorted by total error (best first)
    
    Example:
        >>> ranking = test_seeds()
        >>> print(ranking[0])
        SeedTestResult(seed=136, total_error=1.89e-05, rank=1)
    """
    if seeds is None:
        seeds = CANDIDATE_SEEDS
    if targets is None:
        targets = TARGET_NAMES
    
    results = []
    
    if verbose:
        print("\n" + "="*70)
        print("UNIFIED SEED TESTING")
        print(f"Testing {len(seeds)} seeds against {len(targets)} constants")
        print("="*70 + "\n")
    
    for seed in seeds:
        if verbose:
            print(f"\n--- Testing seed: {seed} ---")
        
        individual_errors = {}
        total_error = 0.0
        
        for target_name in targets:
            target = get_target(target_name)
            glyphs = GlyphSet.seed_test(seed=seed)
            
            (_, _, best_val, _), _, _ = evolve_with_glyphs(
                glyph_set=glyphs,
                target=target.value,
                pop_size=pop_size,
                head_len=10,
                generations=generations_per_target,
                verbose=False,
            )
            
            error = abs(best_val - target.value) / target.value * 100
            individual_errors[target_name] = error
            total_error += error
            
            if verbose:
                print(f"  {target.symbol}: {error:.2e}%")
        
        results.append(SeedTestResult(
            seed=seed,
            total_error=total_error,
            individual_errors=individual_errors,
            rank=0,  # Will be set after sorting
        ))
        
        if verbose:
            print(f"  TOTAL: {total_error:.2e}%")
    
    # Sort by total error and assign ranks
    results.sort(key=lambda r: r.total_error)
    for i, r in enumerate(results):
        r.rank = i + 1
    
    if verbose:
        print("\n" + "="*70)
        print("SEED RANKING")
        print("="*70)
        for r in results[:5]:
            print(f"  #{r.rank}: seed={r.seed:>3d} | total_error={r.total_error:.2e}%")
        print("="*70 + "\n")
    
    return results


# =============================================================================
# STAGE 3: FULL METHODOLOGY REPLICATION
# =============================================================================

def replicate_methodology(
    full_seed_test: bool = False,
    verbose: bool = True,
) -> Dict[str, EvolutionResult]:
    """
    Stage 3: Replicate the full HoloCell methodology.
    
    1. (Optional) Run unified seed testing to confirm T(16)=136
    2. Evolve expressions for all 5 constants using T(16)=136
    3. Report results and errors
    
    Parameters:
        full_seed_test: Run seed comparison (slower, default: False)
        verbose: Print progress (default: True)
    
    Returns:
        Dict mapping constant names to EvolutionResult
    
    Example:
        >>> results = replicate_methodology()
        >>> for name, r in results.items():
        ...     print(f"{name}: {r.error_percent:.2e}%")
    """
    if verbose:
        print("\n" + "="*70)
        print("HOLOCELL METHODOLOGY REPLICATION")
        print("="*70)
    
    # Optional: Run seed test
    if full_seed_test:
        if verbose:
            print("\nPhase 1: Unified Seed Testing")
        ranking = test_seeds(verbose=verbose)
        best_seed = ranking[0].seed
        if verbose:
            print(f"\nBest seed identified: {best_seed}")
    else:
        best_seed = 136
        if verbose:
            print(f"\nUsing known best seed: T(16) = {best_seed}")
    
    # Evolve all constants
    if verbose:
        print("\nPhase 2: Evolving expressions for all constants")
    
    results = {}
    for target_name in TARGET_NAMES:
        result = evolve_constant(
            target_name,
            seed_value=best_seed,
            verbose=verbose,
        )
        results[target_name] = result
    
    # Summary
    if verbose:
        print("\n" + "="*70)
        print("METHODOLOGY REPLICATION COMPLETE")
        print("="*70)
        print(f"\nSeed: T(16) = {best_seed}")
        print("\nResults:")
        for name, r in results.items():
            target = get_target(name)
            print(f"  {target.symbol:>8}: {r.error_percent:.2e}% error")
        
        total = sum(r.error_percent for r in results.values())
        print(f"\n  TOTAL ERROR: {total:.2e}%")
        print("="*70 + "\n")
    
    return results
