"""
Glyph-Aware GEP Engine

Gene Expression Programming engine using frozen glyphs.
Any formula produced is inherently elegant because atoms ARE elegant.

Adapted from GEPEvolver for HoloCell integration.
"""

import math
import random
from dataclasses import dataclass
from typing import List, Tuple, Optional

from .glyphs import GlyphSet


# =============================================================================
# PROTECTED OPERATORS
# =============================================================================

EPSILON = 1e-10
MAX_VALUE = 1e15


def protected_div(a, b):
    if abs(b) < EPSILON:
        return 1.0
    return max(-MAX_VALUE, min(MAX_VALUE, a / b))


def protected_pow(a, b):
    b = max(-50, min(50, b))
    if b < 0 and abs(a) < EPSILON:
        return 1.0
    if a < 0 and b != int(b):
        a = abs(a)
    try:
        result = a ** b
        if isinstance(result, complex):
            return abs(result)
        return max(-MAX_VALUE, min(MAX_VALUE, result))
    except:
        return 1.0


def protected_sqrt(a):
    return math.sqrt(abs(a))


@dataclass
class Operator:
    symbol: str
    arity: int
    func: callable
    display: str


OPERATORS = {
    '+': Operator('+', 2, lambda a, b: a + b, '+'),
    '-': Operator('-', 2, lambda a, b: a - b, '-'),
    '*': Operator('*', 2, lambda a, b: a * b, '×'),
    '/': Operator('/', 2, protected_div, '/'),
    '^': Operator('^', 2, protected_pow, '^'),
    'Q': Operator('Q', 1, protected_sqrt, '√'),
}

MAX_ARITY = 2


# =============================================================================
# GENE STRUCTURE
# =============================================================================

@dataclass
class Gene:
    sequence: str
    head_length: int
    
    @property
    def tail_length(self):
        return self.head_length * (MAX_ARITY - 1) + 1
    
    @property
    def head(self):
        return self.sequence[:self.head_length]
    
    @property
    def tail(self):
        return self.sequence[self.head_length:]


@dataclass 
class TreeNode:
    symbol: str
    children: List['TreeNode'] = None
    
    def __post_init__(self):
        if self.children is None: 
            self.children = []


# =============================================================================
# GLYPH-AWARE ENGINE
# =============================================================================

class GlyphGEP:
    """
    GEP engine that uses a GlyphSet for terminals.
    
    All terminal symbols come from the glyph set.
    Evaluation looks up values from glyphs.
    Display uses glyph names for elegant output.
    """
    
    def __init__(self, glyph_set: GlyphSet, operators: dict = None):
        self.glyphs = glyph_set
        self.operators = operators or OPERATORS
        self.terminal_symbols = glyph_set.symbols
        self.operator_symbols = list(self.operators.keys())
        self.all_symbols = self.operator_symbols + self.terminal_symbols
    
    def is_terminal(self, symbol: str) -> bool:
        return symbol in self.terminal_symbols
    
    def is_operator(self, symbol: str) -> bool:
        return symbol in self.operator_symbols
    
    def arity(self, symbol: str) -> int:
        if self.is_terminal(symbol):
            return 0
        op = self.operators.get(symbol)
        return op.arity if op else 0
    
    # =========================================================================
    # GENE OPERATIONS
    # =========================================================================
    
    def random_gene(self, head_length: int) -> Gene:
        """Create random gene using only glyph terminals."""
        tail_length = head_length + 1
        head = ''.join(random.choice(self.all_symbols) for _ in range(head_length))
        tail = ''.join(random.choice(self.terminal_symbols) for _ in range(tail_length))
        return Gene(sequence=head + tail, head_length=head_length)
    
    def mutate(self, gene: Gene, rate: float = 0.05) -> Gene:
        """Point mutation respecting glyph constraints."""
        seq = list(gene.sequence)
        for i in range(len(seq)):
            if random.random() < rate:
                if i < gene.head_length:
                    seq[i] = random.choice(self.all_symbols)
                else:
                    seq[i] = random.choice(self.terminal_symbols)
        return Gene(''.join(seq), gene.head_length)
    
    def transpose_is(self, gene: Gene, length: int = 3) -> Gene:
        """IS transposition."""
        seq = gene.sequence
        h = gene.head_length
        if h < 2:
            return gene
        src = random.randint(0, len(seq) - length)
        segment = seq[src:src + length]
        ins = random.randint(1, h - 1)
        new_head = (seq[:ins] + segment + seq[ins:h])[:h]
        return Gene(new_head + gene.tail, h)
    
    def recombine(self, g1: Gene, g2: Gene) -> Tuple[Gene, Gene]:
        """One-point crossover."""
        pt = random.randint(1, len(g1.sequence) - 1)
        return (
            Gene(g1.sequence[:pt] + g2.sequence[pt:], g1.head_length),
            Gene(g2.sequence[:pt] + g1.sequence[pt:], g2.head_length)
        )
    
    # =========================================================================
    # TREE OPERATIONS
    # =========================================================================
    
    def to_tree(self, gene: Gene) -> TreeNode:
        """Convert K-expression to tree."""
        seq = gene.sequence
        if not seq:
            return None
        
        root = TreeNode(seq[0])
        queue = [root]
        pos = 1
        
        while queue and pos < len(seq):
            current = queue.pop(0)
            for _ in range(self.arity(current.symbol)):
                if pos >= len(seq):
                    break
                child = TreeNode(seq[pos])
                current.children.append(child)
                if self.arity(child.symbol) > 0:
                    queue.append(child)
                pos += 1
        
        return root
    
    def evaluate_tree(self, node: TreeNode) -> float:
        """Evaluate tree using glyph values."""
        if node is None:
            return 0.0
        
        try:
            if self.is_terminal(node.symbol):
                return self.glyphs.value(node.symbol)
            
            op = self.operators.get(node.symbol)
            if op is None:
                return 0.0
            
            children = [self.evaluate_tree(c) for c in node.children]
            result = op.func(*children)
            
            if isinstance(result, complex):
                return abs(result)
            if math.isnan(result) or math.isinf(result):
                return 0.0
            return result
        except:
            return 0.0
    
    def evaluate(self, gene: Gene) -> float:
        """Evaluate a gene."""
        return self.evaluate_tree(self.to_tree(gene))
    
    # =========================================================================
    # DISPLAY
    # =========================================================================
    
    def tree_to_elegant(self, node: TreeNode) -> str:
        """Convert tree to elegant expression using glyph names."""
        if node is None:
            return "?"
        
        if self.is_terminal(node.symbol):
            return self.glyphs.display(node.symbol)
        
        op = self.operators.get(node.symbol)
        if op is None:
            return "?"
        
        if len(node.children) == 1:
            child = self.tree_to_elegant(node.children[0])
            if node.symbol == 'Q':
                return f"√({child})"
            return f"{op.display}({child})"
        
        if len(node.children) == 2:
            left = self.tree_to_elegant(node.children[0])
            right = self.tree_to_elegant(node.children[1])
            if node.symbol == '^':
                return f"({left})^({right})"
            return f"({left} {op.display} {right})"
        
        return "?"
    
    def to_elegant(self, gene: Gene) -> str:
        """Convert gene to elegant expression."""
        return self.tree_to_elegant(self.to_tree(gene))


