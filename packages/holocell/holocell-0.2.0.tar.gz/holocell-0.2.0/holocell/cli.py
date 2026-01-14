"""
HoloCell CLI — Command-line interface for methodology replication.

Usage:
    holocell verify              # Verify crystallized expressions
    holocell evolve <constant>   # Evolve expression for one constant
    holocell seed-test           # Run unified seed testing
    holocell replicate           # Full methodology replication
"""

import argparse
import sys


def cmd_verify():
    """Verify all crystallized expressions."""
    from holocell import verify_all, CRYSTAL
    
    print("\n" + "="*60)
    print("HOLOCELL CRYSTAL VERIFICATION")
    print("="*60 + "\n")
    
    results = verify_all()
    
    for name, passed in results.items():
        c = CRYSTAL[name]
        status = "✓" if passed else "✗"
        print(f"{status} {c.symbol:>10}: {c.error_percent:.2e}% error")
    
    total_pass = sum(results.values())
    print(f"\n{total_pass}/{len(results)} passed verification\n")
    
    return 0 if all(results.values()) else 1


def cmd_evolve(args):
    """Evolve expression for a single constant."""
    from holocell.evolve import evolve_constant
    
    result = evolve_constant(
        args.constant,
        seed_value=args.seed,
        generations=args.generations,
        pop_size=args.population,
        verbose=True,
    )
    
    return 0 if result.error_percent < 0.01 else 1


def cmd_seed_test(args):
    """Run unified seed testing."""
    from holocell.evolve import test_seeds, CANDIDATE_SEEDS
    
    seeds = CANDIDATE_SEEDS if args.all else [136, 137, 66, 36, 11]
    
    ranking = test_seeds(
        seeds=seeds,
        generations_per_target=args.generations,
        pop_size=args.population,
        verbose=True,
    )
    
    return 0


def cmd_replicate(args):
    """Full methodology replication."""
    from holocell.evolve import replicate_methodology
    
    results = replicate_methodology(
        full_seed_test=args.seed_test,
        verbose=True,
    )
    
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="HoloCell: T(16) = 136 as the eigenvalue of physics constants",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    holocell verify              Verify crystallized expressions
    holocell evolve alpha        Evolve expression for α⁻¹
    holocell evolve proton       Evolve expression for mp/me
    holocell seed-test           Test candidate seeds
    holocell replicate           Full methodology replication

Constants:
    alpha     Fine structure constant inverse (α⁻¹)
    proton    Proton-electron mass ratio (mp/me)
    muon      Muon-electron mass ratio (μ/me)
    weinberg  Weinberg angle (sin²θW)
    rydberg   Rydberg constant mantissa (R∞)
        """
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    # verify
    sub_verify = subparsers.add_parser("verify", help="Verify crystallized expressions")
    
    # evolve
    sub_evolve = subparsers.add_parser("evolve", help="Evolve expression for a constant")
    sub_evolve.add_argument("constant", help="Constant name (alpha, proton, muon, weinberg, rydberg)")
    sub_evolve.add_argument("--seed", type=int, default=136, help="Seed value (default: 136)")
    sub_evolve.add_argument("--generations", type=int, default=1000, help="Max generations (default: 1000)")
    sub_evolve.add_argument("--population", type=int, default=300, help="Population size (default: 300)")
    
    # seed-test
    sub_seed = subparsers.add_parser("seed-test", help="Test candidate seeds")
    sub_seed.add_argument("--all", action="store_true", help="Test all candidate seeds")
    sub_seed.add_argument("--generations", type=int, default=500, help="Generations per target")
    sub_seed.add_argument("--population", type=int, default=200, help="Population size")
    
    # replicate
    sub_rep = subparsers.add_parser("replicate", help="Full methodology replication")
    sub_rep.add_argument("--seed-test", action="store_true", help="Include seed testing phase")
    
    args = parser.parse_args()
    
    if args.command is None:
        parser.print_help()
        return 0
    
    if args.command == "verify":
        return cmd_verify()
    elif args.command == "evolve":
        return cmd_evolve(args)
    elif args.command == "seed-test":
        return cmd_seed_test(args)
    elif args.command == "replicate":
        return cmd_replicate(args)
    
    return 0


if __name__ == "__main__":
    sys.exit(main())
