"""
Main CLI Entry Point
====================

Unified command-line interface for cosmic simulations.
Enhanced with progress bars, validation, and configuration support.
"""

import argparse
import sys


# Lazy imports for faster CLI startup
def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        prog="sim",
        description="Unified Cosmological Simulation Framework",
        epilog="For detailed help, use: sim <command> --help",
    )

    parser.add_argument("--version", "-v", action="store_true", help="Show version and exit")

    parser.add_argument(
        "--config", "-c", type=str, metavar="FILE", help="Configuration file (YAML/JSON)"
    )

    parser.add_argument("--verbose", action="store_true", help="Enable verbose logging")

    parser.add_argument("--quiet", "-q", action="store_true", help="Suppress progress output")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Info command
    info_parser = subparsers.add_parser("info", help="Show library information")
    info_parser.add_argument("--gpu", action="store_true", help="Show GPU information")

    # Quantum command
    quantum_parser = subparsers.add_parser("quantum", help="Run quantum simulation")
    quantum_parser.add_argument(
        "--qubits", "-n", type=int, default=3, help="Number of qubits (1-20)"
    )
    quantum_parser.add_argument("--entangle", "-e", action="store_true", help="Create entanglement")
    quantum_parser.add_argument("--gpu", action="store_true", help="Use GPU acceleration")

    # Cosmic command
    cosmic_parser = subparsers.add_parser("cosmic", help="Run N-body simulation")
    cosmic_parser.add_argument(
        "--system",
        "-s",
        choices=["solar", "binary", "earth-moon", "three-body"],
        default="earth-moon",
        help="Preset system",
    )
    cosmic_parser.add_argument("--days", "-d", type=float, default=30, help="Simulation days (> 0)")
    cosmic_parser.add_argument(
        "--points", "-p", type=int, default=1000, help="Number of output points"
    )
    cosmic_parser.add_argument(
        "--integrator",
        "-i",
        choices=["rk45", "verlet", "leapfrog", "yoshida4"],
        default="rk45",
        help="Integration method",
    )
    cosmic_parser.add_argument("--save", type=str, metavar="FILE", help="Save trajectory to file")

    # Coherence command
    coherence_parser = subparsers.add_parser("coherence", help="Run coherence simulation")
    coherence_parser.add_argument(
        "--stages", "-n", type=int, default=12, help="Number of stages (1-100)"
    )
    coherence_parser.add_argument(
        "--alpha", "-a", type=float, default=0.66, help="Alpha parameter (0-1)"
    )

    # Genesis command
    genesis_parser = subparsers.add_parser("genesis", help="Run matter genesis simulation")
    genesis_parser.add_argument(
        "--time", "-t", type=float, default=1000, help="Simulation time (> 0)"
    )
    genesis_parser.add_argument("--dt", type=float, default=1.0, help="Time step")

    # Holographic command
    holo_parser = subparsers.add_parser("holographic", help="Run holographic analysis")
    holo_parser.add_argument("--report", "-r", action="store_true", help="Generate full report")

    # Config command
    config_parser = subparsers.add_parser("config", help="Configuration management")
    config_parser.add_argument(
        "--generate", "-g", type=str, metavar="FILE", help="Generate example config file"
    )
    config_parser.add_argument("--validate", type=str, metavar="FILE", help="Validate config file")

    args = parser.parse_args()

    # Setup logging
    if args.verbose:
        import logging

        from sim.core.logging import setup_logging

        setup_logging(level=logging.DEBUG)

    # Load config if provided
    if args.config:
        from sim.core.config import load_config

        try:
            load_config(args.config)
            if not args.quiet:
                print(f"Loaded configuration from {args.config}")
        except Exception as e:
            print(f"Error loading config: {e}", file=sys.stderr)
            return 1

    if args.version:
        from sim import __version__

        print(f"sim version {__version__}")
        return 0

    if args.command == "info":
        return cmd_info(args)
    elif args.command == "quantum":
        return cmd_quantum(args)
    elif args.command == "cosmic":
        return cmd_cosmic(args)
    elif args.command == "coherence":
        return cmd_coherence(args)
    elif args.command == "genesis":
        return cmd_genesis(args)
    elif args.command == "holographic":
        return cmd_holographic(args)
    elif args.command == "config":
        return cmd_config(args)
    else:
        parser.print_help()
        return 0


