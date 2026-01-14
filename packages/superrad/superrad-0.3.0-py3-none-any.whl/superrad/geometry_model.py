from .geometry import Geometry
import numpy as np
from pathlib import Path
from scipy.optimize import fsolve
from scipy.interpolate import SmoothBivariateSpline
from scipy.interpolate import LinearNDInterpolator
from scipy.optimize import least_squares

class ScalarGeometry(Geometry):
    """
    Geometric quantities for black holes with boson clouds

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mc is boson cloud mass (as fraction of black hole mass)
    for all calculations here the azimuthal number of cloud is m=1
    """
    def __init__(self):
        """Importing data files"""
        scalar_data = np.load(Path(__file__).parent.joinpath('data/scalar_geometry.npz'))
        self._Mc = scalar_data['Mc'].flatten()
        self._alpha = scalar_data['alpha'].flatten()
        self._Madm = scalar_data['Madm'].flatten()
        self._Jadm = scalar_data['Jadm'].flatten()
        self._Jbh = scalar_data['Jbh'].flatten()
        self._Rlr = scalar_data['Rlr'].flatten()
        self._Risco = scalar_data['Risco'].flatten()
        self._redshift = scalar_data['redshift'].flatten()
        self._blueshift = scalar_data['blueshift'].flatten()
        self._iscofreq = scalar_data['iscofreq'].flatten()
        scalar_data = np.load(Path(__file__).parent.joinpath('data/scalar_geometry_errors.npz'))
        Mc_err_param = scalar_data['Mc'].flatten()
        alpha_err_param = scalar_data['alpha'].flatten()
        Mc_err = scalar_data['McErr'].flatten()
        alpha_err = scalar_data['alphaErr'].flatten()
        Jbh_err = scalar_data['Jbh'].flatten()
        Rlr_err = scalar_data['Rlr'].flatten()
        Risco_err = scalar_data['Risco'].flatten()
        redshift_err = scalar_data['redshift'].flatten()
        blueshift_err = scalar_data['blueshift'].flatten()
        iscofreq_err = scalar_data['iscofreq'].flatten()
        """ now interpolating over data"""
        self._lrinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._Rlr)
        self._iscointerp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._Risco)
        self._iscofreqinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._iscofreq)
        self._rdshiftinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._redshift)
        self._blshiftinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._blueshift)
        self._errMc = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Mc_err)
        self._erralpha = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), alpha_err)
        self._errJbh = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Jbh_err)
        self._errlr = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Rlr_err)
        self._errisco = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Risco_err)
        self._erriscofreq = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), iscofreq_err)
        self._errredshift = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), redshift_err)
        self._errblshift = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), blueshift_err)

    def alpha_data(self):
        return self._alpha
    def Mcloud_data(self):
        return self._Mc
    def Jbh_data(self):
        "Returns angular momentum of the internal black hole"
        return self._Jbh
    def LightRing_radius_data(self):
        return self._Rlr
    def ISCO_radius_data(self):
        return self._Risco
    def ISCO_orbital_freq_data(self):
        return self._iscofreq
    def ISCO_redshift_data(self):
        return self._redshift
    def ISCO_blueshift_data(self):
        return self._blueshift
    def LightRing_radius(self, alpha, Mc):
        """Returns prograde light ring circumferential radius"""
        return self._lrinterp(alpha, Mc)
    def ISCO_radius(self, alpha, Mc):
        """Returns prograde ISCO circumferential radius"""
        return self._iscointerp(alpha, Mc)
    def ISCO_orbital_freq(self, alpha, Mc):
        """Returns orbital frequency at the prograde ISCO"""
        return self._iscofreqinterp(alpha, Mc)
    def ISCO_redshift(self, alpha, Mc):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the same direction"""
        return self._rdshiftinterp(alpha, Mc)
    def ISCO_blueshift(self, alpha, Mc):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the opposite direction.
        This geodesic stops escaping the black hole for higher spins (approximately abh = 0.94) when the ISCO radius enters the ergoregion."""
        return self._blshiftinterp(alpha, Mc)
    def alpha_error(self, alpha, Mc):
        return self._erralpha(alpha, Mc)
    def CloudMass_error(self, alpha, Mc):
        return self._errMc(alpha, Mc)
    def BHSpin_error(self, alpha, Mc):
        return self._errJbh(alpha, Mc)
    def LightRing_radius_error(self, alpha, Mc):
        return self._errlr(alpha, Mc)
    def ISCO_radius_error(self, alpha, Mc):
        return self._errisco(alpha, Mc)
    def ISCO_orbital_freq_error(self, alpha, Mc):
        return self._erriscofreq(alpha, Mc)
    def ISCO_redshift_error(self, alpha, Mc):
        return self._errredshift(alpha, Mc)
    def ISCO_blueshift_error(self, alpha, Mc):
        return self._errblshift(alpha, Mc)

