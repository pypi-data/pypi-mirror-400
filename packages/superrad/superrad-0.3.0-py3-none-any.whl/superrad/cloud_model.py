from abc import ABCMeta, abstractmethod

class CloudModel(metaclass=ABCMeta):
    """
    Abstract base class encompassing functions needed
    to compute ultralight boson cloud gravitational waves.

    All inputs are in units where black hole mass=G=c=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    m is azimuthal number of cloud
    """
    @abstractmethod
    def boson_spin(self):
        """Spin of boson"""
        pass
    @abstractmethod
    def max_azi_num(self):
        """Maximum azimuthal number the model is defined for"""
        pass
    @abstractmethod
    def max_spin(self):
        """Maximum spin the model is defined for"""
        pass
    @abstractmethod
    def omega_real(self, m, alpha, abh, Mcloud):
        """Returns real frequency of cloud oscillation"""
        pass
    @abstractmethod
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        """Returns derivative of real frequency of cloud oscillation w.r.t.
        cloud mass: domega_R/dMc"""
        pass
    @abstractmethod
    def omega_imag(self, m, alpha, abh):
        """Returns imaginary frequency, 
           i.e. growth rate of superradiant instability"""
        pass
    @abstractmethod
    def power_gw(self, m, alpha, abh):
        """Returns gravitational wave power, scaled to Mcloud=1"""
        pass
    @abstractmethod
    def strain_sph_harm(self, m, alpha, abh):
        """
        Returns array of C(l=2m,2m), C_(l=2m+1,2m), C_(l=2m+2,2m)...
        corresponding to the spherical harmonics of the gravitational wave strain
        
        Still need to work out conventions here (spin-weighted?, normalization?, what about -2m? etc...)
        """
        pass
