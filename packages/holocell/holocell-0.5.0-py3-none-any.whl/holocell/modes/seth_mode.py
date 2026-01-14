"""
HoloCell — Mode 3: Seth Mode (Dual Set Partition)

Seth = Set = the separator, the filter function

Two sets evolve simultaneously:
  A (archive)     — full integer set, ennead (9)
  B (transmitted) — filtered subset (5-6)

Physics constants resolve from EITHER set:
  - Archival constants need the full set
  - Transmitted constants resolve from filtered subset

The partition operation itself is discovered, not imposed.
Which constants are archival vs transmitted? The crystal reveals.

D(36) → Seth filter → W(16)
A(9)  → Seth filter → B(5-6)
"""

import random
import time
from dataclasses import dataclass
from typing import Dict, List, Tuple

from gepevolver import GlyphGEP, Gene

from .targets import EXTENDED_TARGETS
from .glyphs import coherent_glyphs, architectural_candidates
from .operators import get_holocell_operators


@dataclass
class SethResult:
    """Result from Seth mode evolution."""
    archive: List[int]           # Full set A (ennead)
    transmitted: List[int]       # Filtered set B
    filter_mask: List[bool]      # Which elements pass through Seth
    archival_constants: List[str]
    transmitted_constants: List[str]
    expressions: Dict[str, Dict]  # {name: {value, error, set}}
    total_error: float
    partition_ratio: float       # |B|/|A|, ideal ~16/36
    converged: bool
    generations: int
    elapsed_seconds: float

    def __repr__(self):
        return (
            f"SethResult\n"
            f"  Archive A:     {self.archive}\n"
            f"  Transmitted B: {self.transmitted}\n"
            f"  Partition:     {len(self.transmitted)}/{len(self.archive)} = {self.partition_ratio:.3f}\n"
            f"  Total Error:   {self.total_error:.4f}"
        )


@dataclass
class _SethChromosome:
    """Internal chromosome for Seth evolution."""
    archive: List[int]           # 9 integers (ennead)
    filter_mask: List[bool]      # Which pass through Seth
    expressions: Dict[str, Tuple[str, bool]]  # target -> (genes, use_archive)


def _random_archive() -> List[int]:
    """Generate random 9-integer archive."""
    candidates = architectural_candidates()
    archive = []
    for _ in range(9):
        if random.random() < 0.8:
            archive.append(random.choice(candidates))
        else:
            archive.append(random.randint(1, 100))
    return archive


def _random_filter_mask() -> List[bool]:
    """Generate random filter mask (~5-6 pass through)."""
    mask = [random.random() < 0.55 for _ in range(9)]
    # Ensure at least 3 pass
    passing = sum(mask)
    if passing < 3:
        indices = [i for i, m in enumerate(mask) if not m]
        random.shuffle(indices)
        for i in indices[:3 - passing]:
            mask[i] = True
    return mask


def _apply_filter(archive: List[int], mask: List[bool]) -> List[int]:
    """Apply Seth filter to get transmitted set."""
    return [v for v, m in zip(archive, mask) if m]


def _random_genes(head_length: int, operators: dict) -> str:
    """Generate random gene sequence for 9 integers."""
    op_symbols = list(operators.keys())
    term_chars = [chr(ord('a') + i) for i in range(9)] + ['P', 'X', 'E']

    gene = []
    for _ in range(head_length):
        if random.random() < 0.5:
            gene.append(random.choice(op_symbols))
        else:
            gene.append(random.choice(term_chars))
    for _ in range(head_length + 1):
        gene.append(random.choice(term_chars))
    return ''.join(gene)


