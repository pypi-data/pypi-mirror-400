import argparse
from .gbm_simulator import GBMSimulator


def main():
    """
    Entry point for the pygbm command-line interface.

    Parses command-line arguments, runs a Geometric Brownian Motion
    simulation using the specified parameters, and produces a plot
    of the simulated path.
    """
    parser = argparse.ArgumentParser(description="Simulate Geometric Brownian Motion")
    subparsers = parser.add_subparsers(dest="command", required=True)

    sim = subparsers.add_parser("simulate", help="Simulate a GBM path and plot it")
    sim.add_argument("--y0", type=float, required=True, help="Initial value Y(0)")
    sim.add_argument("--mu", type=float, required=True, help="Drift coefficient")
    sim.add_argument("--sigma", type=float, required=True, help="Diffusion coefficient")
    sim.add_argument("--T", type=float, required=True, help="Total time for simulation")
    sim.add_argument("--N", type=int, required=True, help="Number of time steps")
    sim.add_argument("--output", type=str, help="Output file for the plot")

    args = parser.parse_args()

    if args.command == "simulate":
        simulator = GBMSimulator(args.y0, args.mu, args.sigma)
        t_values, y_values = simulator.simulate_path(args.T, args.N)
        simulator.plot_path(t_values, y_values, output=args.output)


if __name__ == "__main__":
    main()
