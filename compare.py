#!/usr/bin/env python3

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})
import os
import yaml

# Use seaborn whitegrid style for publication-quality figures with grid
plt.style.use('seaborn-v0_8-whitegrid')

def load_case_parameters(name):
    """Load experimental parameters for acoustic transit time calculation"""
    with open("experiments.yaml") as h:
        expts = yaml.safe_load(h)        
    with open("materials.yaml") as h:
        materials = yaml.safe_load(h)

    thickness = float(expts[name]['thickness'])
    mat = expts[name]['material']
    v = float(materials[mat]['speed_of_sound'])

    return thickness, v

def load_case(name):
    """Load CSV data and center on acoustic transit time"""
    filename = f"photoacoustic-{name}.csv"
    data = np.loadtxt(filename)
    t, u, a = data[:, 0], data[:, 1], data[:, 2]  # time, velocity, acceleration

    # Calculate acoustic transit time
    thickness, v = load_case_parameters(name)
    if thickness is not None:
        # Convert to μm, ns units for consistency with simulation
        um, ns = 1e-6, 1e-9
        thickness /= um
        v /= (um/ns)
        t_transit = thickness/v

        # Center time axis on acoustic transit
        t_centered = t - t_transit
        return t_centered, u, a

def load_comparison_cases():
    """Load case list from compare.txt with experiment_name -> publication_label mapping"""
    cases = []
    labels = []
    with open('compare.txt', 'r') as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith('#'):
                # Split on first whitespace: everything before = experiment_name, everything after = publication_label
                parts = line.split(None, 1)  # Split on any whitespace, max 1 split
                cases.append(parts[0])
                labels.append(parts[1])
    return cases, labels

if __name__=='__main__':
    
    # Load cases and labels from configuration file
    cases, labels = load_comparison_cases()
    
    plt.rcParams.update({'font.size': 17})  # Base font size
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, figsize=(8, 8), sharex=True)
    
    for case, label in zip(cases, labels):
        t, u, a = load_case(case)
        if t is not None:
            # Calculate displacement by integrating velocity
            dt = t[1] - t[0] if len(t) > 1 else 1.0
            displacement = np.cumsum(u) * dt
            
            # Convert to nm/ns units for plotting
            # Use publication label for legend
            ax1.plot(t, displacement/1e-3, label=label)  # displacement in nm
            ax2.plot(t, u/1e-3, label=label)             # velocity in nm/ns
            ax3.plot(t, a/1e-3, label=label)             # acceleration in nm/ns²
    
    # Formatting - Displacement plot (top)
    ax1.set_ylabel('Displacement [nm]', fontsize=18)
    ax1.text(0.02, 0.95, '(a)', transform=ax1.transAxes, fontsize=20, fontweight='bold',
             verticalalignment='top')
    
    # Formatting - Velocity plot (middle)
    ax2.set_ylabel('Velocity [nm/ns]', fontsize=18)
    ax2.text(0.02, 0.95, '(b)', transform=ax2.transAxes, fontsize=20, fontweight='bold',
             verticalalignment='top')
    
    # Formatting - Acceleration plot (bottom)
    ax3.set_ylabel('Acceleration [nm/ns²]', fontsize=18)
    ax3.set_xlabel('Time - t$_{transit}$ [ns]', fontsize=18)
    # Legend placed below figure to avoid obscuring data
    handles, leg_labels = ax3.get_legend_handles_labels()
    fig.legend(handles, leg_labels, loc='lower center', ncol=3,
               frameon=True, fontsize=16, bbox_to_anchor=(0.5, -0.08))
    ax3.text(0.02, 0.95, '(c)', transform=ax3.transAxes, fontsize=20, fontweight='bold',
             verticalalignment='top')
    
    # Add vertical line at acoustic transit time
    ax1.axvline(x=0, color='black', linestyle='--', alpha=0.7)
    ax2.axvline(x=0, color='black', linestyle='--', alpha=0.7)
    ax3.axvline(x=0, color='black', linestyle='--', alpha=0.7)
    
    # Set plot limits: -11 to +11 ns for display, ticks every 5 ns
    ax1.set_xlim([-11, 11])
    ax2.set_xlim([-11, 11])
    ax3.set_xlim([-11, 11])
    ax3.set_xticks([-10, -5, 0, 5, 10])
    
    # Set tick label font sizes
    ax1.tick_params(axis='both', labelsize=15)
    ax2.tick_params(axis='both', labelsize=15)
    ax3.tick_params(axis='both', labelsize=15)
    
    plt.tight_layout()
    plt.savefig('comparison.png', dpi=300, bbox_inches='tight')
    plt.savefig('comparison.pdf', bbox_inches='tight')
