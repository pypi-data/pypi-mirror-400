"""
Self-Healing Networks — Finding special topologies from 12 to 408

The hypothesis: There exists a sequence of network sizes with self-healing
properties, starting from 12 (confirmed) and extending to 408 (full grammar).

Self-healing criteria:
1. High vertex connectivity (k-connected, k ≥ 3)
2. Regular or semi-regular structure
3. Derives from unit cell symmetry (Egyptian architecture)
4. Resilient to node removal

Candidate derivations:
- Triangular numbers: T(n) = n(n+1)/2
- Wheel × spine: 16 × 3 = 48, 16 × 5 = 80
- Platonic/Archimedean: 12 (icosahedron), 20, 60 (buckyball)
- Egyptian grammar: 136 = T(16), 408 = 136 × 3
"""

import math
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict
from itertools import combinations


# =============================================================================
# TRIANGULAR AND ARCHITECTURE NUMBERS
# =============================================================================

def T(n: int) -> int:
    """Triangular number T(n) = n(n+1)/2"""
    return n * (n + 1) // 2


def inverse_T(t: int) -> Optional[int]:
    """If t is triangular, return n such that T(n) = t, else None."""
    # T(n) = t => n² + n - 2t = 0 => n = (-1 + √(1 + 8t)) / 2
    discriminant = 1 + 8 * t
    sqrt_d = int(math.isqrt(discriminant))
    if sqrt_d * sqrt_d != discriminant:
        return None
    if (sqrt_d - 1) % 2 != 0:
        return None
    n = (sqrt_d - 1) // 2
    return n if T(n) == t else None


def is_triangular(n: int) -> bool:
    """Check if n is a triangular number."""
    return inverse_T(n) is not None


# Egyptian architecture constants
WHEEL = 16          # Phonemes on the wheel
SPINE = 3           # Primary spine axes
HOURGLASS = 5       # Positions per phoneme
DIRECTED = 15       # Directed pairs per phoneme (16-1)


# =============================================================================
# CANDIDATE GENERATION
# =============================================================================

@dataclass
class NetworkCandidate:
    """A candidate network size with derivation."""
    n: int                      # Number of nodes
    derivation: str             # How it's derived
    family: str                 # Which family (triangular, platonic, wheel, etc.)
    factors: Tuple[int, ...]    # Component factors
    
    @property
    def is_triangular(self) -> bool:
        return is_triangular(self.n)
    
    @property
    def triangular_index(self) -> Optional[int]:
        return inverse_T(self.n)


def generate_candidates(max_n: int = 500) -> List[NetworkCandidate]:
    """
    Generate candidate network sizes from Egyptian architecture.
    
    Families:
    1. Triangular: T(k) for various k
    2. Wheel products: 16 × k
    3. Spine expansions: n × 3
    4. Platonic/Archimedean: 4, 6, 8, 12, 20, 60, 120
    5. Grammar: 136, 240, 408
    """
    candidates = []
    seen = set()
    
    def add(n, derivation, family, factors):
        if n <= max_n and n not in seen:
            candidates.append(NetworkCandidate(n, derivation, family, factors))
            seen.add(n)
    
    # Triangular numbers
    for k in range(2, 50):
        t = T(k)
        if t > max_n:
            break
        add(t, f"T({k})", "triangular", (k,))
    
    # Platonic solids (vertices)
    platonic = [
        (4, "tetrahedron"),
        (6, "octahedron"),
        (8, "cube"),
        (12, "icosahedron"),
        (20, "dodecahedron"),
    ]
    for v, name in platonic:
        add(v, f"{name} vertices", "platonic", (v,))
    
    # Archimedean (notable)
    add(24, "cuboctahedron", "archimedean", (24,))
    add(60, "buckyball/truncated icosahedron", "archimedean", (60,))
    add(120, "4D 600-cell vertices", "polytope", (120,))
    
    # Wheel products
    for k in [1, 2, 3, 4, 5, 6, 7, 8, 9, 15]:
        n = WHEEL * k
        if n <= max_n:
            add(n, f"wheel × {k}", "wheel", (WHEEL, k))
    
    # Spine expansions of key numbers
    for base in [12, 36, 45, 60, 80, 136]:
        n = base * SPINE
        if n <= max_n:
            add(n, f"{base} × spine", "spine", (base, SPINE))
    
    # Grammar numbers
    add(136, "T(16) = wheel relations", "grammar", (16,))
    add(240, "16 × 15 = directed pairs", "grammar", (16, 15))
    add(408, "136 × 3 = full grammar", "grammar", (136, 3))
    
    # Hourglass expansions
    for base in [16, 36, 80]:
        n = base * HOURGLASS
        if n <= max_n:
            add(n, f"{base} × hourglass", "hourglass", (base, HOURGLASS))
    
    # Sort by size
    candidates.sort(key=lambda c: c.n)
    return candidates


