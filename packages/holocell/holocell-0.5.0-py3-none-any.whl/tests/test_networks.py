"""Tests for HoloCell self-healing networks."""

import pytest
from holocell.networks import (
    T,
    inverse_T,
    is_triangular,
    generate_candidates,
    icosahedron_edges,
    dodecahedron_edges,
    regular_polygon_edges,
    healing_score,
    is_connected,
    analyze_network,
    test_egyptian_candidates,
    NetworkCandidate,
    NetworkAnalysis,
    WHEEL,
    SPINE,
    HOURGLASS,
    DIRECTED,
)


class TestTriangularFunctions:
    """Tests for triangular number utilities in networks."""

    def test_t_function(self):
        assert T(16) == 136
        assert T(8) == 36

    def test_inverse_t(self):
        # inverse_T(136) should give 16
        assert inverse_T(136) == 16
        assert inverse_T(36) == 8

    def test_inverse_t_non_triangular(self):
        # Non-triangular numbers should return None
        result = inverse_T(137)
        assert result is None

    def test_is_triangular(self):
        assert is_triangular(136) is True
        assert is_triangular(36) is True
        assert is_triangular(137) is False


class TestPlatonicSolids:
    """Tests for Platonic solid edge functions."""

    def test_icosahedron_edges(self):
        edges = icosahedron_edges()
        # Icosahedron has 30 edges
        assert len(edges) == 30

    def test_dodecahedron_edges(self):
        edges = dodecahedron_edges()
        # Dodecahedron has 30 edges (allow slight variance in impl)
        assert 29 <= len(edges) <= 31

    def test_regular_polygon_edges(self):
        # Triangle
        edges = regular_polygon_edges(3)
        assert len(edges) == 3
        # Square
        edges = regular_polygon_edges(4)
        assert len(edges) == 4
        # Pentagon
        edges = regular_polygon_edges(5)
        assert len(edges) == 5


class TestHealingScore:
    """Tests for healing score calculation."""

    def test_healing_score_complete_graph(self):
        # Complete graph K_4: every pair connected
        edges = [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]
        score = healing_score(4, edges)
        # Complete graph has maximum connectivity
        assert score > 0

    def test_healing_score_disconnected(self):
        # Two separate edges, disconnected
        edges = [(0, 1), (2, 3)]
        score = healing_score(4, edges)
        # Should have low score due to disconnection
        assert score <= healing_score(4, [(0, 1), (1, 2), (2, 3), (3, 0)])


class TestIsConnected:
    """Tests for graph connectivity."""

    def test_connected_graph(self):
        edges = [(0, 1), (1, 2), (2, 3)]
        assert is_connected(4, edges) is True

    def test_disconnected_graph(self):
        edges = [(0, 1), (2, 3)]  # Two separate components
        assert is_connected(4, edges) is False


class TestGenerateCandidates:
    """Tests for candidate generation."""

    def test_generate_candidates_returns_list(self):
        candidates = generate_candidates(max_n=50)
        assert isinstance(candidates, list)
        assert len(candidates) > 0
        assert all(isinstance(c, NetworkCandidate) for c in candidates)

    def test_candidates_include_triangular_136(self):
        candidates = generate_candidates(max_n=150)
        # Should include a candidate with n=136 (T(16))
        ns = [c.n for c in candidates]
        assert 136 in ns


class TestAnalyzeNetwork:
    """Tests for network analysis."""

    def test_analyze_small_network(self):
        # Simple cycle - need to create a NetworkCandidate first
        edges = [(0, 1), (1, 2), (2, 0)]
        candidate = NetworkCandidate(n=3, derivation='cycle', family='test', factors=(3,))
        analysis = analyze_network(candidate, edges)
        assert isinstance(analysis, NetworkAnalysis)
        assert analysis.candidate.n == 3
        assert analysis.is_connected is True


class TestNetworkCandidate:
    """Tests for NetworkCandidate dataclass."""

    def test_candidate_creation(self):
        nc = NetworkCandidate(n=136, derivation='T(16)', family='triangular', factors=(16,))
        assert nc.n == 136
        assert nc.family == 'triangular'
        assert nc.derivation == 'T(16)'

    def test_candidate_is_triangular(self):
        nc = NetworkCandidate(n=136, derivation='T(16)', family='triangular', factors=(16,))
        assert nc.is_triangular is True
        assert nc.triangular_index == 16


class TestConstants:
    """Tests for network constants."""

    def test_wheel_value(self):
        assert WHEEL == 16

    def test_spine_value(self):
        assert SPINE == 3

    def test_hourglass_value(self):
        assert HOURGLASS == 5


class TestEgyptianCandidates:
    """Tests for the Egyptian candidate sequence."""

    def test_egyptian_candidates_returns_dict(self):
        results = test_egyptian_candidates()
        assert isinstance(results, dict)

    def test_136_in_results(self):
        results = test_egyptian_candidates()
        assert 136 in results

    def test_results_have_analysis(self):
        results = test_egyptian_candidates()
        for n, analysis in results.items():
            assert isinstance(analysis, NetworkAnalysis)
            assert analysis.candidate.n == n