# =============================================================================
# EVOLUTION
# =============================================================================

def evolve_with_glyphs(
    glyph_set: GlyphSet,
    target: float,
    pop_size: int = 300,
    head_len: int = 12,
    generations: int = 1000,
    mutation_rate: float = 0.08,
    crossover_rate: float = 0.70,
    verbose: bool = True,
    seed: int = None,
) -> Tuple[Tuple, List[Gene], 'GlyphGEP']:
    """
    Run GEP evolution using a frozen glyph set.
    
    Parameters:
        glyph_set: GlyphSet to use for terminals
        target: Target value to evolve towards
        pop_size: Population size (default 300)
        head_len: Gene head length (default 12)
        generations: Max generations (default 1000)
        mutation_rate: Point mutation rate (default 0.08)
        crossover_rate: Crossover probability (default 0.70)
        verbose: Print progress (default True)
        seed: Random seed for reproducibility (optional)
    
    Returns:
        (best_fitness, best_gene, best_value, best_expression), population, engine
    """
    if seed is not None:
        random.seed(seed)
    
    engine = GlyphGEP(glyph_set)
    population = [engine.random_gene(head_len) for _ in range(pop_size)]
    
    def fitness(value):
        if not isinstance(value, (int, float)) or math.isnan(value) or math.isinf(value):
            return 0.0
        error = abs(value - target) / abs(target)
        return max(0, 1000 * (1 - math.log10(1 + error * 1e10) / 10))
    
    best_ever = (0, None, None, "")
    stagnant = 0
    
    for gen in range(generations):
        # Evaluate
        results = [(g, engine.evaluate(g)) for g in population]
        fits = [fitness(v) for g, v in results]
        
        # Find best
        best_idx = max(range(len(fits)), key=lambda i: fits[i])
        best_gene, best_val = results[best_idx]
        best_fit = fits[best_idx]
        best_expr = engine.to_elegant(best_gene)
        
        if best_fit > best_ever[0]:
            best_ever = (best_fit, best_gene, best_val, best_expr)
            stagnant = 0
        else:
            stagnant += 1
        
        if verbose and (gen % 100 == 0 or gen < 10):
            err = abs(best_val - target) / abs(target) * 100
            print(f"Gen {gen:4d} | {best_val:.12f} | err={err:.8f}% | fit={best_fit:.1f}")
        
        if stagnant > 500:
            if verbose:
                print(f"Stagnant at gen {gen}")
            break
        
        # Selection + reproduction
        new_pop = [best_gene]  # Elitism
        while len(new_pop) < pop_size:
            # Tournament
            t = random.sample(range(pop_size), 3)
            winner = max(t, key=lambda i: fits[i])
            parent = population[winner]
            
            # Genetic ops
            child = engine.mutate(parent, mutation_rate)
            if random.random() < 0.1:
                child = engine.transpose_is(child)
            if random.random() < crossover_rate:
                t2 = random.sample(range(pop_size), 3)
                w2 = max(t2, key=lambda i: fits[i])
                child, _ = engine.recombine(child, population[w2])
            
            new_pop.append(child)
        
        population = new_pop[:pop_size]
    
    return best_ever, population, engine
