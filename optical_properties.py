#!/usr/bin/env python3
"""
Extract optical constants from refractiveindex.info database.

Usage:
    python3 optical_properties.py
"""

import sys
import numpy as np
import yaml

OUTPUT_FILE = 'optical_properties.yaml'

def complex_refractive_to_optical_properties(n, kappa, wavelength):
    """
    Convert literature optical properties to photoacoustic model parameters.

    Parameters:
    -----------
    n : float
        Real refractive index (dimensionless)
    kappa : float
        Extinction coefficient (dimensionless)
    wavelength : float
        Wavelength in meters

    Returns:
    --------
    dict with keys:
        'skin_depth' : float (meters)
        'absorption_coefficient' : float (dimensionless)
        'reflectance' : float (dimensionless)
    """

    # Skin depth for intensity absorption: xi = lambda/(4*pi*kappa)
    k0 = 2 * np.pi / wavelength  # vacuum wave vector
    skin_depth = 1 / (2 * k0 * kappa)  # intensity skin depth

    # Reflectance from Fresnel formula (appendix_optical.tex Eq. A6)
    numerator = (n - 1)**2 + kappa**2
    denominator = (n + 1)**2 + kappa**2
    reflectance = numerator / denominator

    # Absorption coefficient (fraction of incident power absorbed)
    absorption_coefficient = 1 - reflectance

    return {
        'skin_depth': skin_depth,
        'absorption_coefficient': absorption_coefficient,
        'reflectance': reflectance
    }

def extract_from_database():
    """Extract optical constants from refractiveindex.info database."""
    # Database path (clone from https://github.com/polyanskiy/refractiveindex.info-database)
    db_path = "refractiveindex.info-database/database/data/main"

    # Wavelengths we need (in microns)
    wavelengths = [0.532, 1.064]

    # Materials and their data files
    materials = {
        'Al': 'Al/nk/Rakic.yml',
        'Ti': 'Ti/nk/Johnson.yml',
        'Fe': 'Fe/nk/Johnson.yml',
        'W': 'W/nk/Ordal.yml'
    }

    print(f"Extracting optical constants from refractiveindex.info database")
    print("=" * 70)

    yaml_entries = []

    for material, filepath in materials.items():
        print(f"\n{material}:")

        # Read YAML file
        full_path = f"{db_path}/{filepath}"
        with open(full_path, 'r') as f:
            data = yaml.safe_load(f)

        # Print citation
        citation = data['REFERENCES'].strip()
        print(f"  Citation: {citation[:100]}...")

        # Extract tabulated nk data
        data_block = data['DATA'][0]
        rows = data_block['data'].strip().split('\n')

        # Parse into arrays
        wl_data = []
        n_data = []
        k_data = []
        for row in rows:
            parts = row.split()
            if len(parts) == 3:
                wl_data.append(float(parts[0]))
                n_data.append(float(parts[1]))
                k_data.append(float(parts[2]))

        wl_data = np.array(wl_data)
        n_data = np.array(n_data)
        k_data = np.array(k_data)

        # Interpolate at our wavelengths and convert
        for wl in wavelengths:
            n = np.interp(wl, wl_data, n_data)
            kappa = np.interp(wl, wl_data, k_data)

            # Convert using conversion function
            wl_meters = wl * 1e-6
            props = complex_refractive_to_optical_properties(n, kappa, wl_meters)

            # Display results
            print(f"  λ={wl*1000:.0f}nm: n={n:.3f}, κ={kappa:.3f} → "
                  f"xi={props['skin_depth']*1e9:.1f}nm, β={props['absorption_coefficient']:.2f}")

            # Build YAML entry with computed quantities
            yaml_entries.append(f"{material}_{int(wl*1000)}nm:\n"
                              f"  n: {n:.3f}\n"
                              f"  kappa: {kappa:.3f}\n"
                              f"  wavelength: {wl_meters:.2e}\n"
                              f"  skin_depth: {props['skin_depth']:.3e}\n"
                              f"  absorption_coefficient: {props['absorption_coefficient']:.3f}\n"
                              f"  reflectance: {props['reflectance']:.3f}\n")

    print("\n" + "=" * 70)
    print(f"Writing to {OUTPUT_FILE}...")

    # Write YAML to file
    with open(OUTPUT_FILE, 'w') as f:
        f.write("# Optical properties from refractiveindex.info database\n")
        f.write("# Values extracted using optical_properties.py\n")
        f.write("# See script for citations and sources\n\n")
        for entry in yaml_entries:
            f.write(entry)

    print(f"Done! Wrote {len(yaml_entries)} entries to {OUTPUT_FILE}")
    print("=" * 70)

if __name__ == "__main__":
    extract_from_database()
