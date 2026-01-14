from .simulator import Simulation
from .info_parser import get_positions_and_filename
from .read_non_blocking import NonBlockingBytesReader

from subprocess import Popen, PIPE
import sys
import os
import time
import datetime

import argparse

from jelka_validator import DataReader

parser = argparse.ArgumentParser(description="Run Jelka FMF simulation.")

parser.add_argument(
    "run",
    type=str,
    nargs="+",
    help="how to run the program",
)

parser.add_argument(
    "--positions",
    type=str,
    help="specify the file with LED positions, leave empty for automatic detection or random",
    required=False,
)


def main(header_wait: float = 0.5):
    print(
        f"[SIMULATION] You are executing JelkaSim from '{os.getcwd()}' using Python '{sys.executable}'.",
        file=sys.stderr,
        flush=True,
    )

    args = parser.parse_args()

    if len(args.run) == 1 and args.run[0].endswith(".py"):
        # Python file is a special case: run it using the same python that is running this script
        # Python interpreter can be changed by putting it in front of the program name
        target = args.run[0]
        cmd = [sys.executable, target]
    else:
        target = args.run[-1]  # Guess with this
        cmd = args.run

    # Allow specifying a custom path
    if args.positions:
        filenames = [args.positions]
    else:
        # Provide default file locations
        filenames = [
            os.path.join(os.getcwd(), "positions.csv"),
            os.path.join(os.getcwd(), "../../data/positions.csv"),
        ]
        if os.path.dirname(target):
            filenames.append(os.path.join(os.path.dirname(target), "positions.csv"))
            filenames.append(os.path.join(os.path.dirname(target), "../../data/positions.csv"))

    # Resolve relative paths to absolute paths
    filenames = [os.path.abspath(filename) for filename in filenames]

    # Try to load positions from various files
    positions, filename = get_positions_and_filename(filenames)

    # Set environment variables for the target program
    environment = os.environ.copy()
    if filename:
        environment["JELKA_POSITIONS"] = filename

    print(f"[SIMULATION] Running {cmd} at {datetime.datetime.now()}.", file=sys.stderr, flush=True)

    with Popen(cmd, env=environment, stdout=PIPE) as p:
        breader = NonBlockingBytesReader(p.stdout.read1)  # type: ignore
        dr = DataReader(breader.start())  # type: ignore
        dr.update()

        t_start = time.time()
        while time.time() - t_start < header_wait and dr.header is None:
            dr.update()
            time.sleep(0.01)

        if dr.header is None:
            print(
                f"[SIMULATION] No header found in the first {header_wait} seconds. Is your program running?",
                file=sys.stderr,
                flush=True,
            )
            sys.exit(1)

        print("[SIMULATION] Initializing the simulation window.", file=sys.stderr, flush=True)
        sim = Simulation(positions)
        sim.init()

        while sim.running:
            c = next(dr)
            dr.user_print()
            sim.set_colors(dict(zip(range(len(c)), c)))
            sim.frame()

        breader.close()
        sim.quit()

    print(
        f"[SIMULATION] Finished running at {datetime.datetime.now()} (took {time.time() - t_start:.2f} seconds).",
        file=sys.stderr,
        flush=True,
    )
