#!/usr/bin/env python3
"""
Acoustic pulse evolution in the thin-skin limit using analytical solution.

Implements the analytical formula derived in Appendix A, showing how the
normalized waveform depends on the dimensionless parameter eta = w/(2*v*tau).
"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 28})
from thinskin import u_nat, a_nat

def create_eta_comparison_plot(plot_velocity=False):
    """Create multi-panel plot showing different eta values.

    Parameters:
    -----------
    plot_velocity : bool
        If True, plot velocity; if False, plot acceleration
    """

    z_max = 4.0
    t_max = 4.0
    nz = 200
    nt = 200

    z_norm = np.linspace(0, z_max, nz)
    t_norm = np.linspace(0, t_max, nt)
    Z, T = np.meshgrid(z_norm, t_norm)

    # Eta values to compare
    # Geometrically spaced to match experimental systems: Nikkhou (0.24), intermediate (0.8), Bykov (2.6)
    eta_values = [0.24, 0.8, 2.6]
    titles = ['(a) η = 0.24\n(tight focus)',
              '(b) η = 0.8\n(intermediate)',
              '(c) η = 2.6\n(large waist)']

    # Create figure with tight subplot spacing
    fig, axes = plt.subplots(1, 3, figsize=(15, 4.5),
                             gridspec_kw={'wspace': 0.15, 'hspace': 0.05})

    field_name = "velocity" if plot_velocity else "acceleration"
    print(f"Plotting {field_name}...")

    # Compute all fields to get global vmax
    all_fields = []
    for eta in eta_values:
        if plot_velocity:
            Field = u_nat(Z, T, eta)
        else:
            Field = a_nat(Z, T, eta)
        field_max = np.max(np.abs(Field))
        all_fields.append(Field / field_max)

    # Global color scale
    vmax = max([np.max(np.abs(f)) for f in all_fields])

    for i, (eta, title, Field_norm) in enumerate(zip(eta_values, titles, all_fields)):
        print(f"Computing η = {eta}...")

        if plot_velocity:
            ylabel = r'$u/u_{\mathrm{max}}$'
        else:
            ylabel = r'$a/a_{\mathrm{max}}$'

        print(f"  Max |{field_name[0]}|: {np.max(np.abs(Field_norm)):.3e}")

        # Plot
        ax = axes[i]

        im = ax.imshow(Field_norm,
                      extent=[0, z_max, 0, t_max],
                      origin='lower',
                      aspect='auto',
                      cmap='RdBu_r',
                      vmin=-vmax,
                      vmax=vmax)

        ax.set_xlabel(r'$z/d_{\mathrm{evo}}$', fontsize=24)
        if i == 0:
            ax.set_ylabel(r'$vt/d_{\mathrm{evo}}$', fontsize=24)
        else:
            ax.set_yticklabels([])

        ax.set_title(title, fontsize=24)

        # Add substrate thickness markers for experimental systems
        if i == 0:  # Nikkhou: d = 400 μm, d_evo = 1.0 μm → d/d_evo ~ 390 (beyond plot range)
            pass
        elif i == 2:  # Bykov: d = 250 μm, d_evo = 130 μm → d/d_evo ~ 1.9
            ax.axvline(x=1.9, color='black', linestyle='--', linewidth=1.2, alpha=0.7)

        # Add wavefront line
        ax.plot([0, min(z_max, t_max)], [0, min(z_max, t_max)],
               color='gray', linestyle='--', linewidth=1, alpha=0.6)

        # Thin black frame
        for spine in ax.spines.values():
            spine.set_edgecolor('black')
            spine.set_linewidth(0.5)

    # Single colorbar for all panels
    fig.subplots_adjust(right=0.92)
    cbar_ax = fig.add_axes([0.93, 0.15, 0.015, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    cbar.set_label(ylabel, fontsize=24)

    # Save
    plt.savefig('spacetime.png', dpi=300, bbox_inches='tight')
    plt.savefig('spacetime.pdf', dpi=300, bbox_inches='tight')

    return fig, axes

if __name__ == "__main__":
    import sys

    print("Acoustic pulse evolution in thin-skin limit")
    print("Analytical solution with η-dependence")
    print("=" * 50)

    # Check for command-line argument
    plot_velocity = '--velocity' in sys.argv

    fig, axes = create_eta_comparison_plot(plot_velocity=plot_velocity)
    #plt.show()
