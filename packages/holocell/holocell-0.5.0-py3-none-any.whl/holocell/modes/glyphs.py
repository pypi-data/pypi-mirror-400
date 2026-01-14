"""
HoloCell — Architectural Glyph Sets

GlyphSets specific to HoloCell, built on GEPEvolver.
"""

import math
from gepevolver import GlyphSet

from ..operators import T, B, S


def holocell_glyphs(seed: int = 136) -> GlyphSet:
    """
    Standard HoloCell glyph set with architectural integers.
    
    Args:
        seed: The privileged seed value (default: T(16) = 136)
    """
    gs = GlyphSet("holocell")
    
    # The seed (privileged position)
    gs.add('s', f'seed({seed})', seed, f'T(16)={seed}')
    
    # Architectural integers
    gs.add('1', '1', 1, '1')
    gs.add('7', '7', 7, '7')
    gs.add('9', '9', 9, '9')
    gs.add('b', '11', 11, '11')
    gs.add('w', '16', 16, '16')
    gs.add('f', '28', 28, 'T(7)')
    gs.add('g', '36', 36, 'T(8)')
    gs.add('h', '44', 44, '44')
    gs.add('j', '60', 60, '60')
    gs.add('k', '66', 66, 'T(11)')
    gs.add('m', '666', 666, 'T(36)')
    
    # Transcendentals
    gs.add('p', 'π', math.pi, 'pi')
    gs.add('e', 'e', math.e, 'e')
    gs.add('x', 'φ', (1 + math.sqrt(5)) / 2, 'phi')
    
    return gs


def seed_test_glyphs(seed: int) -> GlyphSet:
    """
    Minimal glyph set for seed comparison testing.
    Only the seed + transcendentals + small integers.
    """
    gs = GlyphSet(f"seed_test_{seed}")
    
    # The seed being tested
    gs.add('s', f'seed({seed})', seed, f'seed={seed}')
    
    # Small building blocks
    gs.add('1', '1', 1, '1')
    gs.add('2', '2', 2, '2')
    gs.add('3', '3', 3, '3')
    gs.add('6', '6', 6, '6')
    gs.add('9', '9', 9, '9')
    
    # Key triangulars
    gs.add('a', 'T(8)', 36, 'T(8)')
    gs.add('b', 'T(11)', 66, 'T(11)')
    
    # Transcendentals
    gs.add('p', 'π', math.pi, 'pi')
    gs.add('e', 'e', math.e, 'e')
    gs.add('x', 'φ', (1 + math.sqrt(5)) / 2, 'phi')
    
    return gs


def coherent_glyphs(integers: list) -> GlyphSet:
    """
    Dynamic glyph set for coherent evolution.
    Terminals are the evolved integer set.
    
    Args:
        integers: List of integers to use as terminals
    """
    gs = GlyphSet("coherent")
    
    # Evolved integers as terminals (I0, I1, I2, ...)
    symbols = "abcdefghijklmnopqrstuvwxyz"
    for i, val in enumerate(integers[:len(symbols)]):
        gs.add(symbols[i], f'I{i}', val, f'integers[{i}]')
    
    # Transcendentals always available
    gs.add('P', 'π', math.pi, 'pi')
    gs.add('E', 'e', math.e, 'e')
    gs.add('X', 'φ', (1 + math.sqrt(5)) / 2, 'phi')
    
    return gs


def architectural_candidates() -> list:
    """
    Candidate integers biased toward architectural values.
    Used for random initialization in coherent modes.
    """
    return [1, 2, 3, 5, 7, 8, 9, 10, 11, 12, 15, 16, 21, 28, 36, 44, 60, 66, 666]