# =============================================================================
# GRAPH GENERATION
# =============================================================================

def complete_graph_edges(n: int) -> List[Tuple[int, int]]:
    """Generate edges for complete graph K_n."""
    return list(combinations(range(n), 2))


def cycle_graph_edges(n: int) -> List[Tuple[int, int]]:
    """Generate edges for cycle graph C_n."""
    return [(i, (i + 1) % n) for i in range(n)]


def regular_polygon_edges(n: int, connections: int = 1) -> List[Tuple[int, int]]:
    """
    Generate edges for regular polygon with skip connections.
    connections=1: simple cycle
    connections=2: each vertex connects to 2 neighbors on each side
    etc.
    """
    edges = set()
    for i in range(n):
        for k in range(1, connections + 1):
            j = (i + k) % n
            edges.add((min(i, j), max(i, j)))
    return list(edges)


def icosahedron_edges() -> List[Tuple[int, int]]:
    """
    Generate edges for icosahedron (12 vertices, 30 edges).
    Each vertex has degree 5.
    """
    # Icosahedron adjacency (0-indexed)
    adj = [
        [1, 2, 3, 4, 5],      # 0: top
        [0, 2, 5, 6, 7],      # 1
        [0, 1, 3, 7, 8],      # 2
        [0, 2, 4, 8, 9],      # 3
        [0, 3, 5, 9, 10],     # 4
        [0, 1, 4, 6, 10],     # 5
        [1, 5, 7, 10, 11],    # 6
        [1, 2, 6, 8, 11],     # 7
        [2, 3, 7, 9, 11],     # 8
        [3, 4, 8, 10, 11],    # 9
        [4, 5, 6, 9, 11],     # 10
        [6, 7, 8, 9, 10],     # 11: bottom
    ]
    edges = set()
    for i, neighbors in enumerate(adj):
        for j in neighbors:
            edges.add((min(i, j), max(i, j)))
    return list(edges)


def dodecahedron_edges() -> List[Tuple[int, int]]:
    """
    Generate edges for dodecahedron (20 vertices, 30 edges).
    Each vertex has degree 3.
    """
    # Dodecahedron adjacency (0-indexed)
    adj = [
        [1, 4, 5],
        [0, 2, 6],
        [1, 3, 7],
        [2, 4, 8],
        [0, 3, 9],
        [0, 10, 14],
        [1, 10, 11],
        [2, 11, 12],
        [3, 12, 13],
        [4, 13, 14],
        [5, 6, 15],
        [6, 7, 16],
        [7, 8, 17],
        [8, 9, 18],
        [5, 9, 19],
        [10, 16, 19],
        [10, 11, 17],
        [12, 16, 18],
        [13, 17, 19],
        [14, 15, 18],
    ]
    edges = set()
    for i, neighbors in enumerate(adj):
        for j in neighbors:
            edges.add((min(i, j), max(i, j)))
    return list(edges)


# =============================================================================
# SELF-HEALING METRICS
# =============================================================================

def vertex_connectivity_lower_bound(n: int, edges: List[Tuple[int, int]]) -> int:
    """
    Estimate vertex connectivity (κ) lower bound.
    κ = minimum number of vertices that must be removed to disconnect the graph.
    
    For regular graphs, κ ≤ minimum degree.
    """
    if not edges:
        return 0
    
    # Calculate degree of each vertex
    degree = [0] * n
    for i, j in edges:
        degree[i] += 1
        degree[j] += 1
    
    return min(degree)


def is_connected(n: int, edges: List[Tuple[int, int]]) -> bool:
    """Check if graph is connected using BFS."""
    if n == 0:
        return True
    if not edges:
        return n == 1
    
    adj = {i: set() for i in range(n)}
    for i, j in edges:
        adj[i].add(j)
        adj[j].add(i)
    
    visited = {0}
    queue = [0]
    while queue:
        v = queue.pop(0)
        for u in adj[v]:
            if u not in visited:
                visited.add(u)
                queue.append(u)
    
    return len(visited) == n


