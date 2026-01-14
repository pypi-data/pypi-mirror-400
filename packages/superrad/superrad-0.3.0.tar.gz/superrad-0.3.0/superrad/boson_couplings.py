import numpy as np
from .cloud_model import CloudModel 
from .units import set_units, electron_mass
import warnings
from abc import ABCMeta, abstractmethod

class CoupledBosonModel(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, cloud_model, units="natural", undefined_max_coupling=0):
        """
        Abstract class for calculating critical couplings in models where boson
        has additional (non-gravitational) interactions with itself or other fields. 

        If units="physical" use the following units for input/output:

        mu : electronvolts
        Mass : solar mass

        If units="natural" assume G=c=hbar=1

        If "+alpha" is appended to either "physical" or "natural," then units
        are the same as above, except the input mu is taken to be in units of 
        (hbar c^3)/(G*Mbh0), i.e.  mu is set to the dimensionless 
        "fine structure constant" alpha. 
        """
        pass
    @abstractmethod
    def max_coupling(self, mu, Mbh, abh):
        """Max coupling allowed such that black hole spins down through superradiance"""
        pass


def _get_superradiance_final_state(mu, Mbh0, abh0, cloud_model):
    #Check if superradiant condition is met for m<mmax
    mmax = cloud_model.max_azi_num()
    rp0 = (Mbh0+np.sqrt(Mbh0**2-(abh0*Mbh0)**2))
    OmegaBH0 = 0.5*abh0/rp0
    Mir0 = 0.5*rp0
    m = 1
    omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0
    while (not(np.isfinite(omega0)) or not(omega0<m*OmegaBH0)):
        m = m+1
        if (m>mmax): 
            return (0,0,0)
        else: omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0

    if (m<mmax):
        if (cloud_model.omega_imag(m, mu*Mbh0, abh0)
            <cloud_model.omega_imag(m+1, mu*Mbh0, abh0)):
                m = m+1

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
    Mcloud = Mbh0-Mbhf
    tauI = Mbh0/(2*cloud_model.omega_imag(m, mu*Mbh0, abh0)) 
    return (m, Mcloud, tauI)

class KineticMixedDarkPhoton(CoupledBosonModel):
    def __init__(self, cloud_model, units="physical", undefined_max_coupling=0):
        """
        Kinetically mixed dark photon model.
        Dark photon has coupling with standard model photon of the form:
    
        eps* F'^{ab}F_{ab} 

        Calculates max epsilon where electromagnetic dissipation due to
        resulting pair plasma is subdominant to superradiance, and black hole fully
        spins down.
        """
        if not isinstance(cloud_model, CloudModel):
            raise TypeError
        if (cloud_model.boson_spin()!=1):
            raise TypeError("Only defined for spin 1 cloud models.")
        self._cm = cloud_model
        self._units = units
        self._undefined_max_coupling = undefined_max_coupling
    def max_coupling(self, mu, Mbh, abh):
        """
        Returns maximum value of epsilon (dimensionless constant) where superradiance dominates spindown 
        See Appendix C of arXiv:2507.20979
        """
        if (mu<0 or Mbh<0 or abh<=0 or abh>self._cm.max_spin()):
            raise ValueError("Invalid max_coupling parameters: mu,Mbh0,abh0<=0, or abh>max. spin the cloud_model is valid for.")
        #Set units
        (self._tunit, self._Punit, self._dunit, self._hbar, mu_fac) = set_units(self._units, Mbh)
        me = electron_mass(self._units)

        mu = mu_fac*mu
        alpha = mu*Mbh

        m, Mc, tauI = _get_superradiance_final_state(mu, Mbh, abh, self._cm)
        Cm = np.asarray([1, np.exp(-2)/16, 4*np.exp(-4)/81, 81*np.exp(-6)/1024, 1024*np.exp(-8)/5625])/np.pi
        if (Mc<=0 or m<1 or m>len(Cm)): return self._undefined_max_coupling 

        # Pair plasma production criterion
        eps_pm = (1.0/0.30282212)*electron_mass("natural")*(2.0*me/mu)**0.5*(Mbh/Mc/Cm[m-1])**0.5/alpha**2

        # Select critical eps
        if (m==1): 
            # See eq. 55 in arXiv:2212.09772
            Falpha = 0.131*alpha-0.188*alpha**2
            # SR rate larger than EM dissipation rate
            eps_diss = (Mbh/tauI/Falpha)**0.5
            eps_crit = max(0.1*eps_pm,eps_diss)
        else: 
            eps_crit = 0.1*eps_pm

        return eps_crit

