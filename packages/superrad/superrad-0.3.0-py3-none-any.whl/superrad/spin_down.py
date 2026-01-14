import numpy as np
from .cloud_model import CloudModel 
from .units import set_units
import warnings

def spindown(mu, Mbh0, abh0, tage, cloud_model, units="natural"):
    """
    Calculate black mass and spin after specified time using the specified CloudModel
    for the specified parameters:
    mu : ultralight boson mass
    Mbh0 : initial black hole mass (before cloud growth)
    abh0 : initial black hole dimensionless (before cloud growth)
    tage : time black hole is subject to potential instability
    
    See units.py for input/output units.
    """
    if not isinstance(cloud_model, CloudModel):
        raise TypeError
    if (mu<0 or Mbh0<0 or abh0<=0 or abh0>cloud_model.max_spin()):
        raise ValueError("Invalid boson cloud waveform parameters: mu,Mbh0,abh0<=0, or abh0>max. spin the cloud_model is valid for.")

    #Set units
    (tunit, Punit, dunit, hbar, mu_fac) = set_units(units, Mbh0)
    mu = mu_fac*mu

    #Check if superradiant condition is met for m<mmax
    mmax = cloud_model.max_azi_num()
    rp0 = (Mbh0+np.sqrt(Mbh0**2-(abh0*Mbh0)**2))
    OmegaBH0 = 0.5*abh0/rp0
    Mir0 = 0.5*rp0
    m = 1
    omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0
    while (not(np.isfinite(omega0)) or not(omega0<m*OmegaBH0)):
        m = m+1
        if (m>mmax): break
        else: omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0
    if (m<mmax):
        if (cloud_model.omega_imag(m, mu*Mbh0, abh0)
            <cloud_model.omega_imag(m+1, mu*Mbh0, abh0)):
                m = m+1
    t=0
    while (t<tage and m<=mmax):
        #Find cloud frequency/mass at saturation
        Jbh0 = abh0*Mbh0**2
        omegaR = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0 
        omegaRprevious = 0.0
        rel_omega_tol = 1.0e-10
        max_iter = 100
        i=0
        while (abs(omegaRprevious-omegaR)>rel_omega_tol*mu and i<max_iter):
            omegaRprevious = 1.0*omegaR
            Mbhf = (m**3-np.sqrt(m**6-16.0*m**2*omegaR**2*(m*Mbh0-omegaR*Jbh0)**2))/(8.0*omegaR**2*(m*Mbh0-omegaR*Jbh0))
            if (Mbhf>=Mbh0): Mbhf = Mbh0-abs(Mbh0-Mbhf)
            Jbhf = Jbh0 -m/omegaR*(Mbh0-Mbhf)
            omegaR = cloud_model.omega_real(m, mu*Mbhf, Jbhf/Mbhf**2, (Mbh0-Mbhf)/Mbhf)/Mbhf
            i = i+1
        if (i>=max_iter):
            warnings.warn(("Saturation condition only satisfied up to relative difference of %e" 
                                 % (abs(omegaRprevious-omegaR)/mu)), RuntimeWarning)
        Mcloud0 = Mbh0-Mbhf
        tauI = Mbh0/(2*cloud_model.omega_imag(m, mu*Mbh0, abh0)) 
        tc = tunit*tauI*np.log(Mcloud0/(mu*hbar)) 
        if (tc<tage-t):
            t = t + tc
            Mbh0=Mbhf
            abh0=Jbhf/Mbhf**2
        else:
            Mcloud0 = Mcloud0*np.exp((tage-t-tc)/(tauI*tunit))
            Mbh0 = Mbh0-Mcloud0
            Jbh0 = Jbh0 -m/omegaR*(Mcloud0)
            abh0=Jbh0/Mbh0**2
            break
        m = m+1
    return (Mbh0,abh0) 

def max_spin(mu, tage, cloud_model, Mbh_lower, Mbh_upper, Nmbh, units="natural", Nspin=128, eps_spin=1.0e-3):
    """
    Calculate the maximum dimensionless spin of black holes subject to an 
    ultralight boson over some range of boson mass masses and black hole masses 

    for the specified parameters:
    mu : array of ultralight boson masses
    tage : time black hole is subject to potential instability
    Mbh_lower: lower bound of black hole mass to consider
    Mbh_upper: upper bound of black hole mass to consider
    Nmbh: Number of black hole masses to compute in the above range 
    Nspin: Number of points in dimensionless spin to consider, i.e. max_spin will be computed to ~1/Nspin
    eps_spin: computes spin values in the range [eps_spin, a_max*(1-eps_spin)]

    Note that Nmbh determines the resolution in black hole mass

    Returns max_spin as a 2D array of size len(mu)*Nbh

    """
    if not isinstance(cloud_model, CloudModel):
        raise TypeError
    if (tage<=0 or Mbh_lower<0 or Mbh_upper<=Mbh_lower or Nmbh<2):
        raise ValueError("Invalid max_spin parameters.")
    Mbh = np.linspace(Mbh_lower, Mbh_upper, Nmbh)
    dM = Mbh[1]-Mbh[0]
    Nin = int(np.ceil((Mbh_upper*2.0**0.5-Mbh_lower)/(0.5*dM))+1)
    Mbh_in = np.linspace(Mbh_lower, Mbh_lower+0.5*dM*(Nin-1), Nin)
    a_in = np.linspace(eps_spin, cloud_model.max_spin()*(1-eps_spin), Nspin)
    mus, Mbhs, abhs = np.meshgrid(mu, Mbh_in, a_in, indexing='ij')
    
    sd_vec = np.vectorize(spindown, excluded=[3,4,"units"])
    Mbhf,abhf = sd_vec(mus, Mbhs, abhs, tage, cloud_model, units=units)
    Mbhf = Mbhf.reshape(mu.size, Mbh_in.size*a_in.size)
    abhf = abhf.reshape(mu.size, Mbh_in.size*a_in.size)
    
    Mbin = np.zeros(len(Mbh)+1) 
    Mbin[1:-1] = 0.5*(Mbh[1:]+Mbh[:-1])
    Mbin[0] = max(Mbin[1]-dM,0.5*Mbin[1])
    Mbin[-1] = Mbin[-2]+dM
    inds = np.digitize(Mbhf, Mbin)
    
    a_max = np.ones([len(mu),len(Mbh)])
    for n in range(len(mu)):  
        mask = inds[n, :, None] == np.arange(1,len(Mbin))  
        a_max[n] = np.max(np.where(mask, abhf[n][:, None], -np.inf), axis=0)

    return a_max
