#!/usr/bin/env python
"""
weigh_events.py - Basic LeptonWeighter Example with Power-Law Flux

This calculates the weight of each event using a simple power-law flux model.
Can be run directly with default parameters or customized via command-line arguments.
Does not require nuSQuIDS.

Usage:
    python weigh_events.py                    # Use defaults
    python weigh_events.py --help             # Show all options
    python weigh_events.py --lic config.lic   # Specify LIC file

Author: Ben Smithers (benjamin.smithers@mavs.uta.edu)
Modified: Carlos A. Arguelles
"""

import LeptonWeighter as LW
import h5py as h5
import numpy as np
import argparse
import os

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")

def parse_args():
    parser = argparse.ArgumentParser(
        description='LeptonWeighter example with power-law flux.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Input files
    parser.add_argument('--lic', default=os.path.join(SCRIPT_DIR, "config.lic"),
                        help='Path to LeptonInjector configuration file')
    parser.add_argument('--events', default=os.path.join(SCRIPT_DIR, "data_output.h5"),
                        help='Path to HDF5 file with events')

    # Cross section splines
    parser.add_argument('--xs-nu-cc',
                        default=os.path.join(DATA_DIR, "dsdxdy-numu-N-cc-HERAPDF15NLO_EIG_central.fits"),
                        help='Neutrino CC differential cross section spline')
    parser.add_argument('--xs-nubar-cc',
                        default=os.path.join(DATA_DIR, "dsdxdy-numubar-N-cc-HERAPDF15NLO_EIG_central.fits"),
                        help='Antineutrino CC differential cross section spline')
    parser.add_argument('--xs-nu-nc',
                        default=os.path.join(DATA_DIR, "dsdxdy-numu-N-nc-HERAPDF15NLO_EIG_central.fits"),
                        help='Neutrino NC differential cross section spline')
    parser.add_argument('--xs-nubar-nc',
                        default=os.path.join(DATA_DIR, "dsdxdy-numubar-N-nc-HERAPDF15NLO_EIG_central.fits"),
                        help='Antineutrino NC differential cross section spline')

    # Flux parameters
    parser.add_argument('--flux-norm', type=float, default=1e-18,
                        help='Flux normalization (GeV^-1 cm^-2 sr^-1 s^-1)')
    parser.add_argument('--flux-index', type=float, default=-2.0,
                        help='Spectral index (negative for falling spectrum)')
    parser.add_argument('--flux-pivot', type=float, default=1e5,
                        help='Pivot energy (GeV)')

    # Livetime
    parser.add_argument('--livetime', type=float, default=3.1536e7,
                        help='Livetime in seconds (default: 1 year)')

    return parser.parse_args()


def get_weight(weight_event, props, livetime):
    """
    Accepts the properties list of an event and returns the weight.

    To convert this to one working with i3-LeptonInjector, you will need
    to modify the event loop and this function.
    """
    LWevent = LW.Event()
    LWevent.energy = props[0]
    LWevent.zenith = props[1]
    LWevent.azimuth = props[2]

    LWevent.interaction_x = props[3]
    LWevent.interaction_y = props[4]
    LWevent.final_state_particle_0 = LW.ParticleType(int(props[5]))
    LWevent.final_state_particle_1 = LW.ParticleType(int(props[6]))
    LWevent.primary_type = LW.ParticleType(int(props[7]))
    LWevent.radius = props[9]
    LWevent.total_column_depth = props[10]
    LWevent.x = 0
    LWevent.y = 0
    LWevent.z = 0

    weight = weight_event(LWevent)

    if np.isnan(weight):
        raise ValueError("Bad Weight!")

    return weight * livetime


def main():
    args = parse_args()

    print("LeptonWeighter Power-Law Flux Example")
    print("=" * 40)
    print(f"LIC file: {args.lic}")
    print(f"Events file: {args.events}")
    print(f"Flux: {args.flux_norm:.2e} * (E/{args.flux_pivot:.0e} GeV)^{args.flux_index}")
    print(f"Livetime: {args.livetime:.2e} s")
    print()

    # Create generator from LIC file
    # If there were multiple LIC files, you would make a list of Generators
    net_generation = LW.MakeGeneratorsFromLICFile(args.lic)
    print(f"Loaded {len(net_generation)} generator(s) from LIC file")

    # Load cross sections
    # This cross section object takes four differential cross sections (dS/dEdxdy):
    #   - Neutrino CC-DIS xs
    #   - Anti-Neutrino CC-DIS xs
    #   - Neutrino NC-DIS xs
    #   - Anti-Neutrino NC-DIS xs
    xs = LW.CrossSectionFromSpline(
        args.xs_nu_cc,
        args.xs_nubar_cc,
        args.xs_nu_nc,
        args.xs_nubar_nc
    )

    # Create flux model
    flux = LW.PowerLawFlux(args.flux_norm, args.flux_index, args.flux_pivot)

    # Build weighter
    weight_event = LW.Weighter(flux, xs, net_generation)

    # Load data and weight events
    print()
    print("Event Weights (rate * livetime):")
    print("-" * 40)

    data_file = h5.File(args.events, 'r')

    total_events = 0
    for injector in data_file.keys():
        events = data_file[injector]['properties']
        for event_idx in range(len(events)):
            weight = get_weight(weight_event, events[event_idx], args.livetime)
            print(f"Event {total_events}: {weight:.6e}")
            total_events += 1

    data_file.close()
    print()
    print(f"Processed {total_events} events")


if __name__ == "__main__":
    main()
