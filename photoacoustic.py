#!/usr/bin/env python3

import numpy as np
from scipy.linalg import norm
from scipy.integrate import nquad
from numpy import exp, inf, pi, sqrt
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor
from itertools import product

# ====================================================================================================================
# General functions
# ====================================================================================================================

def S(x,y,z,t,w,xi,tau,v,S0):
    """Source term S as described in README."""
    return -S0 * exp(-(x**2+y**2)/(2*w**2)) * exp(-abs(z)/xi) * (t/tau) * exp(-(t/tau)**2)

def u(x,y,z,t, w,xi,tau,v,S0, N=10**5):
    """Find u(x,y,z,t) by Monte Carlo integration over a domain
    extending 3x the Gaussian width and 3x the skin depth of the
    laser pulse. This finite region captures ~95% of the total.

    (This function operates only on single values for x,y,z,t.)
    """

    # Define domain, probability density p, and pick points X,Y,Z
    X0,Y0,Z0 = 3*w, 3*w, 3*xi
    p = 1/(2*2*2*X0*Y0*Z0)
    X = np.random.uniform(low=-X0,high=X0,size=N)
    Y = np.random.uniform(low=-Y0,high=Y0,size=N)
    Z = np.random.uniform(low=-Z0,high=Z0,size=N)

    # Compute samples of the integrand
    # scipy.linalg.norm does not support arrays so we compute with numpy tools
    D = np.array([x-X,y-Y,z-Z]).T
    M = sqrt((D**2).sum(axis=1))
    f = S(X,Y,Z,t-M/v,w,xi,tau,v,S0)/(4*pi*M)

    # Compute the Monte Carlo estimate and associated uncertainty
    vals = f/p
    ans,err = np.mean(vals), np.std(vals)/sqrt(N)
    return ans,err

# ====================================================================================================================
# Parallel processing helper for evaluation of u(x,y,z,t)
# ====================================================================================================================
def uargs(args):
    """Rephrasing of function u to accept args as a list,
    and return only the Monte Carlo estimate i.e. discard
    the uncertainty estimate."""
    return u(*args)[0]

def u_array(xaxis,yaxis,zaxis,taxis,w,xi,tau,v,S0,N=10**5):
    """Wrapper to parallel process function u over iterables
    (xaxis,yaxis,zaxis,taxis) and return 4D array"""

    args = [(x,y,z,t,w,xi,tau,v,S0,N) for x,y,z,t in product(xaxis,yaxis,zaxis,taxis)]    
    with ProcessPoolExecutor() as executor:
        data = list(executor.map(uargs, args))
    data = np.array(data).reshape(len(xaxis),len(yaxis),len(zaxis),len(taxis))

    return data

# ====================================================================================================================

def make_frames(xaxis,zaxis,taxis,data,tag=''):
    """Helper function to make cross-section images;
    assumes data = u_array(xaxis,[0],zaxis,taxis,*args)"""
    
    MAX = abs(data).max()
    for n,t in enumerate(taxis):
        print(n,t)
        A = data[:,0,:,n]
        plt.figure(figsize=(4,4))
        plt.title(f"t = {t:.1f}")
        plt.pcolormesh(xaxis,zaxis,A.T)
        plt.tight_layout(pad=1.5)
        plt.xlabel('r [um]'); plt.ylabel('z [um]')
        plt.clim([-MAX,MAX]); plt.axis('equal')        
        plt.savefig(f"frames/img-{tag}-{n:05d}.png")
        plt.close()

# ====================================================================================================================
# Cylindrical symmetry
# ====================================================================================================================
def u_on_axis_integrand(z,t,rd,zd,w,xi,tau,v,S0):
    """Used exclusively by u_on_axis_integrator"""
    # Phrased as top-level function to allow use with ProcessPoolExecutor
    return S(rd,0,zd,t-norm([rd,0,zd-z])/v,w,xi,tau,v,S0)/(4*pi*norm([rd,0,zd-z]))