class VectorGeometry(Geometry):
    """
    Geometric quantities for black holes with boson clouds

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mc is boson cloud mass (as fraction of black hole mass)
    for all calculations here the azimuthal number of cloud is m=1
    """
    def __init__(self):
        """Importing data files"""
        vector_data = np.load(Path(__file__).parent.joinpath('data/vector_geometry.npz'))
        self._Mc = vector_data['Mc'].flatten()
        self._alpha = vector_data['alpha'].flatten()
        self._Madm = vector_data['Madm'].flatten()
        self._Jadm = vector_data['Jadm'].flatten()
        self._Jbh = vector_data['Jbh'].flatten()
        self._Rlr = vector_data['Rlr'].flatten()
        self._Risco = vector_data['Risco'].flatten()
        self._redshift = vector_data['redshift'].flatten()
        self._blueshift = vector_data['blueshift'].flatten()
        self._iscofreq = vector_data['iscofreq'].flatten()
        vector_data = np.load(Path(__file__).parent.joinpath('data/vector_geometry_errors.npz'))
        Mc_err_param = vector_data['Mc'].flatten()
        alpha_err_param = vector_data['alpha'].flatten()
        Mc_err = vector_data['McErr'].flatten()
        alpha_err = vector_data['alphaErr'].flatten()
        Jbh_err = vector_data['Jbh'].flatten()
        Rlr_err = vector_data['Rlr'].flatten()
        Risco_err = vector_data['Risco'].flatten()
        redshift_err = vector_data['redshift'].flatten()
        blueshift_err = vector_data['blueshift'].flatten()
        iscofreq_err = vector_data['iscofreq'].flatten()
        """ now interpolating over data"""
        self._lrinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._Rlr)
        self._iscointerp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._Risco)
        self._iscofreqinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._iscofreq)
        self._rdshiftinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._redshift)
        self._blshiftinterp = LinearNDInterpolator(list(zip(self._alpha,self._Mc)), self._blueshift)
        self._errMc = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Mc_err)
        self._erralpha = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), alpha_err)
        self._errJbh = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Jbh_err)
        self._errlr = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Rlr_err)
        self._errisco = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), Risco_err)
        self._erriscofreq = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), iscofreq_err)
        self._errredshift = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), redshift_err)
        self._errblshift = LinearNDInterpolator(list(zip(alpha_err_param,Mc_err_param)), blueshift_err)

    def alpha_data(self):
        return self._alpha
    def Mcloud_data(self):
        return self._Mc
    def Jbh_data(self):
        "Returns angular momentum of the internal black hole"
        return self._Jbh
    def LightRing_radius_data(self):
        return self._Rlr
    def ISCO_radius_data(self):
        return self._Risco
    def ISCO_orbital_freq_data(self):
        return self._iscofreq
    def ISCO_redshift_data(self):
        return self._redshift
    def ISCO_blueshift_data(self):
        return self._blueshift
    def LightRing_radius(self, alpha, Mc):
        """Returns prograde light ring circumferential radius"""
        return self._lrinterp(alpha, Mc)
    def ISCO_radius(self, alpha, Mc):
        """Returns prograde ISCO circumferential radius"""
        return self._iscointerp(alpha, Mc)
    def ISCO_orbital_freq(self, alpha, Mc):
        """Returns orbital frequency at the prograde ISCO"""
        return self._iscofreqinterp(alpha, Mc)
    def ISCO_redshift(self, alpha, Mc):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the same direction"""
        return self._rdshiftinterp(alpha, Mc)
    def ISCO_blueshift(self, alpha, Mc):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the opposite direction.
        This geodesic stops escaping the black hole for higher spins (approximately abh = 0.94) when the ISCO radius enters the ergoregion."""
        return self._blshiftinterp(alpha, Mc)
    def alpha_error(self, alpha, Mc):
        return self._erralpha(alpha, Mc)
    def CloudMass_error(self, alpha, Mc):
        return self._errMc(alpha, Mc)
    def BHSpin_error(self, alpha, Mc):
        return self._errJbh(alpha, Mc)
    def LightRing_radius_error(self, alpha, Mc):
        return self._errlr(alpha, Mc)
    def ISCO_radius_error(self, alpha, Mc):
        return self._errisco(alpha, Mc)
    def ISCO_orbital_freq_error(self, alpha, Mc):
        return self._erriscofreq(alpha, Mc)
    def ISCO_redshift_error(self, alpha, Mc):
        return self._errredshift(alpha, Mc)
    def ISCO_blueshift_error(self, alpha, Mc):
        return self._errblshift(alpha, Mc)
