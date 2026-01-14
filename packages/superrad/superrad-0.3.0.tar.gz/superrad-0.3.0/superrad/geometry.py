from abc import ABCMeta, abstractmethod

class Geometry(metaclass=ABCMeta):
    """
    Abstract base class encompassing functions needed
    to compute geometrical quantities for black holes with ultralight boson clouds.

    All inputs are in units where black hole mass=G=c=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    These quantities are only calculated for m=1 (m is azimuthal number of cloud)
    """
    @abstractmethod
    def alpha_data(self):
        pass
    @abstractmethod
    def Mcloud_data(self):
        pass
    @abstractmethod
    def LightRing_radius_data(self):
        pass
    @abstractmethod
    def ISCO_radius_data(self):
        pass
    @abstractmethod
    def ISCO_orbital_freq_data(self):
        pass
    @abstractmethod
    def ISCO_redshift_data(self):
        pass
    @abstractmethod
    def ISCO_blueshift_data(self):
        pass
    @abstractmethod
    def LightRing_radius(self, alpha, Mcloud):
        """Returns prograde light ring circumferential radius"""
        pass
    @abstractmethod
    def ISCO_radius(self, alpha, Mcloud):
        """Returns prograde ISCO circumferential radius"""
        pass
    @abstractmethod
    def ISCO_orbital_freq(self, alpha, Mcloud):
        """Returns orbital frequency at the prograde ISCO"""
        pass
    @abstractmethod
    def ISCO_redshift(self, alpha, Mcloud):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the same direction"""
        pass
    @abstractmethod
    def ISCO_blueshift(self, alpha, Mcloud):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the opposite direction.
        This geodesic stops escaping the black hole for higher spins (approximately abh = 0.94) when the ISCO radius enters the ergoregion."""
        pass
    @abstractmethod
    def alpha_error(self, alpha, Mcloud):
        """Error in LightRing_radius data (not accounting for interpolation error)"""
        pass
    @abstractmethod
    def CloudMass_error(self, alpha, Mcloud):
        """Error in LightRing_radius data (not accounting for interpolation error)"""
        pass
    @abstractmethod
    def BHSpin_error(self, alpha, Mcloud):
        """Error in LightRing_radius data (not accounting for interpolation error)"""
        pass
    @abstractmethod
    def LightRing_radius_error(self, alpha, Mcloud):
        """Error in LightRing_radius data (not accounting for interpolation error)"""
        pass
    @abstractmethod
    def ISCO_radius_error(self, alpha, Mcloud):
        """Error in ISCO_radius data (not accounting for interpolation error)"""
        pass
    def ISCO_orbital_freq_error(self, alpha, Mcloud):
        """Error in ISCO_orbital_freq data (not accounting for interpolation error)"""
        pass
    def ISCO_redshift_error(self, alpha, Mcloud):
        """Error in ISCO_redshift data (not accounting for interpolation error)"""
        pass
    def ISCO_blueshift_error(self, alpha, Mcloud):
        """Error in ISCO_blueshift data (not accounting for interpolation error)"""
        pass
                         