def u_on_axis_integrator(args):
    """Used exclusively by u_on_axis"""
    # Computes the integral
    # Phrased as top-level function to allow use with ProcessPoolExecutor
    # Uses domain 0 < r < 4w and -5 xi < z < 5 xi which captures 98% of total
    z,t,w,xi,tau,v,S0 = args
    return nquad(lambda rd, zd: 2*pi*rd*u_on_axis_integrand(z,t,rd,zd,w,xi,tau,v,S0),[(0,4*w),(-5*xi,5*xi)])

def u_on_axis(zaxis,taxis,w,xi,tau,v,S0,tag=''):
    """Compute u(x=0,y=0,z,t) i.e. on axis above a circularly symmetric laser spot.
    zaxis, taxis : iterables; often, will set zaxis to be a list containing a single scalar
    Returns : data, consisting of values [u(z,t) for z in zaxis] for t in taxis]"""

    args = [(z,t,w,xi,tau,v,S0) for z,t in product(zaxis,taxis)]
    with ProcessPoolExecutor() as executor:
        data = list(executor.map(u_on_axis_integrator,args))
    data = np.array(data).reshape(len(zaxis),len(taxis),2)

    return data

# ====================================================================================================================
def load_values(tag):
    """Load experimental details from YAML files.
    Returned values have units derived from um, ns."""

    import yaml
    with open("experiments.yaml") as h:
        expts = yaml.safe_load(h)        
    with open("materials.yaml") as h:
        materials = yaml.safe_load(h)
        
    beta  = float(expts[tag]['absorption'])
    U0    = float(expts[tag]['pulse_energy'])
    tau   = float(expts[tag]['pulse_duration'])
    w     = float(expts[tag]['waist'])
    xi = float(expts[tag]['skin_depth'])

    thickness = float(expts[tag]['thickness'])

    mat = expts[tag]['material']
    rho = float(materials[mat]['density'])
    Cp  = float(materials[mat]['heat_capacity'])
    alpha = float(materials[mat]['thermal_expansion'])
    v = float(materials[mat]['speed_of_sound'])

    # Compute derived values
    Z = rho * v
    H0 = beta*U0/(2 * pi**1.5 * w**2 * xi * tau)  # Corrected normalization
    S0 = (1/Z) * (alpha/Cp) * 2 * H0/tau

    # Convert all values used hereafter into um, ns units
    um = 1e-6; ns = 1e-9
    tau /= ns
    w /= um
    xi /= um
    v /= (um/ns)
    thickness /= um
    S0 /= (um/ns)/(um**2)

    return {'S0':S0, 'xi':xi, 'tau':tau, 'w':w, 'v':v, 'thickness':thickness}

if __name__=="__main__":

    from sys import argv
    tag = argv[1]
    
    vals = load_values(tag)
    thickness = vals.pop('thickness')
    
    # On-axis calculation - extend time domain to -50ns to +50ns for proper integration
    t_transit = thickness/vals['v']
    t0 = t_transit - 50.0  # ns
    t1 = t_transit + 50.0  # ns
    taxis = np.linspace(t0,t1,1001)  # Increase points for better resolution
    data = u_on_axis([thickness],taxis,**vals)
    uvals = data[0,:,0]
    avals = np.gradient(uvals,taxis)
    np.savetxt(f"photoacoustic-{tag}.csv", np.array([taxis,uvals,avals]).T)
    
    plt.figure(figsize=(8,4))
    plt.title(tag)
    plt.plot(taxis,uvals/1e-3,label='Speed [nm/ns]')
    plt.plot(taxis,avals/1e-3,label='Acceleration [nm/ns$^2$]')
    plt.ylim([-20,+20])
    plt.grid()
    plt.xlabel('Time [ns]')
    plt.legend()
    plt.tight_layout()
    plt.savefig(f"photoacoustic-{tag}.png")
    plt.savefig(f"photoacoustic-{tag}.pdf")
    print(f"Max acceleration : {abs(avals).max()/1e-3:.3f} nm/ns^2")
    
#    plt.show()
