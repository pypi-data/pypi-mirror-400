# LeptonWeighter

Weights injected neutrino final states to neutrino fluxes.

Author: C.A. Arg\"uelles

Reviewer: A. Schneider, B. Smithers

If there are any problems do not hesitate to email: carguelles@fas.harvard.edu

Prerequisites
-------------

The following libraries are required:

* C++11 capable compiler
* GSL (>= 1.15): http://www.gnu.org/software/gsl/
* HDF5 with C bindings: http://www.hdfgroup.org/HDF5/
* Photospline (v2): https://github.com/icecube/photospline

Optional (recommended):

* SQuIDS (>= 1.2): https://github.com/jsalvado/SQuIDS/ - Required by nuSQuIDS
* nuSQuIDS (>= 1.0): https://github.com/arguelles/nuSQuIDS - Enables nuSQuIDS flux interfaces and tau decay corrections
* nuflux: https://github.com/icecube/nuflux - Enables nuflux interface (requires Boost headers)

For Python bindings, you also need:

* numpy: http://www.numpy.org/
* pybind11 (default) or Boost.Python (legacy)

Configuration
-------------

Use the provided configure script:

	./configure --help

Basic configuration:

	./configure --with-squids=/path/to/squids --with-nusquids=/path/to/nusquids

The configure script will automatically detect most dependencies via pkg-config. You can manually specify paths if needed:

	./configure --with-gsl=/path/to/gsl \
	            --with-hdf5=/path/to/hdf5 \
	            --with-squids=/path/to/squids \
	            --with-nusquids=/path/to/nusquids \
	            --with-photospline-config=/path/to/photospline-config

Building
--------

Once configuration is complete, compile the library:

	make

Compile example programs:

	make examples

The examples can be found in `resources/example/`.

Installing
----------

Install the library (default location: `/usr/local`):

	make install

To change the installation prefix:

	./configure --prefix=$HOME/local

Python Bindings
---------------

LeptonWeighter supports two Python binding backends:

### pybind11 (default, recommended)

To build Python bindings using pybind11:

	./configure --with-python-bindings
	make
	make python

pybind11 is detected automatically via pip. If not installed:

	pip install pybind11

Additional options:

	# Specify pybind11 headers location
	./configure --with-python-bindings --with-pybind-incdir=/path/to/pybind11/include

	# Specify Python executable
	./configure --with-python-bindings --python-bin=/path/to/python

### Boost.Python (legacy)

To use Boost.Python instead:

	./configure --with-boost-python-bindings --with-boost=/path/to/boost
	make
	make python

### Installing Python bindings

Install to the system Python path:

	make python-install

Or add the library directory to your PYTHONPATH:

	export PYTHONPATH=/path/to/LeptonWeighter/lib:$PYTHONPATH

### Using the Python module

After installation:

```python
import LeptonWeighter as LW

# Create a flux model
flux = LW.PowerLawFlux(1e-18, 2.0, 1e5)

# Load cross sections from splines
xs = LW.CrossSectionFromSpline("cc_nu.fits", "cc_nubar.fits",
                                "nc_nu.fits", "nc_nubar.fits")

# Load generators from LIC file
generators = LW.MakeGeneratorsFromLICFile("simulation.lic")

# Create weighter
weighter = LW.Weighter(flux, xs, generators)

# Weight an event
event = LW.Event()
event.energy = 1e5  # GeV
event.zenith = 1.0  # radians
# ... set other event properties
weight = weighter.weight(event)
```

Optional Dependencies
---------------------

### nuSQuIDS

nuSQuIDS provides advanced neutrino physics functionality. When nuSQuIDS is available, the following features are enabled:

**C++ library:**
* `GlashowResonanceCrossSection` class - Glashow resonance cross section calculations
* `Weighter::get_effective_tau_weight()` - Effective tau neutrino weighting with tau decay corrections
* `Weighter::get_effective_tau_oneweight()` - Effective tau neutrino one-weight calculation

**Python bindings:**
* `nuSQUIDSAtmFlux` - Atmospheric neutrino flux from nuSQuIDS
* `nuSQUIDSFlux` - General nuSQuIDS flux interface
* `GlashowResonanceCrossSection` - Glashow resonance cross section

To enable nuSQuIDS support:

	./configure --with-nusquids=/path/to/nusquids

### nuflux

nuflux provides conventional and prompt atmospheric neutrino flux models. When nuflux is available, the `NFluxInterface` class is enabled for using nuflux flux models.

Note: nuflux requires Boost headers (for `boost::shared_ptr`).

To enable nuflux support:

	./configure --with-nuflux=/path/to/nuflux

Citation
--------

If you use LeptonWeighter in your research, please cite:

```bibtex
@article{IceCube:2020tcq,
    author = "{IceCube Collaboration}",
    title = "{LeptonInjector and LeptonWeighter: A neutrino event generator and weighter for neutrino observatories}",
    eprint = "2012.10449",
    archivePrefix = "arXiv",
    primaryClass = "physics.comp-ph",
    doi = "10.1016/j.cpc.2021.108018",
    journal = "Comput. Phys. Commun.",
    volume = "263",
    pages = "107894",
    year = "2021"
}
```

Detailed Author Contributions
-----------------------------

The LeptonInjector and LeptonWeighter modules were motivated by the high-energy light sterile neutrino search performed by B. Jones and C. Arguelles. C. Weaver wrote the first implementation of LeptonInjector using the IceCube internal software framework, icetray, and wrote the specifications for LeptonWeighter. In doing so, he also significantly enhanced the functionality of IceCube's Earth-model service. These weighting specifications were turned into code by C. Arguelles in LeptonWeighter. B. Jones performed the first detailed Monte Carlo comparisons that showed that this code had similar performance to the standard IceCube neutrino generator at the time for throughgoing muon neutrinos.

It was realized that these codes could have use beyond IceCube and could benefit the broader neutrino community. The codes were copied from IceCube internal subversion repositories to this GitHub repository; unfortunately, the code commit history was not preserved in this process. Thus the current commits do not represent the contributions from the original authors, particularly from the initial work by C. Weaver and C. Arguelles.

The transition to this public version of the code has been spearheaded by A. Schneider and B. Smithers, with significant input and contributions from C. Weaver and C. Arguelles. B. Smithers isolated the components of the code needed to make the code public, edited the examples, and improved the interface of the code. A. Schneider contributed to improving the weighting algorithm, particularly to making it work for volume mode cascades, as well as in writing the general weighting formalism that enables joint weighting of volume and range mode.

This project also received contributions and suggestions from internal IceCube reviewers and the collaboration as a whole.
