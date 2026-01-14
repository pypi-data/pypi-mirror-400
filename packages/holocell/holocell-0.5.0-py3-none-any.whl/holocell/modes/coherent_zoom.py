"""
HoloCell — Mode 2: Coherent Zoom

Evolves the integer set itself while requiring multiple physics constants
to resolve simultaneously. The terminals aren't fixed inputs — they're
discovered outputs.

Fitness = combined error across ALL targets using a SHARED integer set.

If physics constants cohere on a small integer set and random numbers don't,
that's the signal.
"""

import random
import time
from dataclasses import dataclass, field
from typing import Dict, List, Tuple

from gepevolver import GlyphGEP, Gene

from .targets import EXTENDED_TARGETS, get_target
from .glyphs import coherent_glyphs, architectural_candidates
from .operators import get_holocell_operators


@dataclass
class CoherentResult:
    """Result from coherent zoom evolution."""
    discovered_integers: List[int]
    expressions: Dict[str, str]
    values: Dict[str, float]
    errors: Dict[str, float]
    total_error: float
    fitness: float
    converged: bool
    generations: int
    elapsed_seconds: float

    def __repr__(self):
        ints_str = ", ".join(str(i) for i in self.discovered_integers)
        return (
            f"CoherentResult\n"
            f"  Integers: [{ints_str}]\n"
            f"  Total Error: {self.total_error:.4f}\n"
            f"  Converged: {self.converged}"
        )


def _random_integers(size: int) -> List[int]:
    """Generate random integer set biased toward architectural candidates."""
    candidates = architectural_candidates()
    result = []
    for _ in range(size):
        if random.random() < 0.7:
            result.append(random.choice(candidates))
        else:
            result.append(random.randint(1, 100))
    return result


def _mutate_integers(integers: List[int], rate: float) -> List[int]:
    """Mutate integer set."""
    candidates = architectural_candidates()
    result = []
    for v in integers:
        if random.random() < rate:
            if random.random() < 0.7:
                result.append(random.choice(candidates))
            else:
                result.append(max(1, v + random.randint(-5, 5)))
        else:
            result.append(v)
    return result


def _random_genes(head_length: int, num_integers: int, operators: dict) -> str:
    """Generate random gene sequence."""
    op_symbols = list(operators.keys())
    term_symbols = [f'I{i}' for i in range(num_integers)] + ['π', 'φ', 'e']
    # Map to single chars for gene
    term_map = {f'I{i}': chr(ord('a') + i) for i in range(num_integers)}
    term_map['π'] = 'P'
    term_map['φ'] = 'X'
    term_map['e'] = 'E'
    all_term_chars = [term_map[t] for t in term_symbols]

    gene = []
    # Head: operators + terminals
    for _ in range(head_length):
        if random.random() < 0.5:
            gene.append(random.choice(op_symbols))
        else:
            gene.append(random.choice(all_term_chars))
    # Tail: terminals only
    for _ in range(head_length + 1):
        gene.append(random.choice(all_term_chars))

    return ''.join(gene)


def _mutate_genes(genes: str, head_length: int, num_integers: int, rate: float, operators: dict) -> str:
    """Mutate gene sequence."""
    op_symbols = list(operators.keys())
    term_chars = [chr(ord('a') + i) for i in range(num_integers)] + ['P', 'X', 'E']

    result = []
    for i, g in enumerate(genes):
        if random.random() < rate:
            if i < head_length:
                if random.random() < 0.5:
                    result.append(random.choice(op_symbols))
                else:
                    result.append(random.choice(term_chars))
            else:
                result.append(random.choice(term_chars))
        else:
            result.append(g)
    return ''.join(result)


@dataclass
class _CoherentChromosome:
    """Internal chromosome for coherent evolution."""
    integers: List[int]
    expressions: Dict[str, str]  # target -> gene sequence


@dataclass
class _CoherentIndividual:
    """Evaluated coherent individual."""
    chromosome: _CoherentChromosome
    values: Dict[str, float]
    errors: Dict[str, float]
    total_error: float
    fitness: float


def _evaluate_coherent(
    chromosome: _CoherentChromosome,
    targets: Dict[str, float],
    head_length: int,
    operators: dict,
) -> _CoherentIndividual:
    """Evaluate a coherent chromosome against all targets."""
    glyphs = coherent_glyphs(chromosome.integers)
    engine = GlyphGEP(glyphs, operators)

    values = {}
    errors = {}
    total_error = 0.0

    for target_name, target_value in targets.items():
        gene_seq = chromosome.expressions.get(target_name, '')
        if not gene_seq:
            values[target_name] = 0.0
            errors[target_name] = 1.0
            total_error += 1.0
            continue

        gene = Gene(gene_seq, head_length)
        value = engine.evaluate(gene)
        error = abs(value - target_value) / (abs(target_value) + 0.001)

        values[target_name] = value
        errors[target_name] = error
        total_error += error

    fitness = 1.0 / (1.0 + total_error)

    return _CoherentIndividual(
        chromosome=chromosome,
        values=values,
        errors=errors,
        total_error=total_error,
        fitness=fitness,
    )