def _evaluate_seth(
    chromosome: _SethChromosome,
    targets: Dict[str, float],
    head_length: int,
    operators: dict,
) -> Tuple[Dict[str, float], Dict[str, float], Dict[str, str], float, float]:
    """Evaluate Seth chromosome."""
    transmitted = _apply_filter(chromosome.archive, chromosome.filter_mask)

    values = {}
    errors = {}
    assignments = {}
    total_error = 0.0

    for target_name, target_value in targets.items():
        gene_seq, use_archive = chromosome.expressions.get(target_name, ('', True))
        if not gene_seq:
            values[target_name] = 0.0
            errors[target_name] = 1.0
            assignments[target_name] = 'archive'
            total_error += 1.0
            continue

        # Choose integer set
        integers = chromosome.archive if use_archive else transmitted
        if len(integers) == 0:
            integers = chromosome.archive  # Fallback

        glyphs = coherent_glyphs(integers)
        engine = GlyphGEP(glyphs, operators)
        gene = Gene(gene_seq, head_length)
        value = engine.evaluate(gene)

        error = abs(value - target_value) / (abs(target_value) + 0.001)
        values[target_name] = value
        errors[target_name] = error
        assignments[target_name] = 'archive' if use_archive else 'transmitted'
        total_error += error

    # Bonus for partition ratio near 16/36 (~0.444)
    transmitted_count = sum(chromosome.filter_mask)
    ideal_ratio = 16 / 36
    actual_ratio = transmitted_count / 9
    ratio_bonus = 1 - abs(actual_ratio - ideal_ratio)

    fitness = (1 / (1 + total_error)) * (0.9 + 0.1 * ratio_bonus)

    return values, errors, assignments, total_error, fitness


