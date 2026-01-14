import numpy as np
from .boson_waveform import BosonCloudWaveform
from .cloud_model import CloudModel 
from .evolve_cloud import EvolveCloud
from .harmonics import sYlm 
from .units import set_units
import warnings
from scipy.interpolate import interp1d
try:
    from scipy.integrate import cumulative_trapezoid as cumtrapz
except ImportError:
    from scipy.integrate import cumtrapz as cumtrapz

class FullEvoWaveform(BosonCloudWaveform):
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

        #Find approximate cloud frequency/mass at saturation
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

        #Azimuthal number of cloud
        self._m = m
        #Ultralight boson mass
        self._mu = mu
        self._cloud_model = cloud_model
        #Original black hole mass and spin
        self._Mbh0 = Mbh0 
        self._abh0 = abh0 

        Mc0 = 1.0e-6*(Mbh0-Mbhf)
        Pgwt = cloud_model.power_gw(m, mu*Mbhf, Jbhf/Mbhf**2)
        tgw = Mbhf**2/(Pgwt*(Mbh0-Mbhf))
        #e-folding time of boson cloud mass
        self._tauI = self._Mbh0/(2*self._cloud_model.omega_imag(self._m, self._mu*self._Mbh0, self._abh0))
        tc = np.linspace(0, 100.0*self._tauI, 2048)

        evoCloud = EvolveCloud(cloud_model, m, mu, Mbh0, abh0*Mbh0**2, Mc0, tc)
        Mc = evoCloud.mass_cloud()
        Mcdot = evoCloud.mass_cloud_dot()
        #Mass of black hole at saturation
        Mbh = evoCloud.mass_bh() 
        #Dimensionless spin of black hole at saturation
        abh = evoCloud.spin_bh() 

        omegaR_vec = np.vectorize(cloud_model.omega_real, excluded=[0])
        omega_gw = 2.0*omegaR_vec(self._m, self._mu*Mbh, abh, Mc/Mbh)/Mbh
        phi = cumtrapz(omega_gw, x=tc, initial=0) 

        I = np.argmax(Mc)
        self._Mcloud0 = Mc[I]
        tc = tc-tc[I]
        phi = phi-phi[I]
        #Time at which cloud is one boson
        self._t_one_boson = tc[0]-self._tauI*np.log(Mc0/(self._mu*self._hbar))
        self._tci = tc[0]
        self._tcf = tc[-1]
        self._Mci = Mc[0]
        self._Mcf = Mc[-1]
        self._phi_gwi = phi[0]
        self._phi_gwf = phi[-1]
        self._Mc = interp1d(tc, Mc, kind="cubic") 
        self._Mcdot = interp1d(tc, Mcdot, kind="cubic") 
        self._phi_gw = interp1d(tc, phi, kind="cubic") 
        self._Mbh = interp1d(tc, Mbh, bounds_error=False, fill_value=(Mbh[0],Mbh[-1]), kind="cubic") 
        self._Mbhf = Mbh[-1]
        #Dimensionless spin of black hole 
        self._abh = interp1d(tc, abh, bounds_error=False, fill_value=(abh[0],abh[-1]), kind="cubic") 
        self._abhf = abh[-1]
        self._Pgwt = cloud_model.power_gw(m, mu*self._Mbhf,  self._abhf) 
        #Spherical harmonic decomposition of strain
        self._hl = self._cloud_model.strain_sph_harm(self._m, self._mu*self._Mbhf, self._abhf)
    def azimuthal_num(self):
        """Azimuthal number of cloud (mass/gravitational waves have twice this)"""
        return self._m
    def mass_bh_final(self):
        """Black hole mass at saturation"""
        return self._Mbhf
    def spin_bh_final(self):
        """Black hole dimensionless spin at saturation"""
        return self._abhf
    def efold_time(self):
        """Before saturation, e-folding time of boson cloud mass"""
        return (self._tauI*self._tunit)
    def cloud_growth_time(self):
        """Time for cloud to grow from single boson to saturation"""
        return (-1.0*self._tunit*self._t_one_boson)
    def mass_cloud(self, t):
        """Mass of boson cloud as  function of time"""
        t = np.atleast_1d(t)/self._tunit
        Mc = np.empty_like(t)
        Mc[t<=self._tci] = self._Mci*np.exp((t[t<=self._tci]-self._tci)/self._tauI)
        tnorm = (t[t>=self._tcf]-self._tcf)*self._Pgwt*self._Mcf/self._Mbhf**2
        Mc[t>=self._tcf] = self._Mcf/(1+tnorm)
        I = np.logical_and(t>self._tci,t<self._tcf)
        Mc[I] = self._Mc(t[I])
        return Mc
    def _mass_cloud_dot(self, t):
        """Time derivative of mass of boson cloud as  function of time"""
        t = np.atleast_1d(t)/self._tunit
        Mcdot = np.empty_like(t)
        Mcdot[t<=self._tci] = self._Mci*np.exp((t[t<=self._tci]-self._tci)/self._tauI)/self._tauI
        tnorm = (t[t>=self._tcf]-self._tcf)*self._Pgwt*self._Mcf/self._Mbhf**2
        Mcdot[t>=self._tcf] = (self._Mcf/(1+tnorm))**2*(-1.0*self._Pgwt/self._Mbhf**2)
        I = np.logical_and(t>self._tci,t<self._tcf)
        Mcdot[I] = self._Mcdot(t[I])
        return Mcdot
    def power_gw(self, t):
        """Power (luminosity) of gravitational waves as a function of time"""
        t = np.atleast_1d(t)
        Mc = self.mass_cloud(t)
        Mbh = self._Mbh(t/self._tunit)
        abh = self._abh(t/self._tunit)
        #vectorize
        Pgw_vec = np.vectorize(self._cloud_model.power_gw, excluded=[0])
        Pgwt = Pgw_vec(self._m, self._mu*Mbh, abh) 
        return (self._Punit*self._Pgwt*(Mc)**2/Mbh**2)
    def gw_time(self):
        """Characteristic timescale of GW emission (Mc/P_GW) at saturation"""
        return (self._tunit*self._Mbhf**2/(self._Pgwt*self._Mcloud0))
    def freq_gw(self, t):
        """Frequency of gravitational wave signal as a function of time"""
        t = np.atleast_1d(t)
        Mc = self.mass_cloud(t)
        Mbh = self._Mbh(t/self._tunit)
        abh = self._abh(t/self._tunit)
        omegaR_vec = np.vectorize(self._cloud_model.omega_real, excluded=[0])
        fgw = omegaR_vec(self._m, self._mu*Mbh, abh, Mc/Mbh)/Mbh/np.pi
        return (fgw/self._tunit)
    def freqdot_gw(self, t):
        """Time derivative of frequency of gravitational wave signal as a function of time"""
        #Currently, this is just a crude finite difference approximation
        dt = self._tauI/512*self._tunit
        fdot = (self.freq_gw(t+0.5*dt)-self.freq_gw(t-0.5*dt))/dt
        return (fdot)
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
            dObs = self._Mbhf
        else:
            dObs = dObs/self._dunit
        Mc = self.mass_cloud(t)
        Mbh = self._Mbh(t/self._tunit)
        abh = self._abh(t/self._tunit)
        omegaR_vec = np.vectorize(self._cloud_model.omega_real, excluded=[0])
        omegagw = 2.0*omegaR_vec(self._m, self._mu*Mbh, abh, Mc/Mbh)/Mbh
        h0 = (10.0*self.power_gw(t)/self._Punit)**0.5/dObs/omegagw
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
            dObs = self._Mbhf
        else:
            dObs = dObs/self._dunit
        t = np.atleast_1d(t)
        Mc = self.mass_cloud(t)
        Mbh = self._Mbh(t/self._tunit)
        abh = self._abh(t/self._tunit)
        strain_vec = np.vectorize(self._cloud_model.strain_sph_harm, excluded=[0], signature='(),()->(n)')
        hl = strain_vec(self._m, self._mu*Mbh, abh)
        hp = 0.0
        hx = 0.0
        l = 2*self._m 
        for nl0 in range(hl.shape[-1]):
            Yp = sYlm(-2,l,2*self._m,thetaObs)
            Ym = sYlm(-2,l,-2*self._m,thetaObs)
            hp = hp + hl[:,nl0]*(Yp+(-1)**l*Ym)
            hx = hx + hl[:,nl0]*(Yp-(-1)**l*Ym)
            l = l + 1
        delta = np.angle(hx)-np.angle(hp)
        #Make delta in [-pi,pi)
        delta = (delta + np.pi) % (2 * np.pi) - np.pi
        hp = np.abs(hp)*(Mc/Mbh)/(dObs/Mbh)
        hx = np.abs(hx)*(Mc/Mbh)/(dObs/Mbh)
        return (hp,hx,delta) 
    def phase_gw(self, t):
        """
        Return the gravitational wave phase [phi(t) as defined above] as a
        function of time. Exact when domega/dMc is a constant plus a piece 
        linear in Mc. By convention, the phase is zero at t=0.
        """
        t = np.atleast_1d(t)/self._tunit
        phi = np.empty_like(t)

        omega_Mi = self._cloud_model.omega_real(self._m, self._mu*self._Mbh0, self._abh0, 0)/self._Mbh0
        domegaRdMc_ti = self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbh0, self._abh0, self._Mci/self._Mbh0)/self._Mbh0**2 
        phi[t<=self._tci] = self._phi_gwi+2.0*(
                            omega_Mi*(t[t<=self._tci]-self._tci)
                            +domegaRdMc_ti*self._Mci*self._tauI*(np.exp((t[t<=self._tci]-self._tci)/self._tauI)-1.0))

        omega_Mf = self._cloud_model.omega_real(self._m, self._mu*self._Mbhf, self._abhf, 0)/self._Mbhf
        domegaRdMc_tf_const = self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbhf, self._abhf, 0)/self._Mbhf**2
        domegaRdMc_tf_lin =  (self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbhf, self._abhf, self._Mcf/self._Mbhf)/(self._Mbhf**2) - self._cloud_model.domegar_dmc(self._m, self._mu*self._Mbhf, self._abhf, 0)/self._Mbhf**2)/(2 * self._Mcf/self._Mbhf)
        tau = self._Mbhf**2/(self._Pgwt*self._Mcf)
        phi[t>=self._tcf] = self._phi_gwf+2.0*(
                            omega_Mf*(t[t>=self._tcf]-self._tcf)
                            +domegaRdMc_tf_const*self._Mcf*tau*np.log(1.0+(t[t>=self._tcf]-self._tcf)/tau)) +domegaRdMc_tf_lin*self._Mcf*tau*((t[t>=self._tcf]-self._tcf)/((t[t>=self._tcf]-self._tcf)+tau))
        I = np.logical_and(t>self._tci,t<self._tcf)
        phi[I] = self._phi_gw(t[I])
        return (phi)
