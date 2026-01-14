"""
HoloCell — Mode 5: Coherence Test (N-Node Corruption Sweep)

Find the fault tolerance threshold.
How many nodes can be corrupted before coherence breaks?

For each corruption level (1, 2, 3, ... N):
  - Run multiple trials
  - Measure integer overlap with architectural set
  - Track convergence quality

The threshold is where overlap drops significantly.
This validates that the architectural integers emerge from
the physics constants themselves, not from fitting noise.
"""

import math
import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from .targets import EXTENDED_TARGETS, ARCHITECTURE
from .coherent_zoom import evolve_coherent


@dataclass
class TrialResult:
    """Result from a single corruption trial."""
    corruption_level: int
    corrupted_constants: List[str]
    discovered_integers: List[int]
    overlap: int                    # How many match architectural set
    total_error: float


@dataclass
class LevelResult:
    """Aggregated results for a corruption level."""
    corruption_level: int
    trials: List[TrialResult]
    avg_overlap: float
    min_overlap: int
    max_overlap: int
    avg_error: float


@dataclass
class CoherenceSweepResult:
    """Result from coherence sweep."""
    levels: List[LevelResult]
    fault_tolerance_threshold: int  # Max corruptions before breakdown
    baseline_overlap: float         # Overlap with 0 corruptions
    elapsed_seconds: float

    def __repr__(self):
        return (
            f"CoherenceSweepResult\n"
            f"  Fault Tolerance: {self.fault_tolerance_threshold} nodes\n"
            f"  Baseline Overlap: {self.baseline_overlap:.2f}/9"
        )


def _exponential_sample(min_val: float, max_val: float) -> float:
    """Sample from log-uniform distribution."""
    log_min = math.log(min_val)
    log_max = math.log(max_val)
    return math.exp(log_min + random.random() * (log_max - log_min))


def _generate_corrupted_value(original: float) -> float:
    """Generate a corrupted value far from original."""
    magnitude = abs(original) + 0.001
    return _exponential_sample(magnitude / 100, magnitude * 100)


def _integer_overlap(discovered: List[int]) -> int:
    """Count how many discovered integers match architectural set."""
    count = 0
    for d in discovered:
        # Allow ±1 tolerance
        if any(abs(d - a) <= 1 for a in ARCHITECTURE):
            count += 1
    return count


def run_coherence_sweep(
    max_corruption: int = 8,
    trials_per_level: int = 3,
    integer_set_size: int = 9,
    generations_per_trial: int = 1000,
    verbose: bool = True,
    random_seed: int = None,
) -> CoherenceSweepResult:
    """
    Mode 5: Coherence Test — N-node corruption sweep.

    Tests fault tolerance by corrupting physics constant values
    and measuring whether the architectural integers still emerge.

    For each corruption level:
    1. Randomly select N constants to corrupt
    2. Replace their values with random numbers
    3. Run coherent evolution
    4. Measure overlap with architectural set

    The threshold is where overlap drops below 60% of baseline.

    Args:
        max_corruption: Maximum number of constants to corrupt
        trials_per_level: Trials per corruption level
        integer_set_size: Size of evolved integer set
        generations_per_trial: Generations per coherent evolution
        verbose: Print progress
        random_seed: For reproducibility

    Returns:
        CoherenceSweepResult with fault tolerance analysis
    """
    if random_seed is not None:
        random.seed(random_seed)

    constant_names = list(EXTENDED_TARGETS.keys())
    true_values = {name: t.value for name, t in EXTENDED_TARGETS.items()}

    if verbose:
        print("\n" + "=" * 70)
        print("MODE 5: COHERENCE TEST (N-Node Corruption Sweep)")
        print("=" * 70)
        print(f"\nTesting corruption levels 0 to {max_corruption}")
        print(f"{trials_per_level} trials per level\n")

    start = time.time()
    results: List[LevelResult] = []

    for level in range(max_corruption + 1):
        if verbose:
            print(f"\n{'─' * 50}")
            print(f"Corruption Level: {level}/{len(constant_names)} nodes")
            print(f"{'─' * 50}")

        trials: List[TrialResult] = []

        for t in range(trials_per_level):
            # Select constants to corrupt
            shuffled = constant_names.copy()
            random.shuffle(shuffled)
            to_corrupt = shuffled[:level]

            # Build corrupted target set
            targets = true_values.copy()
            for name in to_corrupt:
                targets[name] = _generate_corrupted_value(true_values[name])

            # Run coherent evolution
            result = evolve_coherent(
                integer_set_size=integer_set_size,
                head_length=8,
                pop_size=200,
                generations=generations_per_trial,
                targets=targets,
                verbose=False,
            )

            overlap = _integer_overlap(result.discovered_integers)

            trial = TrialResult(
                corruption_level=level,
                corrupted_constants=to_corrupt,
                discovered_integers=result.discovered_integers,
                overlap=overlap,
                total_error=result.total_error,
            )
            trials.append(trial)

            if verbose:
                ints_str = ",".join(str(i) for i in result.discovered_integers)
                print(f"  Trial {t + 1}: overlap={overlap}/9, error={result.total_error:.3f}, ints=[{ints_str}]")

        overlaps = [t.overlap for t in trials]
        avg_overlap = sum(overlaps) / len(overlaps)
        avg_error = sum(t.total_error for t in trials) / len(trials)

        results.append(LevelResult(
            corruption_level=level,
            trials=trials,
            avg_overlap=avg_overlap,
            min_overlap=min(overlaps),
            max_overlap=max(overlaps),
            avg_error=avg_error,
        ))

        if verbose:
            print(f"\n  Level {level} summary: avg overlap = {avg_overlap:.2f}/9")

    elapsed = time.time() - start

    # Find threshold
    baseline = results[0].avg_overlap if results else 0
    threshold = max_corruption
    for i, r in enumerate(results[1:], 1):
        if r.avg_overlap < baseline * 0.6:
            threshold = i
            break

    if verbose:
        print("\n" + "=" * 70)
        print("SWEEP RESULTS")
        print("=" * 70)
        print("\nCorruption Level → Average Overlap with Architectural Set\n")

        for r in results:
            bar = "█" * int(r.avg_overlap)
            spaces = " " * (9 - int(r.avg_overlap))
            print(f"  {r.corruption_level:2d} nodes: [{bar}{spaces}] {r.avg_overlap:.2f}/9 (err: {r.avg_error:.3f})")

        print(f"\n{'─' * 70}")
        print(f"FAULT TOLERANCE THRESHOLD: {threshold} nodes")
        print(f"Coherence holds with up to {threshold - 1} corrupted constants (of {len(constant_names)}).")
        print(f"At {threshold}+ corruptions, overlap drops below 60% of baseline.")
        print("=" * 70)

    return CoherenceSweepResult(
        levels=results,
        fault_tolerance_threshold=threshold,
        baseline_overlap=baseline,
        elapsed_seconds=elapsed,
    )
