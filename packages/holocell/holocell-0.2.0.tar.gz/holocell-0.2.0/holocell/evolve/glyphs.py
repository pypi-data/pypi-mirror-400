"""
Frozen Glyphs — Symbolic Number Sets for GEP

A GlyphSet defines named symbols with computed values.
Any expression produced using glyphs is automatically elegant.

Adapted from GEPEvolver for HoloCell integration.
"""

import math
from dataclasses import dataclass
from typing import Dict, List, Optional


@dataclass
class Glyph:
    """A frozen symbolic constant."""
    symbol: str      # Internal symbol (single char for Karva)
    name: str        # Human-readable name (e.g., "T₁₁", "8³")
    value: float     # Computed numeric value
    formula: str     # How it's computed (e.g., "T(11)", "8**3")
    
    def __repr__(self):
        return f"{self.name}={self.value}"


class GlyphSet:
    """
    A configurable set of frozen glyphs.
    
    Provides:
    - Symbol → Value mapping (for evaluation)
    - Symbol → Name mapping (for display)
    - Validation of which symbols are allowed
    """
    
    def __init__(self, name: str = "custom"):
        self.name = name
        self.glyphs: Dict[str, Glyph] = {}
        self._symbols: List[str] = []
    
    def add(self, symbol: str, name: str, value: float, formula: str = "") -> 'GlyphSet':
        """Add a glyph. Returns self for chaining."""
        if len(symbol) != 1:
            raise ValueError(f"Symbol must be single char, got '{symbol}'")
        glyph = Glyph(symbol=symbol, name=name, value=value, formula=formula or name)
        self.glyphs[symbol] = glyph
        if symbol not in self._symbols:
            self._symbols.append(symbol)
        return self
    
    @property
    def symbols(self) -> List[str]:
        """List of valid terminal symbols."""
        return self._symbols.copy()
    
    def value(self, symbol: str) -> float:
        """Get numeric value of a symbol."""
        if symbol in self.glyphs:
            return self.glyphs[symbol].value
        return float('nan')
    
    def display(self, symbol: str) -> str:
        """Get human-readable name of a symbol."""
        if symbol in self.glyphs:
            return self.glyphs[symbol].name
        return symbol
    
    def __contains__(self, symbol: str) -> bool:
        return symbol in self.glyphs
    
    def __len__(self) -> int:
        return len(self.glyphs)
    
    def __repr__(self):
        return f"GlyphSet({self.name}, {len(self)} glyphs)"
    
    def describe(self) -> str:
        """Full description of all glyphs."""
        lines = [f"GlyphSet: {self.name}", "-" * 40]
        for sym in self._symbols:
            g = self.glyphs[sym]
            lines.append(f"  {sym} = {g.name:>10} = {g.value:>15.6f}  [{g.formula}]")
        return "\n".join(lines)

    # =========================================================================
    # PRESET GLYPH SETS
    # =========================================================================

    @classmethod
    def triangulars(cls) -> 'GlyphSet':
        """Key triangular numbers."""
        gs = cls("triangulars")
        def T(n): return n * (n + 1) // 2
        
        gs.add('a', 'T₂', T(2), 'T(2)')      # 3
        gs.add('b', 'T₃', T(3), 'T(3)')      # 6
        gs.add('c', 'T₄', T(4), 'T(4)')      # 10
        gs.add('d', 'T₅', T(5), 'T(5)')      # 15
        gs.add('e', 'T₆', T(6), 'T(6)')      # 21
        gs.add('f', 'T₇', T(7), 'T(7)')      # 28
        gs.add('g', 'T₈', T(8), 'T(8)')      # 36
        gs.add('h', 'T₉', T(9), 'T(9)')      # 45
        gs.add('i', 'T₁₀', T(10), 'T(10)')   # 55
        gs.add('j', 'T₁₁', T(11), 'T(11)')   # 66
        gs.add('k', 'T₃₆', T(36), 'T(36)')   # 666
        return gs
    
    @classmethod
    def transcendentals(cls) -> 'GlyphSet':
        """Mathematical constants."""
        gs = cls("transcendentals")
        gs.add('p', 'π', math.pi, 'pi')
        gs.add('e', 'e', math.e, 'e')
        gs.add('f', 'φ', (1 + math.sqrt(5)) / 2, 'phi')
        return gs

    @classmethod
    def holocell(cls, seed: int = 136) -> 'GlyphSet':
        """
        HoloCell glyph set — architecture integers + transcendentals.
        The constrained search space for methodology replication.
        """
        gs = cls("holocell")
        def T(n): return n * (n + 1) // 2
        
        # Transcendentals
        gs.add('p', 'π', math.pi, 'pi')
        gs.add('e', 'e', math.e, 'e')
        gs.add('f', 'φ', (1 + math.sqrt(5)) / 2, 'phi')
        
        # Architecture integers
        gs.add('1', '1', 1, '1')
        gs.add('2', '2', 2, '2')
        gs.add('3', '3', 3, '3')
        gs.add('7', '7', 7, '7')
        gs.add('9', '9', 9, '9')
        
        # Key triangulars
        gs.add('a', 'T₄', T(4), 'T(4)')      # 10
        gs.add('b', 'T₇', T(7), 'T(7)')      # 28
        gs.add('c', 'T₈', T(8), 'T(8)')      # 36
        gs.add('d', 'T₁₁', T(11), 'T(11)')   # 66
        gs.add('k', 'T₃₆', T(36), 'T(36)')   # 666
        
        # Architecture numbers
        gs.add('A', '11', 11, '11')
        gs.add('B', '16', 16, '16')
        gs.add('C', '44', 44, '44')
        gs.add('D', '60', 60, '60')
        gs.add('E', '72', 72, '72')
        
        # The seed (or candidate seed for testing)
        gs.add('S', f'seed({seed})', seed, f'seed={seed}')
        
        return gs

    @classmethod
    def seed_test(cls, seed: int) -> 'GlyphSet':
        """
        Glyph set for seed testing.
        Identical to holocell() but with specified seed.
        """
        return cls.holocell(seed=seed)

    @classmethod
    def custom(cls, specs: List[tuple]) -> 'GlyphSet':
        """
        Build from list of (symbol, name, value) tuples.
        
        Example:
            GlyphSet.custom([
                ('a', 'π', math.pi),
                ('b', '36', 36),
            ])
        """
        gs = cls("custom")
        for spec in specs:
            if len(spec) == 3:
                sym, name, val = spec
                gs.add(sym, name, val, name)
            elif len(spec) == 4:
                sym, name, val, formula = spec
                gs.add(sym, name, val, formula)
        return gs
