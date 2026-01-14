from abc import ABCMeta, abstractmethod

class BosonCloudWaveform(metaclass=ABCMeta):
    @abstractmethod
    def __init__(self, mu, Mbh0, abh0, cloud_model, units="natural"):
        """
        Calculate some derived quantites using the specified CloudModel
        for the specified parameters:
        mu : ultralight boson mass
        Mbh0 : initial black hole mass (before cloud growth)
        abh0 : initial black hole dimensionless (before cloud growth)
        
        If units="physical" use the following units for input/output:

        mu : electronvolts
        Mass : solar mass
        time : seconds
        frequency : Hz
        Power : watts
        Distance : Mpc

        If units="natural" assume G=c=hbar=1

        If "+alpha" is appended to either "physical" or "natural," then units
        are the same as above, except the input mu is taken to be in units of 
        (hbar c^3)/(G*Mbh0), i.e.  mu is set to the dimensionless 
        "fine structure constant" alpha. 
        """
        pass
    @abstractmethod
    def azimuthal_num(self):
        """Azimuthal number of cloud (mass/gravitational waves have twice this)"""
        pass
    @abstractmethod
    def mass_bh_final(self):
        """Black hole mass at saturation"""
        pass
    @abstractmethod
    def spin_bh_final(self):
        """Black hole dimensionless spin at saturation"""
        pass
    @abstractmethod
    def efold_time(self):
        """Before saturation, e-folding time of boson cloud mass"""
        pass
    @abstractmethod
    def cloud_growth_time(self):
        """Time for cloud to grow from single boson to saturation"""
        pass
    @abstractmethod
    def mass_cloud(self, t):
        """Mass of boson cloud as  function of time"""
        pass
    @abstractmethod
    def power_gw(self, t):
        """Power (luminosity) of gravitational waves as a function of time"""
        pass
    @abstractmethod
    def gw_time(self):
        """Characteristic timescale of GW emission (Mc/P_GW) at saturation"""
        pass
    @abstractmethod
    def freq_gw(self, t):
        """Frequency of gravitational wave signal as a function of time"""
        pass
    @abstractmethod
    def freqdot_gw(self, t):
        """Time derivative of frequency of gravitational wave signal as a function of time"""
        pass
    @abstractmethod
    def strain_char(self, t, dObs=None): 
        """
        A characteristic strain value, defined to be: 
        h0:=(10 P_{GW})^{1/2}/(omega_{GW}*dObs).
        dObs is distance to source.

        In the non-relativistic limit (and for azimuthal_num=1), should have that:
        h_+ = h_0*(1+cos^2(theta))/2*cos(phi(t))
        h_x = h_0*cos(theta)*sin(phi(t))
        """
        pass
    @abstractmethod
    def strain_amp(self, t, thetaObs, dObs=None):
        """
        Returns magnitude of two polarizations of strain (h_+,h_x) as a
        function of time and inclination angle with respect to spin axis.  Also
        return delta, where delta is the extra phase difference between
        polarizations.  That is, observed strain is: 
        h_I = F^I_+(t)*h_+(t)cos(phi(t))+F^I_x*h_x(t)*sin(phi(t)+delta) 

        dObs is distance to source.
        """
        pass
    @abstractmethod
    def phase_gw(self, t):
        """
        Return the gravitational wave phase [phi(t) as defined above] as a
        function of time. Here we assume (take the approximation) that domega/dMc is a
        constant. By convention, the phase is zero at t=0.
        """
        pass