def is_connected_after_removal(n: int, edges: List[Tuple[int, int]], remove: int) -> bool:
    """Check if graph remains connected after removing vertex 'remove'."""
    new_n = n - 1
    if new_n == 0:
        return True
    
    # Remap vertices
    remap = {}
    idx = 0
    for i in range(n):
        if i != remove:
            remap[i] = idx
            idx += 1
    
    new_edges = []
    for i, j in edges:
        if i != remove and j != remove:
            new_edges.append((remap[i], remap[j]))
    
    return is_connected(new_n, new_edges)


def healing_score(n: int, edges: List[Tuple[int, int]]) -> float:
    """
    Calculate self-healing score (0.0 to 1.0).
    
    Score = fraction of vertices that can be removed while graph stays connected.
    Perfect score (1.0) = removing any single vertex keeps graph connected.
    """
    if n <= 1:
        return 1.0
    
    connected_count = sum(
        1 for v in range(n) 
        if is_connected_after_removal(n, edges, v)
    )
    
    return connected_count / n


def regularity_score(n: int, edges: List[Tuple[int, int]]) -> float:
    """
    Calculate regularity score (0.0 to 1.0).
    
    1.0 = all vertices have same degree (regular graph).
    """
    if n == 0 or not edges:
        return 0.0
    
    degree = [0] * n
    for i, j in edges:
        degree[i] += 1
        degree[j] += 1
    
    mean_degree = sum(degree) / n
    if mean_degree == 0:
        return 0.0
    
    variance = sum((d - mean_degree) ** 2 for d in degree) / n
    # Normalize: 1 - (std_dev / mean_degree)
    std_dev = math.sqrt(variance)
    return max(0.0, 1.0 - std_dev / mean_degree)


@dataclass
class NetworkAnalysis:
    """Analysis results for a candidate network."""
    candidate: NetworkCandidate
    n_vertices: int
    n_edges: int
    min_degree: int
    max_degree: int
    healing_score: float
    regularity_score: float
    is_connected: bool
    
    @property
    def is_self_healing(self) -> bool:
        """Network is self-healing if score = 1.0 (any vertex removable)."""
        return self.healing_score == 1.0
    
    @property
    def composite_score(self) -> float:
        """Combined metric: healing × regularity."""
        return self.healing_score * self.regularity_score


# =============================================================================
# MAIN ANALYSIS
# =============================================================================

def analyze_platonic(n: int) -> Optional[NetworkAnalysis]:
    """Analyze Platonic solid by vertex count."""
    if n == 4:  # Tetrahedron
        edges = complete_graph_edges(4)
        name = "tetrahedron"
    elif n == 6:  # Octahedron
        # Each vertex connects to 4 others (not the opposite)
        edges = [(i, j) for i in range(6) for j in range(i+1, 6) if i + j != 5]
        name = "octahedron"
    elif n == 8:  # Cube
        # Cube edges
        edges = [
            (0,1), (1,2), (2,3), (3,0),  # bottom
            (4,5), (5,6), (6,7), (7,4),  # top
            (0,4), (1,5), (2,6), (3,7),  # verticals
        ]
        name = "cube"
    elif n == 12:  # Icosahedron
        edges = icosahedron_edges()
        name = "icosahedron"
    elif n == 20:  # Dodecahedron
        edges = dodecahedron_edges()
        name = "dodecahedron"
    else:
        return None
    
    candidate = NetworkCandidate(n, f"{name} vertices", "platonic", (n,))
    return analyze_network(candidate, edges)


def analyze_network(candidate: NetworkCandidate, edges: List[Tuple[int, int]]) -> NetworkAnalysis:
    """Analyze a network given its edges."""
    n = candidate.n
    
    degree = [0] * n
    for i, j in edges:
        degree[i] += 1
        degree[j] += 1
    
    return NetworkAnalysis(
        candidate=candidate,
        n_vertices=n,
        n_edges=len(edges),
        min_degree=min(degree) if degree else 0,
        max_degree=max(degree) if degree else 0,
        healing_score=healing_score(n, edges),
        regularity_score=regularity_score(n, edges),
        is_connected=is_connected(n, edges),
    )


