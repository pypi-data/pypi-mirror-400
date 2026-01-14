import sys
import numpy as np
from matplotlib import pyplot as plt 
import os
from pathlib import Path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)
from superrad.ultralight_boson import UltralightBoson
from superrad.orbit_dynamics import OrbitDynamics

def plot_remnant_example():
    """Plot superradiant instability and GW timescale for example remnant"""
    models = ["relativistic", "non-relativistic"]
    mrk = ["-", ":"]
    Mbh0 = 80.0 #solar mass
    abh0 = 0.81
    mu_range = 10.0**np.linspace(-13.5,-12.0,256) # eV
    for n,model in enumerate(models):
        bc = UltralightBoson(spin=1, model=model) 
        tauI = np.zeros_like(mu_range) 
        tauGW = np.zeros_like(mu_range) 
        Mbhf = np.zeros_like(mu_range) 
        abhf = np.zeros_like(mu_range) 
        ms = np.zeros_like(mu_range) 
        fgw = np.zeros_like(mu_range) 
        for i,mu in enumerate(mu_range):
            try:
                wf = bc.make_waveform(Mbh0, abh0, mu, units="physical")
            except ValueError:
                break 
            tauI[i] = wf.efold_time()
            tauGW[i] = wf.gw_time()
            Mbhf[i] = wf.mass_bh_final()
            abhf[i] = wf.spin_bh_final()
            ms[i] = wf.azimuthal_num()
            fgw[i] = wf.freq_gw(0)
        plt.loglog(fgw[ms==1], (tauI)[ms==1]/(60.0)**2, "r"+mrk[n], label=model)
        plt.loglog(fgw[ms==1], (tauGW)[ms==1]/(60.0)**2, "k"+mrk[n])
        plt.loglog(fgw[ms==2], (tauI)[ms==2]/(60.0)**2, "g"+mrk[n])
        plt.loglog(fgw[ms==2], (tauGW)[ms==2]/(60.0)**2, "b"+mrk[n])
    plt.legend(loc="best")
    plt.xlabel(r"$f_{GW}$ (Hz)")
    plt.ylabel(r"$\tau$ (hours)")
    plt.show() 

def plot_freq_shift_example():
    """Compute the relative frequency shift after boson cloud has lost half of its mass"""
    models = ["relativistic", "non-relativistic"]
    mrk = ["-", ":"]
    Mbh0 = 1.0
    abh0 = 0.99
    mu_range = np.linspace(0.05, 1.1, 1024)
    for n,model in enumerate(models):
        bc = UltralightBoson(spin=0, model=model) 
        deltaf_f = np.zeros_like(mu_range) 
        for i,mu in enumerate(mu_range):
            try:
                wf = bc.make_waveform(Mbh0, abh0, mu, units="natural")
            except ValueError:
                break 
            tauGW = wf.gw_time()
            f = wf.freq_gw(np.array([0,tauGW]))
            deltaf_f[i] = (f[1]-f[0])/f[0]
        plt.semilogy(mu_range, deltaf_f, "k"+mrk[n], label=model)
    plt.legend(loc="best")
    plt.ylabel(r"$\Delta f /f$")
    plt.xlabel(r"$\mu M$")
    plt.show() 

def remnant_properties_example():
    """Print out some properties of an example remnant and plot evolution of GW
    signal"""
    bc = UltralightBoson(spin=1, model="relativistic") 
    Mbh = 20.8 #solar mass 
    abh = 0.7
    mu = 1.16e-12 # eV
    print("Initial black hole of %1.1f solar mass and dimensionless spin %1.2f" % (Mbh,abh))
    print("Ultralight boson of mass %1.2e eV" % mu)
    wf = bc.make_waveform(Mbh, abh, mu, units="physical")
    print("Cloud grows in  %1.1f hours" % (wf.cloud_growth_time()/(60.0*60.0)))
    print("At saturation cloud mass is %e solar mass" % wf.mass_cloud(0))
    print("At saturation cloud GW frequency is %1.1f Hz" % wf.freq_gw(0))
    print("GW timescale is %1.1f hours" % (wf.gw_time()/(60.0*60.0)))
    sec_hour = 3600.0
    thetaObs = np.pi/4
    dObs = 100.0 # Mpc
    t = np.linspace(0,24*sec_hour, 256)
    fgw = wf.freq_gw(t)
    fdotgw = wf.freqdot_gw(t)
    hp,hx,delta = wf.strain_amp(t, thetaObs, dObs=dObs)
    phi = wf.phase_gw(t)
    phi_dot = (phi[1:]-phi[:-1])/(t[1:]-t[:-1])
    th = 0.5*(t[1:]+t[:-1]) 

    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    ax1.plot(t/sec_hour, hp, label=r"$h_+$")
    ax1.plot(t/sec_hour, hx, label=r"$h_x$")
    ax1.set_ylabel(r"$h$")
    ax1.legend(loc="best")
    ax2.plot(t/sec_hour, fgw, label=r"$f_{\rm GW}$")
    ax2.plot(th/sec_hour, phi_dot/(2.0*np.pi), ":", label=r"$\dot{\phi}/(2\pi)$")
    ax2.set_ylabel(r"$f_{\rm GW}$ (Hz)")
    ax2.legend(loc="best")
    ax3.plot(t/sec_hour, fdotgw)
    ax3.set_ylabel(r"$\dot{f}_{\rm GW}$ (Hz/s)")
    ax3.set_xlabel(r"$t$ (hours)")
    plt.show()

