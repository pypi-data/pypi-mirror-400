# LeptonWeighter Examples

This directory contains example programs demonstrating how to use LeptonWeighter for weighting neutrino events from LeptonInjector simulations.

## Example Overview

Examples are organized by their dependencies:

| Example | Language | nuSQuIDS Required | Description |
|---------|----------|-------------------|-------------|
| `read_lic` | C++ / Python | No | Read LIC file and print simulation parameters |
| `weigh_events` | C++ / Python | No | Weight events with power-law flux |
| `weigh_events_nusquids` | C++ / Python | **Yes** | Weight events with nuSQuIDS atmospheric flux |

## Data Files

The example directory includes sample data files:

- `config.lic` - LeptonInjector configuration file containing simulation parameters
- `data_output.h5` - Sample HDF5 file with simulated neutrino events

Cross-section spline files are located in `../data/`:

- `dsdxdy-numu-N-cc-HERAPDF15NLO_EIG_central.fits` - Neutrino CC differential cross section
- `dsdxdy-numubar-N-cc-HERAPDF15NLO_EIG_central.fits` - Antineutrino CC differential cross section
- `dsdxdy-numu-N-nc-HERAPDF15NLO_EIG_central.fits` - Neutrino NC differential cross section
- `dsdxdy-numubar-N-nc-HERAPDF15NLO_EIG_central.fits` - Antineutrino NC differential cross section

## Python Examples

### read_lic.py

Reads a LeptonInjector Configuration (LIC) file and prints the simulation parameters for each generator.

```bash
# Using defaults (reads config.lic in current directory)
python read_lic.py

# Specify a different LIC file
python read_lic.py --lic path/to/config.lic
```

### weigh_events.py

Demonstrates weighting events with a simple power-law flux model. This is the simplest example and a good starting point. **Does not require nuSQuIDS.**

```bash
# Using defaults (uses local config.lic, data_output.h5, and cross sections from ../data/)
python weigh_events.py

# Specify custom paths
python weigh_events.py --lic config.lic --events data_output.h5

# Customize flux parameters
python weigh_events.py --flux-norm 1e-18 --flux-index -2.5 --flux-pivot 1e5
```

**Default flux parameters:**
- Normalization: 10^-18 GeV^-1 cm^-2 sr^-1 s^-1
- Spectral index: -2
- Pivot energy: 10^5 GeV

### weigh_events_nusquids.py

Demonstrates weighting events with atmospheric neutrino fluxes from nuSQuIDS. **Requires nuSQuIDS support.**

```bash
python weigh_events_nusquids.py --lic config.lic --events data.h5 \
    --nuSQFluxKaon HondaGaisserKaon.hdf5 \
    --nuSQFluxPion HondaGaisserPion.hdf5
```

**Note:** This example requires LeptonWeighter to be built with nuSQuIDS support and appropriate nuSQuIDS flux files.

## C++ Examples

Build the examples with:

```bash
make examples
```

### read_lic

Reads a LIC file and prints simulation parameters. This is the C++ equivalent of `read_lic.py`.

```bash
./read_lic config.lic
```

### weigh_events

Demonstrates weighting events with cross sections (computes OneWeight values). **Does not require nuSQuIDS.**

```bash
./weigh_events config.lic \
    ../data/dsdxdy-numu-N-cc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numu-N-nc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numubar-N-cc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numubar-N-nc-HERAPDF15NLO_EIG_central.fits \
    flux.hdf5 \
    data_output.h5 \
    output
```

### weigh_events_nusquids

Demonstrates weighting events with nuSQuIDS atmospheric flux. **Requires nuSQuIDS support.**

```bash
./weigh_events_nusquids config.lic \
    ../data/dsdxdy-numu-N-cc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numu-N-nc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numubar-N-cc-HERAPDF15NLO_EIG_central.fits \
    ../data/dsdxdy-numubar-N-nc-HERAPDF15NLO_EIG_central.fits \
    nusquids_flux.hdf5 \
    data_output.h5 \
    output
```

## Event Structure

LeptonWeighter events require the following properties:

| Property | Description | Units |
|----------|-------------|-------|
| `energy` | Neutrino energy | GeV |
| `zenith` | Zenith angle | radians |
| `azimuth` | Azimuth angle | radians |
| `interaction_x` | Bjorken x | dimensionless |
| `interaction_y` | Inelasticity y | dimensionless |
| `primary_type` | Initial neutrino type | ParticleType enum |
| `final_state_particle_0` | First final state particle | ParticleType enum |
| `final_state_particle_1` | Second final state particle | ParticleType enum |
| `total_column_depth` | Column depth to interaction | g/cm^2 |
| `radius` | Injection radius | m |
| `x`, `y`, `z` | Interaction vertex position | m |

## Particle Types

Common particle type codes:

| Code | Particle |
|------|----------|
| 12 | NuE |
| -12 | NuEBar |
| 14 | NuMu |
| -14 | NuMuBar |
| 16 | NuTau |
| -16 | NuTauBar |
| 11 | EMinus |
| -11 | EPlus |
| 13 | MuMinus |
| -13 | MuPlus |
| 15 | TauMinus |
| -15 | TauPlus |

## Typical Workflow

1. **Load generators** from the LIC file that was used to generate your Monte Carlo:
   ```python
   generators = LW.MakeGeneratorsFromLICFile("config.lic")
   ```

2. **Load cross sections** from spline files:
   ```python
   xs = LW.CrossSectionFromSpline(cc_nu, cc_nubar, nc_nu, nc_nubar)
   ```

3. **Define a flux model** (power-law or from nuSQuIDS):
   ```python
   flux = LW.PowerLawFlux(1e-18, -2.0, 1e5)
   ```

4. **Create the weighter**:
   ```python
   weighter = LW.Weighter(flux, xs, generators)
   ```

5. **Weight each event**:
   ```python
   weight = weighter(event)
   ```

The weight has units of Hz (events per second) and should be multiplied by livetime to get expected event counts.
