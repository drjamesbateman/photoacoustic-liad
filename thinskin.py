#!/usr/bin/env python3
"""
Analytical solution for photoacoustic wave propagation in the thin-skin limit.

Exponentials are algebraically combined before evaluation for numerical stability.
"""

import numpy as np
from scipy.special import erfc

u_nat = lambda *opt: ua_nat(*opt)[0]
a_nat = lambda *opt: ua_nat(*opt)[1]

def ua_nat(z_nat, t_nat, eta):
    """
    Compute velocity and acceleration in thin-skin limit (on-axis).

    Parameters:
    -----------
    z_nat : array_like
        Normalized distance z/d_evo
    t_nat : array_like
        Normalized time vt/d_evo
    eta : float
        Dimensionless parameter w/(v*tau) = d_evo/w

    Returns:
    --------
    u_nat : ndarray
        Normalized velocity u / (S0*xi*d_evo)
    a_nat : ndarray
        Normalized acceleration (du/dt) / (S0*xi*v)
    """

    # Precompute common terms
    eta2 = eta**2
    eta3 = eta**3
    eta4 = eta**4

    mu = 1 + 2*eta2                 # Eq. (A7)
    Delta = z_nat - t_nat           # Retarded coordinate

    z_nat2 = z_nat**2
    t_nat2 = t_nat**2

    # Common erfc argument and value
    erfc_arg = eta * (mu*Delta + t_nat) / np.sqrt(2*mu)
    erfc_val = erfc(erfc_arg)

    # === VELOCITY calculation ===
    # Combine exponentials for numerical stability
    exp_u_lead = -eta4 * (z_nat2 + t_nat2*(mu + 1)/mu)

    exp_u1_combined = exp_u_lead + t_nat*eta4*(t_nat + 2*mu*z_nat)/mu
    u_term1 = 2 * np.sqrt(mu) * np.exp(exp_u1_combined)

    exp_u2_combined = exp_u_lead + mu*eta2*z_nat2/2 + eta4*t_nat2
    u_term2 = -np.sqrt(2*np.pi) * t_nat * eta * np.exp(exp_u2_combined) * erfc_val

    u_coeff = 1 / (2 * mu**(3/2))  # Corrected prefactor (positive for expansion)
    u_result = u_coeff * (u_term1 + u_term2)

    # === ACCELERATION calculation ===
    exp_a_lead = 2*eta4*t_nat*Delta - eta2*(2*mu - 1)*z_nat2/2

    exp_a1_combined = exp_a_lead + eta4*t_nat2 + mu*eta2*z_nat2/2
    a_term1 = 4 * mu * eta3 * (mu*Delta - t_nat) * np.exp(exp_a1_combined)

    exp_a2_combined = exp_a_lead + mu*eta2*z_nat2/2 + eta4*t_nat2 \
                    + eta2*(mu*Delta + t_nat)**2 / (2*mu)
    a_term2 = np.sqrt(2*np.pi*mu) * (2*eta4*t_nat2 - mu) \
            * np.exp(exp_a2_combined) * erfc_val

    a_coeff = eta / (2 * mu**3)  # Corrected prefactor (consistent with velocity)
    a_result = a_coeff * (a_term1 + a_term2)

    return u_result, a_result
