#!/usr/bin/env python3
"""
Generate diffraction figure showing acoustic wave propagation using full numerical integration.
Compares different diffraction regimes (different eta values) at multiple time snapshots.

Uses exact numerical integration from photoacoustic module (no approximations).
"""

import numpy as np
import matplotlib.pyplot as plt
plt.rcParams.update({'font.size': 22})
from photoacoustic import u_array


def create_diffraction_figure(d_over_devo=1.0, plot_acceleration=True, normalize_per_panel=False, N=10**5):
    """
    Create 3×3 diffraction comparison figure using full numerical integration.

    Parameters:
    -----------
    d_over_devo : float
        Ratio of substrate thickness to evolution distance: d/d_evo
        Sets the z-axis range. For d/d_evo ~ 1, the Rayleigh range matches
        substrate thickness (minimal diffraction).
    plot_acceleration : bool
        If True, plot acceleration (better contrast). If False, plot velocity.
    normalize_per_panel : bool
        If True, normalize each panel independently for maximum contrast.
        If False, use global colorscale across all panels.
    """

    # Eta values to compare (columns)
    # Geometrically spaced to match experimental systems: Nikkhou (0.6), intermediate (1.4), Bykov (3.1)
    eta_values = [0.6, 1.4, 3.1]

    # Time snapshots (rows) - in units of d_evo/v
    # Times chosen to show wave propagating through substrate of thickness d
    # For d/d_evo = 1.0: t_nat ~ z_nat, so these show wave at different depths
    # Listed bottom-to-top (row 2 -> row 1 -> row 0), so bottom row has earliest time
    t_nat_values = [1.8, 1.2, 0.6]  # Late, middle, early (top to bottom)

    field_type = "acceleration" if plot_acceleration else "velocity"
    print(f"Full numerical integration diffraction comparison (3×3 grid)")
    print(f"Plotting: {field_type}")
    print(f"d/d_evo = {d_over_devo:.2f} (substrate thickness / evolution distance)")
    print(f"Eta values: {eta_values}")
    print(f"Time snapshots (vt/d_evo), top to bottom: {t_nat_values}")
    print(f"  (Wave approximately at z/d_evo = {[f'{t:.1f}' for t in t_nat_values]})")

    # Reference parameters (in µm, ns units)
    # Choose d_evo = 100 µm as reference length scale
    d_evo_ref = 100.0  # µm
    v_ref = 6.0  # µm/ns (typical speed of sound in metals)
    xi_ref = 0.01  # µm (10 nm skin depth)
    S0_ref = 1.0  # Arbitrary units (will normalize later)

    # Spatial grid in natural units
    z_max_nat = d_over_devo
    r_max_nat = 2.5  # Radial extent in units of d_evo (enough to see diffraction)

    # Convert to physical units
    z_max = z_max_nat * d_evo_ref
    r_max = r_max_nat * d_evo_ref

    nr = 100
    nz = 100
    raxis_phys = np.linspace(0, r_max, nr)
    zaxis_phys = np.linspace(0, z_max, nz)

    print(f"\nPhysical domain: r ∈ [0, {r_max:.1f}] µm, z ∈ [0, {z_max:.1f}] µm")
    print(f"Grid: {nr}×{nz} points")
    print(f"Reference d_evo = {d_evo_ref:.1f} µm, v = {v_ref:.2f} µm/ns")

    # Create figure (3 rows × 3 columns) with tight spacing
    fig, axes = plt.subplots(3, 3, figsize=(12, 12),
                             gridspec_kw={'wspace': 0.02, 'hspace': 0.1})

    # Storage for all data to determine global colorscale
    all_data = []

    # Compute all fields
    for row, t_nat in enumerate(t_nat_values):
        print(f"\nRow {row+1}, vt/d_evo = {t_nat:.2f}:")

        for col, eta in enumerate(eta_values):
            print(f"  η = {eta:.1f}: computing...", end='', flush=True)

            # For given eta and d_evo, compute w and tau
            # d_evo = w²/(v*tau)
            # eta = w/(v*tau)
            # Solving: w = d_evo/eta, tau = d_evo/(v*eta²)
            w_phys = d_evo_ref / eta
            tau_phys = d_evo_ref / (v_ref * eta**2)

            # Time in physical units
            t_phys = t_nat * d_evo_ref / v_ref

            if plot_acceleration:
                # Compute velocity at 3 times for acceleration via np.gradient
                dt_phys = 0.1  # ns
                taxis_3 = [t_phys - dt_phys, t_phys, t_phys + dt_phys]
                print(f" w={w_phys:.2f} µm, tau={tau_phys:.3f} ns, t={t_phys:.2f}±{dt_phys} ns...", end='', flush=True)

                data_4d_3t = u_array(raxis_phys, [0], zaxis_phys, taxis_3,
                                     w_phys, xi_ref, tau_phys, v_ref, S0_ref, N)
                # data_4d_3t shape: (nr, 1, nz, 3)
                u_3t = data_4d_3t[:, 0, :, :]  # Shape: (nr, nz, 3)

                # Use np.gradient along time axis (axis=2)
                a_3t = np.gradient(u_3t, dt_phys, axis=2)
                snapshot = a_3t[:, :, 1]  # Take middle time slice
                print(" done")
            else:
                # Compute velocity at single time
                print(f" w={w_phys:.2f} µm, tau={tau_phys:.3f} ns, t={t_phys:.2f} ns...", end='', flush=True)
                data_4d = u_array(raxis_phys, [0], zaxis_phys, [t_phys],
                                  w_phys, xi_ref, tau_phys, v_ref, S0_ref, N)
                snapshot = data_4d[:, 0, :, 0]
                print(" done")

            all_data.append(snapshot)

    # Compute colorscale
    if normalize_per_panel:
        print(f"\nUsing per-panel normalization")
        vmaxes = [np.abs(data).max() for data in all_data]
    else:
        vmax_global = np.abs(np.array(all_data)).max()
        print(f"\nGlobal vmax = {vmax_global:.3e}")
        vmaxes = [vmax_global] * len(all_data)

    # Plot grid
    idx = 0
    for row, t_nat in enumerate(t_nat_values):
        for col, eta in enumerate(eta_values):
            ax = axes[row, col]

            snapshot = all_data[idx]
            vmax = vmaxes[idx]
            idx += 1

            # Create mesh plot
            # Note: raxis_phys and zaxis_phys are in µm, convert to natural units for display
            raxis_nat = raxis_phys / d_evo_ref
            zaxis_nat = zaxis_phys / d_evo_ref

            im = ax.pcolormesh(raxis_nat, zaxis_nat, snapshot.T,
                             cmap='RdBu_r', vmin=-vmax, vmax=vmax,
                             shading='auto', rasterized=True)

            # Add substrate thickness markers for experimental systems
            if col == 0:  # Nikkhou: d = 17 μm, d_evo = 11 μm → d/d_evo = 1.55
                ax.axhline(y=1.55, color='black', linestyle='--', linewidth=1.2, alpha=0.7)
            elif col == 2:  # Bykov: d = 100 μm, d_evo = 330 μm → d/d_evo = 0.30
                ax.axhline(y=0.30, color='black', linestyle='--', linewidth=1.2, alpha=0.7)

            # Labels and titles
            if col == 0:
                ax.set_ylabel(r'$z/d_{\mathrm{evo}}$', fontsize=18)
            else:
                ax.set_yticklabels([])

            if row == 2:  # Bottom row
                ax.set_xlabel(r'$r/d_{\mathrm{evo}}$', fontsize=18)
            else:
                ax.set_xticklabels([])

            if row == 0:  # Top row
                ax.set_title(f'η = {eta:.1f}', fontsize=18, pad=8)

            if col == 0:  # Left column - time label
                ax.text(-0.35, 0.5, f'$vt/d_{{\\mathrm{{evo}}}}$ = {t_nat:.1f}',
                       transform=ax.transAxes,
                       ha='center', va='center', rotation=90, fontsize=18)

            ax.set_aspect('equal')

            # Thin black frame around each subplot
            for spine in ax.spines.values():
                spine.set_edgecolor('black')
                spine.set_linewidth(0.5)

    # Add colorbar
    fig.subplots_adjust(right=0.90, left=0.08)
    cbar_ax = fig.add_axes([0.92, 0.15, 0.015, 0.7])
    cbar = fig.colorbar(im, cax=cbar_ax)
    if plot_acceleration:
        # Natural acceleration scale: a_scale = S₀ξv
        cbar_label = r'$a/(S_0 \xi v)$' if not normalize_per_panel else r'$a/a_{\mathrm{max}}$'
    else:
        # Natural velocity scale: u_scale = S₀ξd_evo (or similar)
        cbar_label = r'$u$ [nat. units]' if not normalize_per_panel else r'$u/u_{\mathrm{max}}$'
    cbar.set_label(cbar_label, fontsize=18)

    # Save figure
    plt.savefig('diffraction.pdf', bbox_inches='tight', dpi=150)
    plt.savefig('diffraction.png', bbox_inches='tight', dpi=150)
    print(f"\nFigure saved to diffraction.pdf and diffraction.png")

    return fig


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description='Generate diffraction figure showing acoustic wave propagation.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python diffraction.py                            # Default: d/d_evo=1.0, acceleration, N=10^5
  python diffraction.py 3.0                        # Set d/d_evo=3.0
  python diffraction.py --velocity                 # Plot velocity instead of acceleration
  python diffraction.py --per-panel                # Per-panel normalization
  python diffraction.py -N 10000                   # Set number of samples
  python diffraction.py 2.5 --velocity -N 1000000  # Combined options
        """)

    parser.add_argument('d_over_devo', type=float, nargs='?', default=1.0,
                        help='Ratio of substrate thickness to evolution distance (default: 1.0)')
    parser.add_argument('--velocity', action='store_true',
                        help='Plot velocity instead of acceleration')
    parser.add_argument('--per-panel', action='store_true',
                        help='Use per-panel normalization instead of global colorscale')
    parser.add_argument('-N', '--samples', type=int, default=10**5,
                        help='Number of Monte Carlo samples (default: 10^5)')

    args = parser.parse_args()

    create_diffraction_figure(d_over_devo=args.d_over_devo,
                             plot_acceleration=not args.velocity,
                             normalize_per_panel=args.per_panel,
                             N=args.samples)
    # plt.show()  # Commented out - files are saved, no need for interactive display
