#!/usr/bin/env python
"""
read_lic.py - Read LeptonInjector Configuration File

Reads a LeptonInjector Configuration (LIC) file and prints the simulation
parameters for each generator. This is the Python equivalent of read_lic.cpp.

Usage:
    python read_lic.py                    # Use default config.lic
    python read_lic.py --lic config.lic   # Specify LIC file

Author: Carlos A. Arguelles
"""

import LeptonWeighter as LW
import argparse
import os
import sys

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Particle type name mapping
PARTICLE_NAMES = {
    12: "NuE",
    -12: "NuEBar",
    14: "NuMu",
    -14: "NuMuBar",
    16: "NuTau",
    -16: "NuTauBar",
    11: "EMinus",
    -11: "EPlus",
    13: "MuMinus",
    -13: "MuPlus",
    15: "TauMinus",
    -15: "TauPlus",
    0: "unknown",
    -2000001006: "Hadrons",
}


def get_particle_name(ptype):
    """Get human-readable particle name from ParticleType."""
    ptype_int = int(ptype)
    return PARTICLE_NAMES.get(ptype_int, f"Unknown({ptype_int})")


def parse_args():
    parser = argparse.ArgumentParser(
        description='Read LeptonInjector configuration file and print simulation details.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    parser.add_argument('--lic', '-l', default=os.path.join(SCRIPT_DIR, "config.lic"),
                        help='Path to LeptonInjector configuration file')
    parser.add_argument('--verbose', '-v', action='store_true',
                        help='Print additional details')

    return parser.parse_args()


def print_simulation_details(sim_details, generator_num):
    """Print simulation details for a generator."""
    print(f"Simulation details of generator {generator_num}")
    print("-" * 40)
    print(f"  Number of events:        {sim_details.numberOfEvents}")
    print(f"  Final state particle 0:  {get_particle_name(sim_details.final_state_particle_0)} ({int(sim_details.final_state_particle_0)})")
    print(f"  Final state particle 1:  {get_particle_name(sim_details.final_state_particle_1)} ({int(sim_details.final_state_particle_1)})")
    print(f"  Energy range:            [{sim_details.energyMin:.2e}, {sim_details.energyMax:.2e}] GeV")
    print(f"  Zenith range:            [{sim_details.zenithMin:.4f}, {sim_details.zenithMax:.4f}] rad")
    print(f"  Azimuth range:           [{sim_details.azimuthMin:.4f}, {sim_details.azimuthMax:.4f}] rad")
    print(f"  Power-law index:         {sim_details.powerlawIndex}")
    print()


def main():
    args = parse_args()

    if not os.path.exists(args.lic):
        print(f"ERROR: LIC file not found: {args.lic}")
        sys.exit(1)

    print("LeptonInjector Configuration Reader")
    print("=" * 40)
    print(f"LIC file: {args.lic}")
    print()

    # Load generators from LIC file
    generators = LW.MakeGeneratorsFromLICFile(args.lic)

    print(f"Number of generators in LIC file: {len(generators)}")
    print()

    # Print details for each generator
    for i, generator in enumerate(generators, start=1):
        # Try to get simulation details
        # The generator exposes simulation details through properties
        try:
            # For RangeGenerator
            sim_details = generator.range_sim_details
            print_simulation_details(sim_details, i)
        except AttributeError:
            try:
                # For VolumeGenerator
                sim_details = generator.volume_sim_details
                print_simulation_details(sim_details, i)
            except AttributeError:
                print(f"Generator {i}: Unable to retrieve simulation details")
                print()


if __name__ == "__main__":
    main()