def gw_power_strain():
    """Check for consistency between GW power and strain"""
    models = ["relativistic", "non-relativistic"]
    mrk = ["-", ":"]
    Mbh0 = 1.0
    abh0 = 0.99
    mu_range = np.linspace(0.01, 1.1, 256)
    theta = np.linspace(0, np.pi, 256)
    for n,model in enumerate(models):
        bc = UltralightBoson(spin=1, model=model) 
        pgw = np.zeros_like(mu_range) 
        pgw_h = np.zeros_like(mu_range) 
        ms = np.zeros_like(mu_range) 
        for i,mu in enumerate(mu_range):
            try:
                wf = bc.make_waveform(Mbh0, abh0, mu, units="natural")
            except ValueError:
                break 
            pgw[i] = wf.power_gw(0)
            omegaGW = 2.0*np.pi*wf.freq_gw(1e20)*wf.mass_bh_final()
            hp,hx,delta = wf.strain_amp(0, theta)
            pgw_h[i] = omegaGW**2*np.trapz((hp**2+hx**2)*np.sin(theta),theta)*np.pi/(16.0*np.pi)
            ms[i] = wf.azimuthal_num()
        plt.semilogy(mu_range[ms==1], pgw[ms==1], "k"+mrk[n], label=model)
        plt.semilogy(mu_range[ms==1], pgw_h[ms==1], "r"+mrk[n], label=model+" from $h$")
        plt.semilogy(mu_range[ms==2], pgw[ms==2], "g"+mrk[n])
        plt.semilogy(mu_range[ms==2], pgw_h[ms==2], "b"+mrk[n])
    plt.ylabel(r"$P_{\rm GW}$")
    plt.xlabel(r"$\mu M$")
    plt.legend(loc="best")
    plt.show()
    
def gw_strain():
    """Compare GW strain"""
    models = ["relativistic", "non-relativistic"]
    mrk = ["-", ":"]
    Mbh0 = 1.0
    abh0 = 0.99
    mu_range = np.linspace(0.01, 1.1, 256)
    theta = 3*np.pi/4 
    for n,model in enumerate(models):
        bc = UltralightBoson(spin=0, model=model) 
        hp = np.zeros_like(mu_range) 
        hx = np.zeros_like(mu_range) 
        delta = np.zeros_like(mu_range) 
        ms = np.zeros_like(mu_range) 
        for i,mu in enumerate(mu_range):
            try:
                wf = bc.make_waveform(Mbh0, abh0, mu, units="natural")
            except ValueError:
                break 
            omegaGW = 2.0*np.pi*wf.freq_gw(0)
            hp[i],hx[i],delta[i] = wf.strain_amp(0, theta)
            ms[i] = wf.azimuthal_num()
        plt.semilogy(mu_range[ms==1], hp[ms==1], "k"+mrk[n], label=model+r" $h_+$")
        plt.semilogy(mu_range[ms==1], hx[ms==1], "r"+mrk[n], label=model+r" $h_x$")
        plt.semilogy(mu_range[ms==2], hp[ms==2], "g"+mrk[n])
        plt.semilogy(mu_range[ms==2], hx[ms==2], "b"+mrk[n])
    plt.ylabel(r"$h$")
    plt.xlabel(r"$\mu M$")
    plt.legend(loc="best")
    plt.show()

