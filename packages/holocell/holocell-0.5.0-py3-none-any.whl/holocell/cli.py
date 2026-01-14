"""
HoloCell CLI — Command-line interface for the Five Modes of Sight.

Usage:
    holocell verify              # Verify crystallized expressions
    holocell evolve <constant>   # Mode 1: Fixed Focus
    holocell seed-test           # Mode 1: Seed comparison
    holocell coherent            # Mode 2: Coherent Zoom
    holocell seth                # Mode 3: Seth Mode
    holocell moonpools           # Mode 4: Moon Pools
    holocell sweep               # Mode 5: Coherence Test
"""

import argparse
import sys


def cmd_verify():
    """Verify all crystallized expressions."""
    from holocell import verify_all, CRYSTAL

    print("\n" + "=" * 60)
    print("HOLOCELL CRYSTAL VERIFICATION")
    print("=" * 60 + "\n")

    results = verify_all()

    for name, passed in results.items():
        c = CRYSTAL[name]
        status = "✓" if passed else "✗"
        print(f"{status} {c.symbol:>10}: {c.error_percent:.2e}% error")

    total_pass = sum(results.values())
    print(f"\n{total_pass}/{len(results)} passed verification\n")

    return 0 if all(results.values()) else 1


def cmd_evolve(args):
    """Mode 1: Fixed Focus - evolve expression for a single constant."""
    from holocell.modes import evolve_constant

    result = evolve_constant(
        args.constant,
        seed_value=args.seed,
        generations=args.generations,
        pop_size=args.population,
        verbose=True,
    )

    return 0 if result.error_percent < 0.01 else 1


def cmd_seed_test(args):
    """Mode 1: Seed testing - compare candidate seeds."""
    from holocell.modes import test_seeds
    from holocell.modes.targets import CANDIDATE_SEEDS

    seeds = CANDIDATE_SEEDS if args.all else [136, 137, 66, 36, 11]

    ranking = test_seeds(
        seeds=seeds,
        generations_per_target=args.generations,
        pop_size=args.population,
        verbose=True,
    )

    return 0


def cmd_coherent(args):
    """Mode 2: Coherent Zoom - co-evolve integer set."""
    from holocell.modes import evolve_coherent

    result = evolve_coherent(
        integer_set_size=args.integers,
        pop_size=args.population,
        generations=args.generations,
        verbose=True,
    )

    return 0 if result.converged else 1


def cmd_seth(args):
    """Mode 3: Seth Mode - dual set partition."""
    from holocell.modes import evolve_seth

    result = evolve_seth(
        pop_size=args.population,
        generations=args.generations,
        verbose=True,
    )

    return 0 if result.converged else 1


def cmd_moonpools(args):
    """Mode 4: Moon Pools - multi-pool triangulation."""
    from holocell.modes import run_moon_pools

    result = run_moon_pools(
        num_pools=args.pools,
        max_runtime_seconds=args.runtime,
        verbose=True,
    )

    return 0


def cmd_sweep(args):
    """Mode 5: Coherence Test - N-node corruption sweep."""
    from holocell.modes import run_coherence_sweep

    result = run_coherence_sweep(
        max_corruption=args.max_corruption,
        trials_per_level=args.trials,
        verbose=True,
    )

    print(f"\nFault tolerance: {result.fault_tolerance_threshold} nodes")
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="HoloCell: T(16) = 136 as the eigenvalue of physics constants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
FIVE MODES OF SIGHT:

  Mode 1: Fixed Focus    — Standard GEP with fixed terminals
      holocell evolve alpha
      holocell seed-test

  Mode 2: Coherent Zoom  — Co-evolve integer set itself
      holocell coherent

  Mode 3: Seth Mode      — Dual set partition (archive/transmitted)
      holocell seth

  Mode 4: Moon Pools     — Multi-pool eigenvalue triangulation
      holocell moonpools

  Mode 5: Coherence Test — N-node corruption sweep
      holocell sweep

VERIFICATION:
      holocell verify         — Verify crystallized expressions

Constants (for Mode 1):
    alpha     Fine structure constant inverse (α⁻¹)
    proton    Proton-electron mass ratio (mp/me)
    muon      Muon-electron mass ratio (μ/me)
    weinberg  Weinberg angle (sin²θW)
    rydberg   Rydberg constant mantissa (R∞)
        """
    )

    subparsers = parser.add_subparsers(dest="command", help="Command")

    # verify
    subparsers.add_parser("verify", help="Verify crystallized expressions")

    # evolve (Mode 1)
    sub_evolve = subparsers.add_parser("evolve", help="Mode 1: Evolve expression for a constant")
    sub_evolve.add_argument("constant", help="Constant name (alpha, proton, muon, weinberg, rydberg)")
    sub_evolve.add_argument("--seed", type=int, default=136, help="Seed value (default: 136)")
    sub_evolve.add_argument("--generations", type=int, default=1000, help="Max generations")
    sub_evolve.add_argument("--population", type=int, default=300, help="Population size")

    # seed-test (Mode 1)
    sub_seed = subparsers.add_parser("seed-test", help="Mode 1: Test candidate seeds")
    sub_seed.add_argument("--all", action="store_true", help="Test all candidate seeds")
    sub_seed.add_argument("--generations", type=int, default=500, help="Generations per target")
    sub_seed.add_argument("--population", type=int, default=200, help="Population size")

    # coherent (Mode 2)
    sub_coh = subparsers.add_parser("coherent", help="Mode 2: Coherent Zoom")
    sub_coh.add_argument("--integers", type=int, default=6, help="Integer set size (default: 6)")
    sub_coh.add_argument("--generations", type=int, default=2000, help="Max generations")
    sub_coh.add_argument("--population", type=int, default=300, help="Population size")

    # seth (Mode 3)
    sub_seth = subparsers.add_parser("seth", help="Mode 3: Seth Mode (dual partition)")
    sub_seth.add_argument("--generations", type=int, default=3000, help="Max generations")
    sub_seth.add_argument("--population", type=int, default=400, help="Population size")

    # moonpools (Mode 4)
    sub_moon = subparsers.add_parser("moonpools", help="Mode 4: Moon Pools")
    sub_moon.add_argument("--pools", type=int, default=4, help="Number of pools (default: 4)")
    sub_moon.add_argument("--runtime", type=float, default=180, help="Max runtime seconds")

    # sweep (Mode 5)
    sub_sweep = subparsers.add_parser("sweep", help="Mode 5: Coherence Test sweep")
    sub_sweep.add_argument("--max-corruption", type=int, default=8, help="Max corruption level")
    sub_sweep.add_argument("--trials", type=int, default=3, help="Trials per level")

    args = parser.parse_args()

    if args.command is None:
        parser.print_help()
        return 0

    commands = {
        "verify": cmd_verify,
        "evolve": lambda: cmd_evolve(args),
        "seed-test": lambda: cmd_seed_test(args),
        "coherent": lambda: cmd_coherent(args),
        "seth": lambda: cmd_seth(args),
        "moonpools": lambda: cmd_moonpools(args),
        "sweep": lambda: cmd_sweep(args),
    }

    handler = commands.get(args.command)
    if handler:
        return handler() if callable(handler) and handler.__name__ == '<lambda>' else handler()

    return 0


if __name__ == "__main__":
    sys.exit(main())