def find_self_healing_sequence(max_n: int = 500) -> List[NetworkAnalysis]:
    """
    Find all self-healing networks up to max_n.
    
    Tests:
    1. Platonic solids
    2. Regular polygons with skip connections
    3. Complete graphs (trivially self-healing but expensive)
    """
    results = []
    
    # Platonic solids
    for n in [4, 6, 8, 12, 20]:
        analysis = analyze_platonic(n)
        if analysis and analysis.is_self_healing:
            results.append(analysis)
    
    # Highly connected regular polygons
    for n in range(3, min(max_n + 1, 100)):
        # Try different connection patterns
        for k in range(1, n // 2):
            edges = regular_polygon_edges(n, k)
            candidate = NetworkCandidate(n, f"C_{n} with k={k}", "circular", (n, k))
            analysis = analyze_network(candidate, edges)
            if analysis.is_self_healing and analysis.regularity_score > 0.99:
                results.append(analysis)
                break  # Found best k for this n
    
    return results


def test_egyptian_candidates() -> Dict[int, NetworkAnalysis]:
    """
    Test the specific candidates from Egyptian architecture.
    
    Key candidates:
    - 12: Confirmed (icosahedron)
    - 36: T(8) = 12 × 3
    - 60: Buckyball
    - 80: Wheel × hourglass
    - 136: T(16)
    - 408: Full grammar
    """
    results = {}
    
    # 12: Icosahedron
    results[12] = analyze_platonic(12)
    
    # For larger structures, we need to define their topology
    # The question is: WHAT topology makes them self-healing?
    
    # Hypothesis: Self-healing requires k-regular graph where k ≥ 3
    # and the graph is k-vertex-connected
    
    candidates = [36, 60, 80, 120, 136, 240, 408]
    
    for n in candidates:
        # Try to find a self-healing configuration
        # Start with regular polygon with sufficient connections
        best_k = None
        best_score = 0
        
        for k in range(3, min(n // 2, 20)):
            edges = regular_polygon_edges(n, k)
            candidate = NetworkCandidate(n, f"circular k={k}", "test", (n, k))
            analysis = analyze_network(candidate, edges)
            
            if analysis.composite_score > best_score:
                best_score = analysis.composite_score
                best_k = k
                results[n] = analysis
        
        # If we didn't find a perfect one, record the best
        if n not in results and best_k:
            edges = regular_polygon_edges(n, best_k)
            candidate = NetworkCandidate(n, f"circular k={best_k}", "test", (n, best_k))
            results[n] = analyze_network(candidate, edges)
    
    return results


# =============================================================================
# CLI / REPORTING
# =============================================================================

def print_analysis(analysis: NetworkAnalysis):
    """Pretty print network analysis."""
    c = analysis.candidate
    print(f"\n{'='*50}")
    print(f"N = {c.n} ({c.derivation})")
    print(f"{'='*50}")
    print(f"  Family:       {c.family}")
    print(f"  Triangular:   {c.is_triangular} {f'[T({c.triangular_index})]' if c.is_triangular else ''}")
    print(f"  Vertices:     {analysis.n_vertices}")
    print(f"  Edges:        {analysis.n_edges}")
    print(f"  Degree:       {analysis.min_degree}-{analysis.max_degree}")
    print(f"  Connected:    {analysis.is_connected}")
    print(f"  Healing:      {analysis.healing_score:.2%}")
    print(f"  Regularity:   {analysis.regularity_score:.2%}")
    print(f"  SELF-HEALING: {'✓ YES' if analysis.is_self_healing else '✗ no'}")


def report_egyptian_candidates():
    """Generate report on Egyptian architecture candidates."""
    print("\n" + "="*60)
    print("SELF-HEALING NETWORK CANDIDATES (Egyptian Architecture)")
    print("="*60)
    
    results = test_egyptian_candidates()
    
    # Sort by size
    for n in sorted(results.keys()):
        print_analysis(results[n])
    
    # Summary
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    
    self_healing = [n for n, a in results.items() if a.is_self_healing]
    print(f"\nSelf-healing networks found: {self_healing}")
    
    # The sequence
    print("\nHypothesized sequence: 12 → ? → ? → 408")
    print("Testing intermediate structures...")


if __name__ == "__main__":
    report_egyptian_candidates()
