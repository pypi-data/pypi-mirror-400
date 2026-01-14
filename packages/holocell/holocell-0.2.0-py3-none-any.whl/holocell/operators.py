"""
HoloCell Operators

Core mathematical operators derived from Egyptian cosmological architecture:
- T(n): Triangular numbers
- B(x): Bilateral covenant
- S(x): Six-nine harmonic
"""

import math


def T(n: float) -> float:
    """
    Triangular number T(n) = n(n+1)/2
    
    Key values:
        T(8)  = 36   (decans)
        T(11) = 66   (proto-phonemes sum)
        T(16) = 136  (THE SEED)
        T(36) = 666  (cascade)
        T(60) = 1830 (proton base)
    
    Args:
        n: Index (uses floor of absolute value)
    
    Returns:
        The nth triangular number
    """
    if math.isnan(n):
        return float('nan')
    m = int(abs(n))
    return (m * (m + 1)) // 2


def B(x: float) -> float:
    """
    Bilateral covenant operator: B(x) = x + 1
    
    Represents the +1 that completes bilateral symmetry.
    
    Key insight: B(T(16)) = B(136) = 137 ≈ α⁻¹
    
    Args:
        x: Input value
    
    Returns:
        x + 1
    """
    return x + 1


def S(x: float) -> float:
    """
    Six-nine harmonic operator: S(x) = x×(6/9) + x×(9/6)
    
    The 6-9 breath mechanism from vortex cosmology.
    Neith (6) ⇌ Anubis (9) exchange.
    
    Simplifies to: S(x) = x × (6/9 + 9/6) = x × 13/6 ≈ 2.1667x
    
    Args:
        x: Input value
    
    Returns:
        x×6/9 + x×9/6
    """
    return x * 6 / 9 + x * 9 / 6


# Aliases for clarity
triangular = T
bilateral = B
six_nine = S


def inv(x: float) -> float:
    """Protected inverse: 1/x, returns 0 for x=0"""
    return 0 if x == 0 else 1 / x


def sqrt(x: float) -> float:
    """Protected square root: √|x|"""
    return math.sqrt(abs(x))


def sq(x: float) -> float:
    """Square: x²"""
    return x * x