class HiggsAbelian(CoupledBosonModel):
    def __init__(self, cloud_model, units="physical", undefined_max_coupling=0):
        """
        Model where vector gets a mass through Higgs mechanism for complex scalar field 

        mu = g*v where v is VEV of Higgs-like scalar
        Mass of the radial mode is (2*lambda)**0.5*v
    
        """
        if not isinstance(cloud_model, CloudModel):
            raise TypeError
        if (cloud_model.boson_spin()!=1):
            raise TypeError("Only defined for spin 1 cloud models.")
        self._cm = cloud_model
        self._units = units
        self._undefined_max_coupling = undefined_max_coupling
    def max_coupling(self, mu, Mbh, abh):
        """
        Returns maximum value of g/[sqrt(lambda)*(v/Mpl)] (dimensionless constant) where superradiance dominates spindown 
        See Appendix C of arXiv:2507.20979
        """
        if (mu<0 or Mbh<0 or abh<=0 or abh>self._cm.max_spin()):
            raise ValueError("Invalid max_coupling parameters: mu,Mbh0,abh0<=0, or abh>max. spin the cloud_model is valid for.")
        #Set units
        (self._tunit, self._Punit, self._dunit, self._hbar, mu_fac) = set_units(self._units, Mbh)

        mu = mu_fac*mu
        alpha = mu*Mbh

        m, Mc, tauI = _get_superradiance_final_state(mu, Mbh, abh, self._cm)

        #Currently only defined for m=1
        if (Mc<=0 or m!=1): return self._undefined_max_coupling

        if (alpha>0.1):
            Asq = 1e2*alpha**4*(Mc/Mbh)/np.pi
        else:
            Asq = (10)**0.5*np.sqrt(3e-9/4/alpha/abh)*(Mc/Mbh)
        return (1.0/Asq**0.5)


class ScalarQuarticInteraction(CoupledBosonModel):
    def __init__(self, cloud_model, tage, units="physical", undefined_max_coupling=0):
        """
        Model where the scalar has leading self-interactions of the form lambda*phi^4

        lambda ~ mu^2/f_a^2, where mu is the scalar mass and f_a the decay
        constant with conventions as in arxiv:2011.11646
        """
        if not isinstance(cloud_model, CloudModel):
            raise TypeError
        if (cloud_model.boson_spin()!=0):
            raise TypeError("Only defined for spin 0 cloud models.")
        self._cm = cloud_model
        self._units = units
        self._tage = tage
        self._undefined_max_coupling = undefined_max_coupling
    def max_coupling(self, mu, Mbh, abh):
        """
        Returns maximal inverse of the decay constant in units of Planck mass
        (M_pl/f) above which spindown is stopped for a black hole of age tage
        """
        if (mu<0 or Mbh<0 or abh<=0 or abh>self._cm.max_spin()):
            raise ValueError("Invalid max_coupling parameters: mu,Mbh0,abh0<=0, or abh>max. spin the cloud_model is valid for.")
        #Set units
        (self._tunit, self._Punit, self._dunit, self._hbar, mu_fac) = set_units(self._units, Mbh)

        mu = mu_fac*mu
        alpha = mu*Mbh
        tage = self._tage/self._tunit

        m, Mc, tauI = _get_superradiance_final_state(mu, Mbh, abh, self._cm)

        #Currently only defined for m=1
        alpha_valid = 0.2
        if (Mc<=0 or m!=1 or alpha>alpha_valid): return self._undefined_max_coupling 

        rp = 1+np.sqrt(1-abh**2)

        # solve eq. 60 in 2011.11646 for f_a and set tau_sd = tage
        fa_inv = (281.64/alpha**7/rp*(tage*mu)/(tauI*mu)**1.5)**0.5 

        return fa_inv

