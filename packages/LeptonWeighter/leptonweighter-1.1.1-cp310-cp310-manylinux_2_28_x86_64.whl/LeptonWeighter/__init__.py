"""
LeptonWeighter - Weights injected neutrino final states to neutrino fluxes.

This module provides tools for weighting neutrino events from LeptonInjector
simulations to physical neutrino fluxes.

Basic usage:
    import LeptonWeighter as LW

    # Load generators from LIC file
    generators = LW.MakeGeneratorsFromLICFile("config.lic")

    # Load cross sections
    xs = LW.CrossSectionFromSpline(cc_nu, cc_nubar, nc_nu, nc_nubar)

    # Create flux model
    flux = LW.PowerLawFlux(1e-18, -2.0, 1e5)

    # Create weighter and weight events
    weighter = LW.Weighter(flux, xs, generators)
    weight = weighter(event)
"""

import importlib as _importlib

# Import the compiled extension module
# The extension is named LeptonWeighter.so and lives in the same directory
_ext_module = _importlib.import_module('.LeptonWeighter', __name__)

# Export all public symbols from compiled extension
for _name in dir(_ext_module):
    if not _name.startswith('_'):
        globals()[_name] = getattr(_ext_module, _name)

# Clean up temporary variable
del _name

# Version - keep in sync with pyproject.toml and configure
__version__ = "1.1.1"

# Convenience: list commonly used classes for tab completion
__all__ = [
    # Generators
    'Generator',
    'RangeGenerator',
    'VolumeGenerator',
    'SimulationDetails',
    'RangeSimulationDetails',
    'VolumeSimulationDetails',
    'MakeGeneratorsFromLICFile',
    # Events
    'Event',
    'ParticleType',
    # Flux models
    'Flux',
    'ConstantFlux',
    'PowerLawFlux',
    # Cross sections
    'CrossSection',
    'CrossSectionFromSpline',
    # Weighter
    'Weighter',
]

# Conditionally add nuSQuIDS classes if available
if hasattr(_ext_module, 'nuSQUIDSAtmFlux'):
    __all__.extend([
        'nuSQUIDSAtmFlux',
        'nuSQUIDSFlux',
        'GlashowResonanceCrossSection',
    ])
