from photoacoustic import *
from thinskin import ua_nat

if __name__=='__main__':

    from sys import argv
    tag = argv[1]
    
    vals = load_values(tag)
    thickness = vals.pop('thickness')
    
    # On-axis calculation
    t0 = thickness/vals['v']-4*vals['tau']
    t1 = thickness/vals['v']+4*vals['tau']
    taxis = np.linspace(t0,t1,501)
    
    plt.figure()
    plt.title(tag)
    
    data = u_on_axis([thickness],taxis,**vals)
    uvals = data[0,:,0]
    avals = np.gradient(uvals,taxis)

    plt.plot(taxis,uvals,label='Speed [um/ns]')
    plt.plot(taxis,avals,label='Acceleration [um/ns$^2$]')
    
    data = u_array([0],[0],[thickness],taxis,**vals)
    uvals = data[0,0,0,:]
    avals = np.gradient(uvals,taxis)

    plt.plot(taxis,uvals,label='Speed [um/ns] [Monte Carlo]')
    plt.plot(taxis,avals,label='Acceleration [um/ns$^2$]  [Monte Carlo]')

    # Thin-skin analytical
    d_evo = vals['w']**2 / (vals['v'] * vals['tau'])
    eta = vals['w'] / (vals['v'] * vals['tau'])
    z_nat = thickness / d_evo
    t_nat = taxis * vals['v'] / d_evo
    u_nat, a_nat = ua_nat(z_nat, t_nat, eta)
    uvals_ts = u_nat * (vals['S0'] * vals['xi'] * d_evo)
    avals_ts = a_nat * (vals['S0'] * vals['xi'] * vals['v'])

    plt.plot(taxis, uvals_ts, '--', label='Speed [um/ns] [Thin-skin]')
    plt.plot(taxis, avals_ts, '--', label='Acceleration [um/ns$^2$] [Thin-skin]')

    plt.grid()
    plt.xlabel('Time [ns]')
    plt.legend()
    plt.savefig(f"photoacoustic-{tag}-verify.png")
    plt.savefig(f"photoacoustic-{tag}-verify.pdf")
    print(f"Max acceleration : {abs(avals).max():.3f} um/ns^2")

    plt.show()