def evolve_coherent(
    integer_set_size: int = 6,
    head_length: int = 8,
    pop_size: int = 300,
    generations: int = 2000,
    mutation_rate: float = 0.15,
    crossover_rate: float = 0.7,
    targets: Dict[str, float] = None,
    verbose: bool = True,
    random_seed: int = None,
) -> CoherentResult:
    """
    Mode 2: Coherent Zoom — co-evolve integer set to fit all constants.

    The integer set itself is discovered, not fixed. Each individual has:
    - A set of integers (terminals)
    - Expressions for each target using those terminals

    Fitness is the combined error across ALL targets.

    Args:
        integer_set_size: Number of integers in the evolved set
        head_length: Gene head length
        pop_size: Population size
        generations: Maximum generations
        mutation_rate: Mutation probability
        crossover_rate: Crossover probability
        targets: Target constants (default: extended set)
        verbose: Print progress
        random_seed: For reproducibility

    Returns:
        CoherentResult with discovered integers and expressions
    """
    if random_seed is not None:
        random.seed(random_seed)

    if targets is None:
        targets = {name: t.value for name, t in EXTENDED_TARGETS.items()}

    operators = get_holocell_operators()
    target_names = list(targets.keys())

    if verbose:
        print("\n" + "=" * 70)
        print("MODE 2: COHERENT ZOOM")
        print("=" * 70)
        print(f"Evolving integer set (size={integer_set_size}) to express {len(targets)} constants")
        print(f"Config: {pop_size} population × {generations} generations\n")

    start = time.time()

    # Initialize population
    population: List[_CoherentIndividual] = []
    for _ in range(pop_size):
        integers = _random_integers(integer_set_size)
        expressions = {
            name: _random_genes(head_length, integer_set_size, operators)
            for name in target_names
        }
        chromosome = _CoherentChromosome(integers, expressions)
        population.append(_evaluate_coherent(chromosome, targets, head_length, operators))

    # Evolution loop
    best_ever = population[0]
    for gen in range(generations):
        population.sort(key=lambda x: x.fitness, reverse=True)
        best = population[0]

        if best.fitness > best_ever.fitness:
            best_ever = best

        if verbose and gen % 100 == 0:
            ints_str = ",".join(str(i) for i in best.chromosome.integers)
            print(f"Gen {gen}: integers=[{ints_str}] totalError={best.total_error:.4f}")

        # Early convergence
        if best.total_error < 0.01:
            if verbose:
                print(f"\n✅ Converged at generation {gen}!")
            break

        # Selection and reproduction
        new_pop: List[_CoherentIndividual] = []
        elite_count = max(1, pop_size // 10)

        # Elitism
        for i in range(elite_count):
            new_pop.append(population[i])

        # Generate rest
        while len(new_pop) < pop_size:
            # Tournament selection
            p1 = population[random.randint(0, int(pop_size * 0.3))]
            p2 = population[random.randint(0, int(pop_size * 0.3))]

            # Crossover integers
            if random.random() < crossover_rate:
                pt = random.randint(1, integer_set_size - 1)
                new_ints = p1.chromosome.integers[:pt] + p2.chromosome.integers[pt:]
            else:
                new_ints = p1.chromosome.integers.copy()

            # Mutate integers
            new_ints = _mutate_integers(new_ints, mutation_rate)

            # Crossover/mutate expressions
            new_exprs = {}
            for name in target_names:
                if random.random() < 0.5:
                    expr = p1.chromosome.expressions[name]
                else:
                    expr = p2.chromosome.expressions[name]
                expr = _mutate_genes(expr, head_length, integer_set_size, mutation_rate, operators)
                new_exprs[name] = expr

            chromosome = _CoherentChromosome(new_ints, new_exprs)
            new_pop.append(_evaluate_coherent(chromosome, targets, head_length, operators))

        population = new_pop[:pop_size]

    elapsed = time.time() - start

    # Final result
    population.sort(key=lambda x: x.fitness, reverse=True)
    best = population[0]

    # Get expressions as readable strings
    glyphs = coherent_glyphs(best.chromosome.integers)
    engine = GlyphGEP(glyphs, operators)
    expressions = {}
    for name, gene_seq in best.chromosome.expressions.items():
        gene = Gene(gene_seq, head_length)
        expressions[name] = engine.to_elegant(gene)

    if verbose:
        print("\n" + "=" * 70)
        print("COHERENT ZOOM RESULT")
        print("=" * 70)
        print(f"\nDiscovered integers: {best.chromosome.integers}")
        print(f"Total error: {best.total_error:.6f}")
        print("\nPer-target results:")
        for name, val in best.values.items():
            target_val = targets[name]
            err = best.errors[name] * 100
            print(f"  {name:20s} target={target_val:<15.6f} got={val:<15.6f} err={err:.3f}%")

    return CoherentResult(
        discovered_integers=best.chromosome.integers,
        expressions=expressions,
        values=best.values,
        errors=best.errors,
        total_error=best.total_error,
        fitness=best.fitness,
        converged=best.total_error < 0.01,
        generations=gen + 1,
        elapsed_seconds=elapsed,
    )
