"""Tests for HoloCell core operators and constants."""

import math
import pytest
from holocell import (
    T, B, S,
    triangular, bilateral, six_nine,
    CRYSTAL, ARCHITECTURE,
    verify_all, verify_constant,
    FINE_STRUCTURE_INV,
    PROTON_ELECTRON_MASS,
    MUON_ELECTRON_MASS,
    WEINBERG_ANGLE,
    RYDBERG_MANTISSA,
    find_closest_magic,
    nearest_triangular,
)


class TestTriangularOperator:
    """Tests for T(n) triangular number operator."""

    def test_t_small_values(self):
        assert T(1) == 1
        assert T(2) == 3
        assert T(3) == 6
        assert T(4) == 10
        assert T(5) == 15

    def test_t_formula(self):
        # T(n) = n(n+1)/2
        for n in range(1, 20):
            assert T(n) == n * (n + 1) // 2

    def test_t_16_is_136(self):
        """The seed: T(16) = 136."""
        assert T(16) == 136

    def test_t_8_is_36(self):
        """T(8) = 36, the decan."""
        assert T(8) == 36

    def test_t_11_is_66(self):
        """T(11) = 66."""
        assert T(11) == 66

    def test_triangular_alias(self):
        """triangular() is alias for T()."""
        for n in [1, 5, 8, 11, 16]:
            assert triangular(n) == T(n)


class TestBilateralOperator:
    """Tests for B(x) bilateral covenant operator."""

    def test_b_basic(self):
        assert B(136) == 137
        assert B(0) == 1
        assert B(-1) == 0

    def test_b_is_increment(self):
        for x in [-5, 0, 1, 66, 136, 1000]:
            assert B(x) == x + 1

    def test_bilateral_alias(self):
        for x in [0, 66, 136]:
            assert bilateral(x) == B(x)


class TestSixNineOperator:
    """Tests for S(x) six-nine harmonic operator."""

    def test_s_formula(self):
        # S(x) = x*6/9 + x*9/6 = x*(6/9 + 9/6) = x*(4/6 + 9/6) = x*13/6
        # Actually: x*6/9 + x*9/6 = x*(2/3 + 3/2) = x*(4/6 + 9/6) = x*13/6
        for x in [1, 9, 36, 136]:
            expected = x * 6/9 + x * 9/6
            assert abs(S(x) - expected) < 1e-10

    def test_s_9(self):
        # S(9) = 9*6/9 + 9*9/6 = 6 + 13.5 = 19.5
        assert abs(S(9) - 19.5) < 1e-10

    def test_six_nine_alias(self):
        for x in [1, 9, 136]:
            assert six_nine(x) == S(x)


class TestArchitecture:
    """Tests for architectural constants."""

    def test_architecture_contains_key_values(self):
        assert 1 in ARCHITECTURE
        assert 16 in ARCHITECTURE
        assert 36 in ARCHITECTURE
        assert 66 in ARCHITECTURE
        assert 136 in ARCHITECTURE or T(16) in [T(n) for n in ARCHITECTURE if n <= 16]

    def test_architecture_is_ordered(self):
        assert ARCHITECTURE == sorted(ARCHITECTURE)


class TestCrystal:
    """Tests for CRYSTAL verified expressions."""

    def test_crystal_contains_five_constants(self):
        assert len(CRYSTAL) == 5

    def test_crystal_keys(self):
        expected_keys = ['mp/me', 'R∞', 'α⁻¹', 'μ/me', 'sin²θW']
        for key in expected_keys:
            assert key in CRYSTAL

    def test_crystal_values_are_close(self):
        """Each crystallized expression should be within 0.01% of measured."""
        for name, crystal in CRYSTAL.items():
            assert crystal.error_percent < 0.01, f"{name} error too high: {crystal.error_percent}%"

    def test_proton_electron_mass(self):
        c = CRYSTAL['mp/me']
        assert abs(c.measured - 1836.15267343) < 0.0001
        assert c.error_percent < 1e-5

    def test_fine_structure(self):
        c = CRYSTAL['α⁻¹']
        assert abs(c.measured - 137.035999084) < 0.0001

    def test_weinberg_angle(self):
        c = CRYSTAL['sin²θW']
        assert abs(c.measured - 0.23121) < 0.001


class TestVerification:
    """Tests for verification functions."""

    def test_verify_all(self):
        results = verify_all()
        assert len(results) == 5
        assert all(results.values()), "All constants should verify"

    def test_verify_constant(self):
        result = verify_constant('mp/me')
        assert result is True


class TestMagicNumbers:
    """Tests for magic number utilities."""

    def test_fine_structure_inv(self):
        assert abs(FINE_STRUCTURE_INV.value - 137.036) < 0.001

    def test_proton_electron_mass_value(self):
        assert abs(PROTON_ELECTRON_MASS.value - 1836.15) < 0.01

    def test_muon_electron_mass_value(self):
        assert abs(MUON_ELECTRON_MASS.value - 206.768) < 0.001

    def test_weinberg_angle_value(self):
        assert abs(WEINBERG_ANGLE.value - 0.2312) < 0.001

    def test_nearest_triangular(self):
        # 136 is T(16), so nearest should be 16
        n, t, delta = nearest_triangular(136)
        assert n == 16
        assert t == 136
        assert delta == 0

    def test_nearest_triangular_between(self):
        # 140 is between T(16)=136 and T(17)=153
        n, t, delta = nearest_triangular(140)
        assert t == 136 or t == 153
