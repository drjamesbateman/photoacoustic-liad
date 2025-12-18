#!/usr/bin/env python3
"""
Update experiments.yaml with optical properties from optical_properties.yaml.

Experiment provenance and notes are documented in README.md.

Usage:
    python3 update_experiments.py
"""

import yaml

# Material mapping (StSt uses Fe as proxy in optical_properties.yaml)
MATERIAL_MAP = {'Al': 'Al', 'Ti': 'Ti', 'W': 'W', 'StSt': 'Fe'}

def main():
    # Load optical properties from database
    with open('optical_properties.yaml') as f:
        optical = yaml.safe_load(f)

    # Load experiments
    with open('experiments.yaml') as f:
        experiments = yaml.safe_load(f)

    # Update each experiment with database values
    for name, config in experiments.items():
        if 'wavelength' not in config:
            print(f" {name:20s} skipped (no wavelength specified)")
            continue

        material = MATERIAL_MAP.get(config['material'], config['material'])
        wavelength_nm = int(float(config['wavelength']) * 1e9)  # convert m to nm
        key = f"{material}_{wavelength_nm}nm"

        if key in optical:
            config['skin_depth'] = optical[key]['skin_depth']
            config['absorption'] = optical[key]['absorption_coefficient']
            print(f" {name:20s} updated from {key}")
        else:
            print(f" {name:20s} skipped ({key} not in database)")

    # Write back
    with open('experiments.yaml', 'w') as f:
        yaml.dump(experiments, f, default_flow_style=False, sort_keys=False)

    print(f"\n Updated experiments.yaml")

if __name__ == "__main__":
    main()