def comp_cloud_evo():
    """Compare a simple approximation for the cloud evolution that matches
    together the expotential growth phase of the cloud with the GW decay
    dominated phase (matched) to evolving cloud while accounting for both
    superradiant growth and GW decay (full).
    """
    bc = UltralightBoson(spin=1, model="relativistic") 
    Mbh = 20.8 #solar mass 
    abh = 0.7
    mu = 1.16e-12 # eV
    sec_hour = 3600.0
    thetaObs = np.pi/4
    dObs = 100.0 # Mpc
    t = np.linspace(-0.25*sec_hour,3*sec_hour, 2048)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    for evo_type in ["matched", "full"]:
        wf = bc.make_waveform(Mbh, abh, mu, units="physical", evo_type=evo_type)
        Mc = wf.mass_cloud(t)
        fgw = wf.freq_gw(t)
        fdotgw = wf.freqdot_gw(t)
        mrk = "-"
        if (evo_type=="full"): mrk = "--"
        ax1.plot(t/sec_hour, Mc, mrk, label=evo_type)
        ax2.plot(t/sec_hour, fgw, mrk, label=evo_type)
        ax3.semilogy(t/sec_hour, abs(fdotgw), mrk, label=evo_type)
    ax1.set_ylabel(r"$M_c\ (M_{\odot})$")
    ax1.legend(loc="best")
    ax2.set_ylabel(r"$f_{\rm GW}$ (Hz)")
    ax2.legend(loc="best")
    ax3.set_ylabel(r"$|\dot{f}_{\rm GW}|$ (Hz/s)")
    ax3.set_xlabel(r"$t$ (hours)")
    plt.show()

def plot_risco():
    """Compare ISCO radius from Kerr black hole and black hole with a boson cloud.
    Geometry provides tabulated data as well as an interpolation between those points,
    with all quantities in geometrical black hole mass units.
    """
    Mc = 0.01 #black hole mass units 
    abh = 0.7
    sca = OrbitDynamics(spin=0)
    sca_model = sca.model()
    vec = OrbitDynamics(spin=1)
    vec_model = vec.model()
    kerr = OrbitDynamics(Kerr=True)
    kerr_model = kerr.model(vec_model.Jbh_data())
    models = [vec_model,sca_model]
    mrk = ['-','--']
    labels = ['Vector cloud','Scalar cloud']
    alpha = np.linspace(0.2,0.4)
    fig, (ax1, ax2, ax3) = plt.subplots(3, 1, sharex=True)
    tabulated_alpha = vec_model.alpha_data()
    tabulated_Mc = vec_model.Mcloud_data()
    tabulated_Jbh = vec_model.Jbh_data()
    tabulated_Risco = vec_model.ISCO_radius_data()
    kerr_tabulated = kerr_model.ISCO_radius()
    err_Risco = np.zeros_like(tabulated_alpha)
    err_al = np.zeros_like(tabulated_alpha)
    for n,al in enumerate(tabulated_alpha):
        err_Risco[n] = vec_model.ISCO_radius_error(al,tabulated_Mc[n])
        err_al[n] = vec_model.alpha_error(al,tabulated_Mc[n])
    ax1.plot(tabulated_alpha,tabulated_Risco,'.',label='with Vector Cloud')
    ax1.plot(tabulated_alpha,kerr_tabulated,'y.',label='Kerr with central black hole parameters')
    ax2.semilogy(tabulated_alpha,np.abs(err_Risco)/tabulated_Risco,'.',label='Risco')
    ax2.semilogy(tabulated_alpha,np.abs(err_al)/tabulated_alpha,'r.',label='alpha')
    for m,model in enumerate(models):
        Risco = np.zeros_like(alpha)
        for n,al in enumerate(alpha):
            Risco[n] = model.ISCO_radius(al, Mc)
        ax3.plot(alpha, Risco, mrk[m], label=labels[m])
    Risco = np.zeros_like(alpha)
    ax1.set_title("Data")
    ax1.set_ylabel(r"$R_{ISCO}/M_{BH}$")
    ax1.set_xlim(0.2,0.4)
    ax1.set_ylim(2,3.8)
    ax1.legend(loc="best")
    ax2.set_ylabel(r"rel. error")
    ax2.legend(loc="best")
    ax3.set_ylabel(r"$R_{ISCO}/M_{BH}$")
    ax3.legend(loc="best")
    ax3.set_xlabel(r"$\alpha$")
    ax3.set_title("Interpolated $M_c = 0.01M_{BH}$")
    plt.show()

if __name__ == "__main__":
    remnant_properties_example()
    plot_remnant_example()
    plot_freq_shift_example()
    gw_power_strain()
    gw_strain()
    comp_cloud_evo()
    plot_risco()
