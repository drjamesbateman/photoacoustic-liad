# Photoacoustic LIAD Simulations

Numerical simulations of laser-induced acoustic desorption: short laser pulses heating metal substrates, generating propagating acoustic waves.

Implementation uses scalar photoacoustic equation with Green's function propagation, cylindrical symmetry solutions, and Monte Carlo integration for full 3D cases.

## Quick Start

```bash
# Single scenario calculation
python3 photoacoustic.py Northup

# Compare multiple scenarios
python3 compare.py

# Generate all figures
make
```

## Data Files

- `experiments.yaml` - Experimental scenarios with laser parameters and geometry
- `materials.yaml` - Material properties (density, sound velocity, thermal expansion, etc.)
- `optical_properties.yaml` - Complex refractive indices and derived optical properties from database

## Experiment Provenance

**Northup**: Paper reference. 3 mJ at 532 nm, 5 ns pulse, 200 μm beam diameter (waist = 100 μm), 250 μm Al foil.

**Standa_W, Standa_Ti, Standa_StSt, Standa_Al**: STA-01-7-OEM laser specification at 1064 nm.

**Standa_StSt_foil**: STA-01-7-OEM laser specification at 1064 nm. Thinner foil configuration.

**uFlash_Ti**: Integrated Optics uFlash 1030U-11C specification. Actual wavelength 1030 nm, using 1064 nm (closest available) in calculations. Pulse energy from "typical" spec value.

**Millen**: Published experimental data. Peak intensity 588 GW/cm², beam waist 17 μm, duration 4.6 ns. Calculated energy: 0.5×π×(17μm/2)² × 588GW/cm² × 4.6ns = 3mJ.

## Data Flow

```
refractiveindex.info database
         ↓ optical_properties.py
  optical_properties.yaml
         ↓ update_experiments.py
    experiments.yaml
         ↓
      simulations
```

To update optical properties after database changes:
```bash
python3 optical_properties.py      # Extract from database
python3 update_experiments.py      # Sync to experiments.yaml
```

## Scripts

### Core simulation

- **`photoacoustic.py`** - Main simulation module; computes time-domain signals

  ```bash
  python3 photoacoustic.py Northup
  ```

- **`verify.py`** - Validates cylindrical vs Monte Carlo integration methods

  ```bash
  python3 verify.py Northup
  ```

### Visualization

- **`compare.py`** - Multi-scenario comparison plots

  ```bash
  python3 compare.py
  ```

- **`diffraction.py`** - Diffraction analysis and visualization

  ```bash
  python3 diffraction.py
  ```

### Optical properties

- **`optical_properties.py`** - Extract optical constants from [refractiveindex.info](https://refractiveindex.info) database

  ```bash
  git clone https://github.com/polyanskiy/refractiveindex.info-database
  python3 optical_properties.py
  ```

  Extracts (n, κ) and computes skin depth, absorption coefficient, reflectance → `optical_properties.yaml`

- **`update_experiments.py`** - Sync optical properties to experiments

  ```bash
  python3 update_experiments.py
  ```

  Updates `skin_depth` and `absorption` in `experiments.yaml` from `optical_properties.yaml` based on each experiment's `material` and `wavelength` fields.

## Makefile Targets

```bash
make                                # Build all figures
make comparison.pdf                 # Multi-scenario comparison plot
make spacetime.pdf                  # Evolution of on-axis in different regimes
make diffraction.pdf                # Spatial visualisation of different regimes

# Convenience targets
make optical_properties.yaml        # Extract optical properties from database
make verify CASE=Northup            # Verify integration methods
make clean                          # Remove generated files
```

