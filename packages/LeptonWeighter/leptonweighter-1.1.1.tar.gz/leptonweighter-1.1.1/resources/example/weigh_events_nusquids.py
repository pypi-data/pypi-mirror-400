#!/usr/bin/env python
"""
weigh_events_nusquids.py - LeptonWeighter Example with nuSQuIDS Atmospheric Flux

This calculates the weight of each event using atmospheric neutrino fluxes
from nuSQuIDS. Requires LeptonWeighter to be built with nuSQuIDS support.

Usage:
    python weigh_events_nusquids.py --lic config.lic --events data.h5 \
        --nuSQFluxKaon kaon_flux.hdf5 --nuSQFluxPion pion_flux.hdf5

Author: Carlos A. Arguelles
"""

import LeptonWeighter as LW
import numpy as np
import tables
import argparse
import os
import sys

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(SCRIPT_DIR, "..", "data")


def parse_args():
    parser = argparse.ArgumentParser(
        description='LeptonWeighter example with nuSQuIDS atmospheric flux.',
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # Input files
    parser.add_argument('--lic', '-l', default=os.path.join(SCRIPT_DIR, "config.lic"),
                        help='Path to LeptonInjector configuration file')
    parser.add_argument('--events', '-e', required=False,
                        help='Path to HDF5 file with events (required)')

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

    # nuSQuIDS flux files
    parser.add_argument('--nuSQFluxKaon', required=False,
                        help='nuSQuIDS kaon component atmospheric flux file (required)')
    parser.add_argument('--nuSQFluxPion', required=False,
                        help='nuSQuIDS pion component atmospheric flux file (required)')

    parser.add_argument('--output', '-o', default="out",
                        help='Output file prefix')

    return parser.parse_args()


def check_nusquids_support():
    """Check if LeptonWeighter was built with nuSQuIDS support."""
    if not hasattr(LW, 'nuSQUIDSAtmFlux'):
        print("ERROR: LeptonWeighter was not built with nuSQuIDS support.")
        print("       Rebuild with: ./configure --with-nusquids=/path/to/nusquids")
        print()
        print("       For a simpler example without nuSQuIDS, try LI_example.py")
        sys.exit(1)


def main():
    args = parse_args()

    # Check for nuSQuIDS support
    check_nusquids_support()

    # Check required arguments
    if args.events is None:
        print("ERROR: --events is required")
        print("       Example: python example.py --events data.h5 --nuSQFluxKaon kaon.hdf5 --nuSQFluxPion pion.hdf5")
        sys.exit(1)

    if args.nuSQFluxKaon is None or args.nuSQFluxPion is None:
        print("ERROR: --nuSQFluxKaon and --nuSQFluxPion are required")
        print("       Example: python example.py --events data.h5 --nuSQFluxKaon kaon.hdf5 --nuSQFluxPion pion.hdf5")
        sys.exit(1)

    print("LeptonWeighter nuSQuIDS Atmospheric Flux Example")
    print("=" * 50)
    print(f"LIC file: {args.lic}")
    print(f"Events file: {args.events}")
    print(f"Kaon flux: {args.nuSQFluxKaon}")
    print(f"Pion flux: {args.nuSQFluxPion}")
    print()

    # Setup LeptonWeighter
    simulation_generators = LW.MakeGeneratorsFromLICFile(args.lic)
    print(f"Loaded {len(simulation_generators)} generator(s) from LIC file")

    # Load nuSQuIDS fluxes
    pion_nusquids_flux = LW.nuSQUIDSAtmFlux(args.nuSQFluxPion)
    kaon_nusquids_flux = LW.nuSQUIDSAtmFlux(args.nuSQFluxKaon)

    # Load cross sections
    xs = LW.CrossSectionFromSpline(
        args.xs_nu_cc,
        args.xs_nubar_cc,
        args.xs_nu_nc,
        args.xs_nubar_nc
    )

    # Create weighter with both flux components
    weighter = LW.Weighter([pion_nusquids_flux, kaon_nusquids_flux], xs, simulation_generators)

    # Read events from file
    h5file = tables.open_file(args.events, "r")

    print()
    print("Event Weights:")
    print("-" * 50)

    for i, event in enumerate(h5file.root.EventProperties[:]):
        LWevent = LW.Event()
        # Field indices correspond to the struct layout in the HDF5 file
        LWevent.primary_type = LW.ParticleType(int(event[12]))
        LWevent.final_state_particle_0 = LW.ParticleType(int(event[10]))
        LWevent.final_state_particle_1 = LW.ParticleType(int(event[11]))
        LWevent.interaction_x = event[8]
        LWevent.interaction_y = event[9]
        LWevent.energy = event[5]
        LWevent.zenith = event[6]
        LWevent.azimuth = event[7]
        LWevent.x = 0.
        LWevent.y = 0.
        LWevent.z = event[16]
        LWevent.radius = event[15]
        LWevent.total_column_depth = event[14]

        weight = weighter(LWevent)
        print(f"Event {i}: E={LWevent.energy:.2e} GeV, weight={weight:.6e}")

    h5file.close()
    print()
    print(f"Processed {i+1} events")


if __name__ == "__main__":
    main()
