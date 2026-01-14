# HoloCell

**T(16) = 136 as the eigenvalue of fundamental physics constants.**

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.18183435.svg)](https://doi.org/10.5281/zenodo.18183435)
[![PyPI version](https://badge.fury.io/py/holocell.svg)](https://pypi.org/project/holocell/)

## Installation

```bash
pip install holocell
```

Requires [GEPEvolver](https://github.com/worldbridgerstudios/GEPEvolver) (installed automatically).

## Quick Start

```python
from holocell import T, B, S, CRYSTAL, verify_all

# The seed
print(T(16))  # 136

# Verify all 5 constants
results = verify_all()
# {'mp/me': True, 'R∞': True, 'α⁻¹': True, 'μ/me': True, 'sin²θW': True}

# Access a specific crystal constant
proton = CRYSTAL["mp/me"]
print(f"Computed:  {proton.computed}")
print(f"Measured:  {proton.measured}")
print(f"Error:     {proton.error_percent:.2e}%")
```

## The Discovery

Five fundamental physics constants emerge from a single seed: **T(16) = 136**.

| Constant | Expression | Error |
|----------|------------|-------|
| mp/me | T(136) × 3 × (9/2) + (11 - 1/T(16))/72 | **1.21×10⁻⁷%** |
| R∞ | B(T(11) × (√(T(16) + e) + 1/36 + 666)⁻¹) | 1.02×10⁻⁵% |
| α⁻¹ | T(16) + (((e/36 + T(16)) + π) / (T(16) - φ)) | 1.35×10⁻⁵% |
| μ/me | (16 + T(16) + T(16)/28 + 44) + B(S(T(16))/60) | 1.40×10⁻⁵% |
| sin²θW | √((28 - (π + 36/T(16))⁻¹ - 9)⁻¹) | 4.67×10⁻⁴% |

## Five Modes of Sight

HoloCell provides five evolutionary modes for discovering and validating architectural structure:

```python
from holocell.modes import (
    evolve_constant,      # Mode 1: Fixed Focus
    evolve_coherent,      # Mode 2: Coherent Zoom
    evolve_seth,          # Mode 3: Seth Mode
    run_moon_pools,       # Mode 4: Moon Pools
    run_coherence_sweep,  # Mode 5: Coherence Test
)
```

### Mode 1: Fixed Focus
Standard GEP evolution with fixed terminals.
```python
result = evolve_constant("alpha", seed_value=136)
```

### Mode 2: Coherent Zoom
Co-evolve the integer set itself across all constants simultaneously.
```python
result = evolve_coherent(integer_set_size=6)
print(f"Discovered integers: {result.discovered_integers}")
```

### Mode 3: Seth Mode
Dual set partition — discover which constants need the full archive vs filtered subset.
```python
result = evolve_seth()
print(f"Archive: {result.archive}")
print(f"Transmitted: {result.transmitted}")
```

### Mode 4: Moon Pools
Multi-pool eigenvalue triangulation — find crossing bands.
```python
result = run_moon_pools(num_pools=4, max_runtime_seconds=180)
```

### Mode 5: Coherence Test
N-node corruption sweep — measure fault tolerance threshold.
```python
result = run_coherence_sweep(max_corruption=8)
print(f"Fault tolerance: {result.fault_tolerance_threshold} nodes")
```

## Self-Healing Networks

Tools for analyzing self-healing network topologies derived from Platonic solids.

**The Sequence:** 12 → 36 → 60 → 80 → 120 → 136 → 240 → 408

```python
from holocell.networks import test_egyptian_candidates

results = test_egyptian_candidates()
for n, analysis in sorted(results.items()):
    print(f"N={n}: self-healing={analysis.is_self_healing}")
```

## Operators

Three architectural operators from Egyptian cosmological mathematics:

```python
from holocell import T, B, S

T(16)    # 136 — Triangular number: n(n+1)/2
B(T(16)) # 137 — Bilateral covenant: x + 1
S(9)     # 19.5 — Six-nine harmonic: x×6/9 + x×9/6
```

## CLI

```bash
# Verify crystallized expressions
holocell verify

# Mode 1: Fixed Focus
holocell evolve alpha
holocell seed-test

# Mode 2: Coherent Zoom
holocell coherent

# Mode 3: Seth Mode
holocell seth

# Mode 4: Moon Pools
holocell moonpools

# Mode 5: Coherence Test
holocell sweep
```

## License

CC0 1.0 Universal — Public Domain

## Citation

```bibtex
@software{brown2025holocell,
  title={HoloCell: T(16) = 136 as the Eigenvalue of Fundamental Physics Constants},
  author={Brown, Nicholas David},
  year={2025},
  doi={10.5281/zenodo.18183435}
}
```