def cmd_info(args):
    """Show library information."""
    from sim import __version__

    print(
        f"""
╔══════════════════════════════════════════════════════════════╗
║          Unified Cosmological Simulation Framework           ║
║                        Version {__version__}                          ║
╠══════════════════════════════════════════════════════════════╣
║  Modules:                                                    ║
║    • quantum     - Quantum mechanics & emergence             ║
║    • cosmic      - N-body gravitational dynamics             ║
║    • coherence   - Universe coherence evolution              ║
║    • genesis     - Early universe matter creation            ║
║    • holographic - Information capacity analysis             ║
║                                                              ║
║  Usage: sim <command> [options]                              ║
║  Examples:                                                   ║
║    sim quantum --qubits 5 --entangle                        ║
║    sim cosmic --system solar --days 365                     ║
║    sim coherence --stages 24 --alpha 0.66                   ║
║    sim holographic --report                                  ║
╚══════════════════════════════════════════════════════════════╝
"""
    )

    if args.gpu:
        from sim.core.gpu import get_gpu_info

        info = get_gpu_info()
        print("GPU Information:")
        print(f"  Available: {info['gpu_available']}")
        print(f"  Backends: {', '.join(info['backends'])}")
        if "cuda" in info:
            cuda_info = info["cuda"]
            print(f"  CUDA Device: {cuda_info['device']}")
            print(
                f"  Memory: {cuda_info['memory_free_gb']:.1f} GB free / "
                f"{cuda_info['memory_total_gb']:.1f} GB total"
            )

    return 0


def cmd_quantum(args):
    """Run quantum simulation."""
    from sim.core.progress import ProgressTracker
    from sim.quantum import QuantumFabric

    # Validate
    if not 1 <= args.qubits <= 20:
        print("Error: qubits must be between 1 and 20", file=sys.stderr)
        return 1

    print(f"Creating quantum system with {args.qubits} qubits...")
    qf = QuantumFabric(num_qubits=args.qubits, use_gpu=args.gpu if args.gpu else None)
    print(qf.get_state_info())

    if args.entangle:
        pairs = [(i, i + 1) for i in range(args.qubits - 1)]
        print(f"Creating entanglement between pairs: {pairs}")

        with ProgressTracker(
            len(pairs), desc="Entangling", disable=getattr(args, "quiet", False)
        ) as pbar:
            for pair in pairs:
                qf.apply_entanglement_operator([pair])
                pbar.update()

        print(qf.get_state_info())
        print(f"Entanglement entropy: {qf.get_entanglement_entropy():.4f}")

    # Measure all qubits
    print("\nMeasurements:")
    for i in range(args.qubits):
        qf_copy = QuantumFabric(num_qubits=args.qubits)
        if args.entangle:
            qf_copy.apply_entanglement_operator(pairs)
        result = qf_copy.measure(i)
        print(f"  Qubit {i}: |{result}>")

    return 0


def cmd_cosmic(args):
    """Run N-body simulation."""
    from sim.cosmic import NBodySimulator, SystemPresets

    # Validate
    if args.days <= 0:
        print("Error: days must be > 0", file=sys.stderr)
        return 1

    presets = SystemPresets()

    print(f"Creating {args.system} system...")

    if args.system == "solar":
        bodies = presets.create_solar_system(include_outer_planets=False)
    elif args.system == "binary":
        bodies = presets.create_binary_star_system()
    elif args.system == "earth-moon":
        bodies = presets.create_earth_moon_system()
    elif args.system == "three-body":
        bodies = presets.create_three_body_problem()
    else:
        bodies = presets.create_earth_moon_system()

    print(f"Bodies: {[b.name for b in bodies]}")

    sim = NBodySimulator(bodies)
    t_span = (0, args.days * 24 * 3600)

    print(f"Running simulation for {args.days} days ({args.points} points)...")
    print(f"Integrator: {args.integrator}")

    # Progress tracking
    step_count = [0]

    def progress_callback(t, bodies):
        step_count[0] += 1
        if step_count[0] % 100 == 0 and not getattr(args, "quiet", False):
            print(f"  Step {step_count[0]}, t = {t/86400:.2f} days", end="\r")

    times, states = sim.simulate(t_span, n_points=args.points, callback=progress_callback)

    print("\n")
    print("Results:")
    print(f"  Total energy: {sim.get_total_energy():.4e} J")
    print(f"  Center of mass: {sim.get_center_of_mass()}")
    print(f"  Total momentum: {sim.get_total_momentum()}")

    initial_e, change = sim.get_energy_conservation()
    print(f"  Energy conservation: {abs(change)*100:.6f}% change")

    if args.save:
        from sim.core.checkpoint import save_checkpoint

        save_checkpoint(
            state={"times": times, "states": states},
            name="cosmic_sim",
            simulation_type="cosmic",
            step=len(times),
            parameters={"system": args.system, "days": args.days},
        )
        print("  Saved to checkpoint")

    return 0