def evolve_seth(
    head_length: int = 8,
    pop_size: int = 400,
    generations: int = 3000,
    mutation_rate: float = 0.12,
    targets: Dict[str, float] = None,
    verbose: bool = True,
    random_seed: int = None,
) -> SethResult:
    """
    Mode 3: Seth Mode — dual set partition evolution.

    Evolves:
    - Archive A (9 integers, the ennead)
    - Filter mask (which integers pass through to B)
    - Expressions per target
    - Which targets use archive vs transmitted

    Args:
        head_length: Gene head length
        pop_size: Population size
        generations: Maximum generations
        mutation_rate: Mutation probability
        targets: Target constants (default: extended set)
        verbose: Print progress
        random_seed: For reproducibility

    Returns:
        SethResult with partition structure
    """
    if random_seed is not None:
        random.seed(random_seed)

    if targets is None:
        targets = {name: t.value for name, t in EXTENDED_TARGETS.items()}

    operators = get_holocell_operators()
    target_names = list(targets.keys())

    if verbose:
        print("\n" + "=" * 70)
        print("MODE 3: SETH MODE (Dual Set Partition)")
        print("=" * 70)
        print("Archive A: 9 integers (ennead)")
        print("Transmitted B: filtered by Seth")
        print(f"Config: {pop_size} population × {generations} generations\n")

    start = time.time()

    # Initialize population
    population = []
    for _ in range(pop_size):
        archive = _random_archive()
        filter_mask = _random_filter_mask()
        expressions = {
            name: (_random_genes(head_length, operators), random.random() < 0.5)
            for name in target_names
        }
        chromosome = _SethChromosome(archive, filter_mask, expressions)
        values, errors, assignments, total_error, fitness = _evaluate_seth(
            chromosome, targets, head_length, operators
        )
        population.append((chromosome, values, errors, assignments, total_error, fitness))

    # Evolution loop
    converged = False
    final_gen = generations
    for gen in range(generations):
        population.sort(key=lambda x: x[5], reverse=True)  # Sort by fitness
        best = population[0]
        chromosome, values, errors, assignments, total_error, fitness = best

        if verbose and gen % 100 == 0:
            archive_str = ",".join(str(i) for i in chromosome.archive)
            trans = _apply_filter(chromosome.archive, chromosome.filter_mask)
            trans_str = ",".join(str(i) for i in trans)
            print(f"Gen {gen}: A=[{archive_str}] B=[{trans_str}] err={total_error:.3f}")

        if total_error < 0.05:
            if verbose:
                print(f"\n✅ Converged at generation {gen}!")
            converged = True
            final_gen = gen
            break

        # Reproduction
        new_pop = []
        elite_count = max(1, pop_size // 10)

        for i in range(elite_count):
            new_pop.append(population[i])

        while len(new_pop) < pop_size:
            parent = population[random.randint(0, int(pop_size * 0.3))]
            p_chrom = parent[0]

            # Mutate archive
            candidates = architectural_candidates()
            new_archive = []
            for v in p_chrom.archive:
                if random.random() < mutation_rate:
                    if random.random() < 0.7:
                        new_archive.append(random.choice(candidates))
                    else:
                        new_archive.append(max(1, v + random.randint(-5, 5)))
                else:
                    new_archive.append(v)

            # Mutate filter mask
            new_mask = []
            for m in p_chrom.filter_mask:
                if random.random() < mutation_rate * 0.5:
                    new_mask.append(not m)
                else:
                    new_mask.append(m)
            # Ensure at least 3 pass
            if sum(new_mask) < 3:
                indices = [i for i, m in enumerate(new_mask) if not m]
                random.shuffle(indices)
                for i in indices[:3 - sum(new_mask)]:
                    new_mask[i] = True

            # Mutate expressions
            op_symbols = list(operators.keys())
            term_chars = [chr(ord('a') + i) for i in range(9)] + ['P', 'X', 'E']
            new_exprs = {}
            for name, (genes, use_archive) in p_chrom.expressions.items():
                # Mutate genes
                new_genes = []
                for i, g in enumerate(genes):
                    if random.random() < mutation_rate:
                        if i < head_length:
                            if random.random() < 0.5:
                                new_genes.append(random.choice(op_symbols))
                            else:
                                new_genes.append(random.choice(term_chars))
                        else:
                            new_genes.append(random.choice(term_chars))
                    else:
                        new_genes.append(g)
                # Maybe flip archive/transmitted assignment
                new_use = not use_archive if random.random() < mutation_rate * 0.3 else use_archive
                new_exprs[name] = (''.join(new_genes), new_use)

            new_chrom = _SethChromosome(new_archive, new_mask, new_exprs)
            v, e, a, te, f = _evaluate_seth(new_chrom, targets, head_length, operators)
            new_pop.append((new_chrom, v, e, a, te, f))

        population = new_pop[:pop_size]

    elapsed = time.time() - start

    # Final result
    population.sort(key=lambda x: x[5], reverse=True)
    best = population[0]
    chromosome, values, errors, assignments, total_error, fitness = best

    transmitted = _apply_filter(chromosome.archive, chromosome.filter_mask)
    archival_constants = [n for n, a in assignments.items() if a == 'archive']
    transmitted_constants = [n for n, a in assignments.items() if a == 'transmitted']

    expressions = {}
    for name in target_names:
        expressions[name] = {
            'value': values[name],
            'error': errors[name],
            'set': assignments[name],
        }

    if verbose:
        print("\n" + "=" * 70)
        print("SETH PARTITION RESULT")
        print("=" * 70)
        print(f"\n📦 Archive A (full set):     {chromosome.archive}")
        mask_str = ", ".join("✓" if m else "✗" for m in chromosome.filter_mask)
        print(f"🚪 Seth filter mask:         [{mask_str}]")
        print(f"📨 Transmitted B (filtered): {transmitted}")
        print(f"\n📜 Archival constants (need full set):")
        for c in archival_constants:
            print(f"   {c:20s} → {values[c]:.6f} ({errors[c]*100:.3f}% err)")
        print(f"\n📡 Transmitted constants (resolve from filtered):")
        for c in transmitted_constants:
            print(f"   {c:20s} → {values[c]:.6f} ({errors[c]*100:.3f}% err)")
        ratio = len(transmitted) / 9
        print(f"\nPartition ratio: {len(transmitted)}/9 = {ratio:.3f} (ideal: {16/36:.3f})")

    return SethResult(
        archive=chromosome.archive,
        transmitted=transmitted,
        filter_mask=chromosome.filter_mask,
        archival_constants=archival_constants,
        transmitted_constants=transmitted_constants,
        expressions=expressions,
        total_error=total_error,
        partition_ratio=len(transmitted) / 9,
        converged=converged,
        generations=final_gen,
        elapsed_seconds=elapsed,
    )
