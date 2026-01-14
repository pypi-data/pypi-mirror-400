"""
HoloCell — Mode 4: Moon Pools

4 independent evolutionary pools, each tracking all 5 constants.
Where the pools' settling bands CROSS = eigenvalue signal.

The centroid of crossing bands = the hidden eigenstate.

Clamp detection: when a pool oscillates between exactly 2 values,
the eigenvalue is bracketed.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Optional

from gepevolver import GlyphGEP, Gene, evolve_with_glyphs

from .targets import CORE_TARGETS, ARCHITECTURE
from .glyphs import holocell_glyphs
from .operators import get_holocell_operators


@dataclass
class PoolState:
    """State of a single evolutionary pool."""
    id: int
    best_values: Dict[str, float]       # Current best value per constant
    best_fitness: Dict[str, float]      # Best fitness per constant
    history: Dict[str, List[float]]     # History of best values


@dataclass
class CrossingBand:
    """Analysis of where pool bands cross."""
    constant: str
    bands: List[Tuple[float, float]]  # (min, max) per pool
    centroid: float                    # Estimated eigenvalue
    spread: float                      # Width of crossing region
    is_clamped: bool                   # Oscillating between 2 values?


@dataclass
class MoonPoolResult:
    """Result from moon pools evolution."""
    constants: Dict[str, Dict]  # {name: {eigenstate, spread, delta_percent}}
    pool_values: Dict[str, List[float]]  # Final values per pool
    crossing_bands: Dict[str, CrossingBand]
    generations: int
    elapsed_seconds: float

    def __repr__(self):
        lines = ["MoonPoolResult"]
        for name, data in self.constants.items():
            lines.append(f"  {name}: eigenstate={data['eigenstate']:.8f} Δ={data['delta_percent']:.4f}%")
        return "\n".join(lines)


def _find_expression(
    target: float,
    max_gens: int = 150,
    operators: dict = None,
) -> Tuple[float, float]:
    """
    Quick expression search for a target value.
    Returns (best_value, error).
    """
    glyphs = holocell_glyphs(136)
    operators = operators or get_holocell_operators()

    result, _, _ = evolve_with_glyphs(
        glyph_set=glyphs,
        target=target,
        pop_size=80,
        head_len=7,
        generations=max_gens,
        operators=operators,
        verbose=False,
    )

    error = abs(result.value - target) / (abs(target) + 1e-10)
    return result.value, error


def _create_pool(pool_id: int) -> PoolState:
    """Create a new pool with random initial values."""
    best_values = {}
    best_fitness = {}
    history = {}

    for name, target in CORE_TARGETS.items():
        # Random initial value within bounds
        val = target.min_bound + random.random() * (target.max_bound - target.min_bound)
        best_values[name] = val
        best_fitness[name] = float('inf')
        history[name] = []

    return PoolState(pool_id, best_values, best_fitness, history)


def _evolve_pool(pool: PoolState, operators: dict, temperature: float = 0.1) -> None:
    """Evolve one pool for one generation."""
    for name, target in CORE_TARGETS.items():
        current = pool.best_values[name]

        # Generate candidate: mutate from current best
        delta = (random.random() - 0.5) * (target.max_bound - target.min_bound) * temperature
        candidate = current + delta
        candidate = max(target.min_bound, min(target.max_bound, candidate))

        # Evaluate expressibility
        _, error = _find_expression(candidate, max_gens=100, operators=operators)

        # Update if better
        if error < pool.best_fitness[name]:
            pool.best_values[name] = candidate
            pool.best_fitness[name] = error

        # Track history
        pool.history[name].append(pool.best_values[name])
        if len(pool.history[name]) > 20:
            pool.history[name].pop(0)


def _analyze_crossings(pools: List[PoolState]) -> Dict[str, CrossingBand]:
    """Analyze where pool settling bands cross."""
    results = {}

    for name, target in CORE_TARGETS.items():
        bands = []
        all_values = []

        for pool in pools:
            hist = pool.history[name]
            if len(hist) >= 5:
                sorted_hist = sorted(hist)
                band_min = sorted_hist[0]
                band_max = sorted_hist[-1]
                bands.append((band_min, band_max))
                all_values.extend(hist)

        if len(bands) == len(pools):
            # Find overlap region
            overlap_min = max(b[0] for b in bands)
            overlap_max = min(b[1] for b in bands)

            if overlap_min <= overlap_max:
                # Bands cross
                centroid = (overlap_min + overlap_max) / 2
                spread = overlap_max - overlap_min
            else:
                # No overlap - use weighted average
                mean = sum(all_values) / len(all_values)
                variance = sum((v - mean) ** 2 for v in all_values) / len(all_values)
                centroid = mean
                spread = (variance ** 0.5) * 2

            # Check for clamping (oscillating between 2 values)
            is_clamped = False
            for pool in pools:
                hist = pool.history[name]
                if len(hist) >= 10:
                    unique = set(round(v, 6) for v in hist[-10:])
                    if len(unique) == 2:
                        is_clamped = True
                        break

            results[name] = CrossingBand(
                constant=name,
                bands=bands,
                centroid=centroid,
                spread=spread,
                is_clamped=is_clamped,
            )

    return results


def run_moon_pools(
    num_pools: int = 4,
    max_runtime_seconds: float = 180.0,  # 3 minutes default
    report_interval: int = 50,
    verbose: bool = True,
    random_seed: int = None,
) -> MoonPoolResult:
    """
    Mode 4: Moon Pools — multi-pool eigenvalue triangulation.

    Runs multiple independent evolutionary pools, each seeking expressions
    for all 5 constants. Where the settling bands CROSS identifies the
    eigenstate value.

    Args:
        num_pools: Number of independent pools (default: 4)
        max_runtime_seconds: Maximum runtime in seconds
        report_interval: Generations between progress reports
        verbose: Print progress
        random_seed: For reproducibility

    Returns:
        MoonPoolResult with eigenstate estimates
    """
    if random_seed is not None:
        random.seed(random_seed)

    operators = get_holocell_operators()

    if verbose:
        print("\n" + "🌙" * 35)
        print("MODE 4: MOON POOLS")
        print("🌙" * 35)
        print(f"\n{num_pools} independent pools × {len(CORE_TARGETS)} constants")
        print("Looking for crossing bands...\n")

    start = time.time()
    pools = [_create_pool(i) for i in range(num_pools)]
    gen = 0

    while (time.time() - start) < max_runtime_seconds:
        gen += 1

        # Evolve all pools
        for pool in pools:
            _evolve_pool(pool, operators)

        # Report
        if verbose and gen % report_interval == 0:
            elapsed = time.time() - start
            print(f"\n{'─' * 70}")
            print(f"Gen {gen} | {elapsed:.1f}s")
            print(f"{'─' * 70}")

            print("\nPool settled values:")
            for name in CORE_TARGETS.keys():
                values = [p.best_values[name] for p in pools]
                band_min = min(values)
                band_max = max(values)
                mean = sum(values) / len(values)
                measured = CORE_TARGETS[name].value
                delta = (mean - measured) / measured * 100
                print(f"  {name:8s} pools: [{', '.join(f'{v:.4f}' for v in values)}]")
                print(f"           band: {band_min:.6f} - {band_max:.6f} Δ={delta:.4f}%")

            crossings = _analyze_crossings(pools)
            print("\nCrossing bands (eigenstate estimates):")
            for name, data in crossings.items():
                measured = CORE_TARGETS[name].value
                delta = (data.centroid - measured) / measured * 100
                status = "🔒" if data.spread < 0.01 else "⚡" if data.spread < 0.1 else "🔄"
                clamp = " [CLAMPED]" if data.is_clamped else ""
                print(f"  {status} {name:8s} centroid: {data.centroid:.8f} spread: {data.spread:.8f} Δ={delta:.6f}%{clamp}")

    elapsed = time.time() - start

    # Final results
    crossings = _analyze_crossings(pools)
    constants = {}
    pool_values = {}

    for name, target in CORE_TARGETS.items():
        vals = [p.best_values[name] for p in pools]
        pool_values[name] = vals

        if name in crossings:
            crossing = crossings[name]
            delta = (crossing.centroid - target.value) / target.value * 100
            constants[name] = {
                'measured': target.value,
                'eigenstate': crossing.centroid,
                'spread': crossing.spread,
                'delta_percent': delta,
                'is_clamped': crossing.is_clamped,
            }

    if verbose:
        print("\n" + "=" * 70)
        print("MOON POOL RESULTS")
        print("=" * 70)
        for name, data in constants.items():
            print(f"\n{name}:")
            print(f"  Measured:   {data['measured']}")
            print(f"  Eigenstate: {data['eigenstate']:.10f}")
            print(f"  Spread:     {data['spread']:.10f}")
            print(f"  Δ:          {data['delta_percent']:.8f}%")
        print("\n" + "🌙" * 35)

    return MoonPoolResult(
        constants=constants,
        pool_values=pool_values,
        crossing_bands=crossings,
        generations=gen,
        elapsed_seconds=elapsed,
    )