def cmd_coherence(args):
    """Run coherence simulation."""
    from sim.coherence import CoherenceModel
    from sim.constants import UNIVERSE_STAGES
    from sim.core.progress import ProgressTracker

    # Validate
    if not 1 <= args.stages <= 100:
        print("Error: stages must be between 1 and 100", file=sys.stderr)
        return 1
    if not 0 < args.alpha <= 1:
        print("Error: alpha must be in (0, 1]", file=sys.stderr)
        return 1

    print(f"Running coherence evolution with N={args.stages}, α={args.alpha}")

    model = CoherenceModel()

    with ProgressTracker(
        args.stages, desc="Computing", disable=getattr(args, "quiet", False)
    ) as pbar:
        K, C, Total = model.evolve(N=args.stages, alpha=args.alpha)
        pbar.update(args.stages)

    print("\nCoherence Evolution:")
    for i in range(min(args.stages, len(UNIVERSE_STAGES))):
        stage = UNIVERSE_STAGES[i] if i < len(UNIVERSE_STAGES) else f"Stage {i}"
        print(f"  {stage:20s}: K = {K[i]:.4f}")

    if args.stages > len(UNIVERSE_STAGES):
        print(f"  ... ({args.stages - len(UNIVERSE_STAGES)} more stages)")
        print(f"  Stage {args.stages-1:15}: K = {K[-1]:.4f}")

    print(f"\nGrowth factor: {K[-1]/K[0]:.2f}x")

    # Information analysis
    info = model.information_content(K)
    print(f"Entropy: {info['entropy']:.4f} bits")
    print(f"Efficiency: {info['efficiency']:.2%}")

    return 0


def cmd_genesis(args):
    """Run matter genesis simulation."""
    from sim.core.progress import ProgressTracker
    from sim.genesis import MatterGenesisSimulation

    # Validate
    if args.time <= 0:
        print("Error: time must be > 0", file=sys.stderr)
        return 1

    print(f"Running matter genesis simulation (t = {args.time})...")

    sim = MatterGenesisSimulation()

    n_steps = int(args.time / args.dt)
    with ProgressTracker(
        n_steps, desc="Evolving universe", disable=getattr(args, "quiet", False)
    ) as pbar:
        history = sim.evolve_universe(total_time=args.time, dt=args.dt)
        pbar.update(n_steps)

    summary = sim.get_summary(history)

    print("\nSimulation Summary:")
    print(f"  Steps: {summary['n_steps']}")
    print(f"  Final temperature: {summary['final_temperature']:.2e} GeV")
    print(f"  Reheating time: {summary['reheating_time']}")
    print(f"  Baryon-to-photon ratio: {summary['baryon_to_photon']:.2e}")
    print("\n  Final composition:")
    for component, fraction in summary["composition"].items():
        print(f"    {component}: {fraction:.2%}")

    return 0


def cmd_holographic(args):
    """Run holographic analysis."""
    from sim.core.progress import ProgressTracker
    from sim.holographic import HolographicAnalysis, UniverseFormulaReport

    if args.report:
        print("Generating full holographic report...")
        report = UniverseFormulaReport()
        report.run_final_report()
    else:
        print("Running holographic analysis...")

        analysis = HolographicAnalysis()

        with ProgressTracker(
            10, desc="Analyzing models", disable=getattr(args, "quiet", False)
        ) as pbar:
            results = analysis.analyze_all_models()
            pbar.update(10)

        print(f"\nResults across {len(results['models'])} cosmological models:")
        print(f"  Mean k: {results['mean_k']:.6f}")
        print(f"  Std k: {results['std_k']:.6f}")
        print(f"  k/α: {results['mean_k_over_alpha']:.2f}")
        print(f"  Error vs 66α: {results['mean_error_vs_66alpha']:.2f}%")

    return 0


def cmd_config(args):
    """Configuration management."""
    if args.generate:
        from sim.core.config import generate_example_config

        path = generate_example_config(args.generate)
        print(f"Generated example configuration: {path}")
        return 0

    if args.validate:
        from sim.core.config import SimulationConfig

        try:
            config = SimulationConfig.from_file(args.validate)
            config.validate()
            print(f"Configuration valid: {args.validate}")
            return 0
        except Exception as e:
            print(f"Configuration invalid: {e}", file=sys.stderr)
            return 1

    print("Use --generate FILE to create example config")
    print("Use --validate FILE to validate config")
    return 0


if __name__ == "__main__":
    sys.exit(main())
