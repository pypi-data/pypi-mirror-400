import numpy as np
from .boson_waveform import BosonCloudWaveform
from .cloud_model import CloudModel 
from .harmonics import sYlm 
from .units import set_units
import warnings

class MatchedWaveform(BosonCloudWaveform):
    def __init__(self, mu, Mbh0, abh0, cloud_model, units="natural"):
        """
        Calculate some derived quantites using the specified CloudModel
        for the specified parameters:
        mu : ultralight boson mass
        Mbh0 : initial black hole mass (before cloud growth)
        abh0 : initial black hole dimensionless (before cloud growth)
        
        Internally G=c=1 and mu has dimensions of 1/mass
        
        See units.py for input/output units.

        If "+alpha" is appended to either "physical" or "natural," then units
        are the same as above, except the input mu is taken to be in units of 
        (hbar c^3)/(G*Mbh0), i.e.  mu is set to the dimensionless 
        "fine structure constant" alpha. 
        """
        if not isinstance(cloud_model, CloudModel):
            raise TypeError
        if (mu<0 or Mbh0<0 or abh0<=0 or abh0>cloud_model.max_spin()):
            raise ValueError("Invalid boson cloud waveform parameters: mu,Mbh0,abh0<=0, or abh0>max. spin the cloud_model is valid for.")

        #Set units
        (self._tunit, self._Punit, self._dunit, self._hbar, mu_fac) = set_units(units, Mbh0)
        mu = mu_fac*mu

        #Check if superradiant condition is met for m<mmax
        mmax = cloud_model.max_azi_num()
        rp0 = (Mbh0+np.sqrt(Mbh0**2-(abh0*Mbh0)**2))
        OmegaBH0 = 0.5*abh0/rp0
        Mir0 = 0.5*rp0
        m = 1
        omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0
        while (not(omega0<m*OmegaBH0)):
            m = m+1
            if (m>mmax): break
            else: omega0 = cloud_model.omega_real(m, mu*Mbh0,abh0,0)/Mbh0
        if (m>mmax): 
            raise ValueError("Error, azimuthal number > %d not supported." % (mmax))

        #Find cloud frequency/mass at saturation
        Jbh0 = abh0*Mbh0**2
        omegaR = 1.0*omega0
        omegaRprevious = 0.0
        rel_omega_tol = 1.0e-10
        max_iter = 100
        i=0
        while (abs(omegaRprevious-omegaR)>rel_omega_tol*mu and i<max_iter):
            omegaRprevious = 1.0*omegaR
            Mbhf = (m**3-np.sqrt(m**6-16.0*m**2*omegaR**2*(m*Mbh0-omegaR*Jbh0)**2))/(8.0*omegaR**2*(m*Mbh0-omegaR*Jbh0))
            Jbhf = Jbh0 -m/omegaR*(Mbh0-Mbhf)
            omegaR = cloud_model.omega_real(m, mu*Mbhf, Jbhf/Mbhf**2, (Mbh0-Mbhf)/Mbhf)/Mbhf
            i = i+1
        if (i>=max_iter):
            warnings.warn(("Saturation condition only satisfied up to relative difference of %e" 
                                 % (abs(omegaRprevious-omegaR)/mu)), RuntimeWarning)

        #Original black hole mass and spin
        self._Mbh0 = Mbh0 
        self._abh0 = abh0 
        # Frequency of cloud initially (at zero mass) 
        self._omegaR0 = omega0
        # Frequency of cloud at saturation
        self._omegaR = omegaR
        #Mass of black hole at saturation
        self._Mbh = Mbhf 
        #Mass of cloud at saturation
        self._Mcloud0 = Mbh0-Mbhf 
        #Dimensionless spin of black hole at saturation
        self._abh = Jbhf/self._Mbh**2
        #Azimuthal number of cloud
        self._m = m
        #Ultralight boson mass
        self._mu = mu
        self._cloud_model = cloud_model
        self._Pgwt = self._cloud_model.power_gw(self._m, self._mu*self._Mbh, self._abh)
        #Spherical harmonic decomposition of strain
        self._hl = self._cloud_model.strain_sph_harm(self._m, self._mu*self._Mbh, self._abh)
        #e-folding time of boson cloud mass
        self._tauI = self._Mbh0/(2*self._cloud_model.omega_imag(self._m, self._mu*self._Mbh0, self._abh0))
    def azimuthal_num(self):
        """Azimuthal number of cloud (mass/gravitational waves have twice this)"""
        return self._m
    def mass_bh_final(self):
        """Black hole mass at saturation"""
        return self._Mbh
    def spin_bh_final(self):
        """Black hole dimensionless spin at saturation"""
        return self._abh
    def efold_time(self):
        """Before saturation, e-folding time of boson cloud mass"""
        return (self._tauI*self._tunit)
    def cloud_growth_time(self):
        """Time for cloud to grow from single boson to saturation"""
        return (self.efold_time()*np.log(self._Mcloud0/(self._mu*self._hbar)))
    def mass_cloud(self, t):
        """Mass of boson cloud as  function of time"""
        t = t/self._tunit
        tnorm = t*self._Pgwt*self._Mcloud0/self._Mbh**2
        H = np.heaviside(tnorm,1.0) 
        treg = (1.0-H)*t #to prevent overflow in exponential
        return (H*self._Mcloud0/(1+tnorm)+(1.0-H)*self._Mcloud0*np.exp(treg/self._tauI))
    def _mass_cloud_dot(self, t):
        """Time derivative of mass of boson cloud as  function of time"""
        t = t/self._tunit
        tnorm = t*self._Pgwt*self._Mcloud0/self._Mbh**2
        H = np.heaviside(tnorm,1.0) 
        treg = (1.0-H)*t #to prevent overflow in exponential
        Mcdot_p = (self._Mcloud0/(1+tnorm))**2*(-1.0*self._Pgwt/self._Mbh**2)
        Mcdot_n = self._Mcloud0*np.exp(treg/self._tauI)/self._tauI
        return (H*Mcdot_p+(1.0-H)*Mcdot_n)
    def power_gw(self, t):
        """Power (luminosity) of gravitational waves as a function of time"""
        Mc = self.mass_cloud(t)
        return (self._Punit*self._Pgwt*(Mc)**2/self._Mbh**2)
    def gw_time(self):
        """Characteristic timescale of GW emission (Mc/P_GW) at saturation"""
        return (self._tunit*self._Mbh**2/(self._Pgwt*self._Mcloud0))
    def freq_gw(self, t):
        """Frequency of gravitational wave signal as a function of time"""
        Mc = self.mass_cloud(t)
        omegaR_vec = np.vectorize(self._cloud_model.omega_real, excluded=[0,1,2])
        H = np.heaviside(t,1.0)
        fgw = (H*omegaR_vec(self._m, self._mu*self._Mbh, self._abh, Mc/self._Mbh)/self._Mbh
               +(1.0-H)*(self._omegaR+(self._omegaR-self._omegaR0)*(Mc/self._Mcloud0-1)) 
              )/np.pi
        return (fgw/self._tunit)
    def freqdot_gw(self, t):
        """Time derivative of frequency of gravitational wave signal as a function of time"""
        Mc = self.mass_cloud(t)
        Mcdot = self._mass_cloud_dot(t) 
        domegaRdMc_vec = np.vectorize(self._cloud_model.domegar_dmc, excluded=[0,1,2])
        H = np.heaviside(t,1.0) 
        fdotgw = (H*domegaRdMc_vec(self._m, self._mu*self._Mbh, self._abh, Mc/self._Mbh)
                  /self._Mbh**2*Mcdot
                  +(1.0-H)*(self._omegaR-self._omegaR0)*Mcdot/self._Mcloud0)/np.pi
        return (fdotgw/self._tunit**2)
    def strain_char(self, t, dObs=None): 
        """
        A characteristic strain value, defined to be: 
        h0:=(10 P_{GW})^{1/2}/(omega_{GW}*dObs).
        dObs is distance to source.

        In the non-relativistic limit (and for azimuthal_num=1), should have that:
        h_+ = h_0*(1+cos^2(theta))/2*cos(phi(t))
        h_x = h_0*cos(theta)*sin(phi(t))
        """
        if (dObs is None):
            #If not specified, assume strain is evaluated at a distance equal to the black hole mass
            dObs = self._Mbh
        else:
            dObs = dObs/self._dunit
        Mc = self.mass_cloud(t)
        omegaR_vec = np.vectorize(self._cloud_model.omega_real, excluded=[0,1,2])
        omegagw = 2.0*omegaR_vec(self._m, self._mu*self._Mbh, self._abh, Mc/self._Mbh)/self._Mbh
        h0 = (10.0*self._Pgwt*(Mc)**2/self._Mbh**2)**0.5/dObs/omegagw
        return h0 
    def strain_amp(self, t, thetaObs, dObs=None):
        """
        Returns magnitude of two polarizations of strain (h_+,h_x) as a
        function of time and inclination angle with respect to spin axis.  Also
        return delta, where delta is the extra phase difference between
        polarizations.  That is, observed strain is: 
        h_I = F^I_+(t)*h_+(t)cos(phi(t))+F^I_x*h_x(t)*sin(phi(t)+delta) 

        dObs is distance to source.
        """
        if (dObs is None):
            #If not specified, assume strain is evaluated at a distance equal to the black hole mass
            dObs = self._Mbh
        else:
            dObs = dObs/self._dunit
        Mc = self.mass_cloud(t)
        hp = 0.0
        hx = 0.0
        l = 2*self._m 
        for hl0 in self._hl:
            Yp = sYlm(-2,l,2*self._m,thetaObs)
            Ym = sYlm(-2,l,-2*self._m,thetaObs)
            hp = hp + hl0*(Yp+(-1)**l*Ym)
            hx = hx + hl0*(Yp-(-1)**l*Ym)
            l = l + 1
        delta = np.angle(hx)-np.angle(hp)
        #Make delta in [-pi,pi)
        delta = (delta + np.pi) % (2 * np.pi) - np.pi
        hp = np.abs(hp)*(Mc/self._Mbh)/(dObs/self._Mbh)
        hx = np.abs(hx)*(Mc/self._Mbh)/(dObs/self._Mbh)
        return (hp,hx,delta) 
    def phase_gw(self, t):
        """
        Return the gravitational wave phase [phi(t) as defined above] as a
        function of time. Exact when domega/dMc is a constant part plus a part linear in Mc.
        By convention, the phase is zero at t=0.
        """
        t = t/self._tunit
        tau = self._Mbh**2/(self._Pgwt*self._Mcloud0)
        # constant part in domegar_dmc(mc)
        domegaRdMc_const_t0 = self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbh, self._abh, 0)/self._Mbh**2 
        # linear part in domegar_dmc(mc)
        domegaRdMc_lin_t0 = (self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbh, self._abh, self._Mcloud0)/(self._Mbh**3) - self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbh, self._abh, 0)/self._Mbh**3)/(2 * self._Mcloud0)
        omega_M0 = self._cloud_model.omega_real(self._m, self._mu*self._Mbh, self._abh, 0)/self._Mbh
        H = np.heaviside(t,1.0) 
        treg = (1.0-H)*t #to prevent overflow in exponential
        phi = 2.0*(H*(omega_M0*t + domegaRdMc_const_t0 * self._Mcloud0 * tau * np.log(1.0+t/tau) + domegaRdMc_lin_t0 * self._Mcloud0**2 * tau * (t/(t+tau)))
                   +(1.0-H)*(self._omegaR0*t+
                     (self._omegaR-self._omegaR0)*self._tauI*(np.exp(treg/self._tauI)-1.0)))
        return (phi)
