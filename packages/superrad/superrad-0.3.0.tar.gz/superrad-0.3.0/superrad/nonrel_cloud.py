from .cloud_model import CloudModel 
from scipy import interpolate
from scipy import optimize
import numpy as np
import math

class NonrelScalar(CloudModel):
    """
    Non-relativistic (alpha<<1) model for scalar bosons

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    m is azimuthal number of cloud
    """
    def __init__(self):
        self._max_m = 15
    def boson_spin(self):
        """Spin of boson"""
        return 0
    def max_azi_num(self):
        """Maximum azimuthal number the model is defined for"""
        return self._max_m 
    def max_spin(self):
        """Maximum spin the model is defined for"""
        return 1.0
    def _shift_factor(self,m):
        coeffs = [-(93/1024), -(793/18432), -(26333/1048576), -(43191/2621440), -(
  1172755/100663296), -(28539857/3288334336), -(1846943453/
  274877906944), -(14911085359/2783138807808), -(240416274739/
  54975581388800), -(1936010885087/532163627843584), -(62306843256889/
  20266198323167232), -(500960136802799/190277084256403456), -(
  8051112929645937/3530822107858468864), -(21555352563374699/
  10808639105689190400), -(8307059966383480541/4722366482869645213696)
  ]
        return coeffs[m-1]
    def omega_real(self, m, alpha, abh, Mcloud):
        """
        Returns real frequency of cloud oscillation.  For cloud mass
        correction, see eq. A4 in Isi et al.  Phys. Rev. D99,084042 (2019), but
        corrected with extra factor of 2 to go from gravitational energy to
        frequency shift
        """
        #If alpha/m is too high (outside superradiant regime) expansion breaks down
        if (alpha>1.5*m*0.5*abh/(1.0+np.sqrt(1.0-abh**2))):
            return np.nan
        l = m 
        n = l + 1
        fnl = -6/(2*l+1) + 2/n
        hl = 16/(2*l*(2*l+1)*(2*l+2))
        w = (alpha * (1-alpha**2/(2*n**2) - alpha**4/(8*n**4) 
                         + fnl * alpha**4 / (n**3) 
                         + hl * abh * m * alpha**5 /(n**3)))
        if (m <= self.max_azi_num()):
            w+= 2.0*self._shift_factor(m)*alpha**3*Mcloud
        else:
            raise ValueError("Azimuthal index too large")
        return w
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        """Returns derivative of real frequency of cloud w.r.t. cloud mass"""
        dwdMc = 0.0
        if (m <= self.max_azi_num()):
            dwdMc = 2.0*self._shift_factor(m)*alpha**3
        return dwdMc
    def omega_imag(self, m, alpha, abh):
        """Returns imaginary frequency, 
           i.e. growth rate of superradiant instability"""
        omega = self.omega_real(m, alpha, abh,0)
        rplus = 1 + np.sqrt(1-abh**2)
        omegaH = 0.5 * (abh/rplus)
        l = m 
        n = l + 1
        Cnl = 2**(4*l+1) * math.factorial(n+l)/(n**(2*l+4)*math.factorial(n-l-1)) * (math.factorial(l)/(math.factorial(2*l) * math.factorial(2*l+1)))**2
        glm = 1.0
        for k in range(l):
            glm*= (k+1)**2 *(1-abh**2) + (abh * m - 2*rplus *omega)**2
        return 2 * rplus * Cnl * glm * (m* omegaH - omega)*alpha**(4*l + 5)  
    def power_gw(self, m, alpha, abh):
        """Returns gravitational wave power, scaled to Mcloud=1.
        m=1: Eq. (13) in R. Brito et al. Class. Quantum Grav.32(2015) 134001
        m>1: Eq. (57) in Yoshino et al. PTEP 2014, 943E02 (2014)
        """
        if (m==1):
            return ((484.0+9.0*np.pi**2)/23040.0*alpha**14)
        else: 
            l = m
            n = l+1
            ql = 4*l+10
            cnl = (16**(l+1)*l*(2*l-1)*math.factorial(2*l-1-1)**2*math.factorial(l+n+1-1)**2)/(n**(4*l+8)*(l+1)*math.factorial(l+1-1)**4*math.factorial(4*l+3-1)*math.factorial(n-l-1)**2)
            return cnl*alpha**ql
    def strain_sph_harm(self, m, alpha, abh):
        omegaGW = 2.0*self.omega_real(m, alpha, abh, 0)
        h22 = -2.0*np.sqrt(2.0*np.pi*self.power_gw(m, alpha, abh))/omegaGW
        return np.array([h22])

class NonrelVector(CloudModel):
    """
    Non-relativistic (alpha<<1) model for vector bosons

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    m is azimuthal number of cloud
    """
    def __init__(self):
        self._max_m = 5
    def boson_spin(self):
        """Spin of boson"""
        return 1
    def max_azi_num(self):
        """Maximum azimuthal number the model is defined for"""
        return self._max_m 
    def max_spin(self):
        """Maximum spin the model is defined for"""
        return 1.0 
    def _shift_factor(self,m):
        coeffs = [-(5/16), -(93/1024), -(793/18432), -(26333/1048576), -(43191/
  2621440), -(1172755/100663296), -(28539857/3288334336), -(
  1846943453/274877906944), -(14911085359/2783138807808), -(
  240416274739/54975581388800), -(1936010885087/532163627843584), -(
  62306843256889/20266198323167232), -(500960136802799/
  190277084256403456), -(8051112929645937/3530822107858468864), -(
  21555352563374699/10808639105689190400)]
        return coeffs[m-1]
    def omega_real(self, m, alpha, abh, Mcloud):
        """
        Returns real frequency of cloud oscillation.  For cloud mass
        correction, see eq. E4 of Baryakhtar et al.  Phys. Rev. D96,035019
        (2017) but corrected with extra factor of 2 to go from gravitational
        energy to frequency shift, and for m>1 in SuperRad paper
        """
        #If alpha/m is too high (outside superradiant regime) expansion breaks down
        if (alpha>1.5*m*0.5*abh/(1.0+np.sqrt(1.0-abh**2))):
            return np.nan

        # Taking result from Baumann eq.2.30 , dominant mode
        l = m -1
        n = l + 1
        j = l + 1 
        fnlj = -4 * (6*l*j + 3*l + 3*j + 2)/((l+j)*(l+j+1)*(l+j+2)) + 2/n
        hlj = 16/((l+j)*(l+j+1)*(l+j+2))
        # 1/Mbh factor = 1
        w = alpha * ( 1 - alpha**2/(2*n**2) - alpha**4 / (8*n**4) 
                         + fnlj *alpha**4 /(n**3) 
                         + hlj *abh * m * alpha **5 / (n**3) )
        if (m<=self.max_azi_num()):
            w+= 2.0*self._shift_factor(m)*alpha**3*Mcloud
        else:
            raise ValueError("Azimuthal index too large")
        return w
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        """Returns derivative of real frequency of cloud w.r.t. cloud mass"""        
        dwdMc = 0.0
        if (m<=self.max_azi_num()):
            dwdMc = 2.0*self._shift_factor(m)*alpha**3 
        return dwdMc
    def omega_imag(self, m, alpha, abh):
        """Returns imaginary frequency, 
           i.e. growth rate of superradiant instability"""
        omega = self.omega_real(m, alpha, abh,0)
        rplus = 1 + np.sqrt(1-abh**2)
        omegaH = 0.5 * (abh/rplus) 
        l = m -1
        n = l + 1
        j = l + 1 
        Cnlj = 2**(2*l+2*j+1) * math.factorial(n+l)/(n**(2*l+4)*math.factorial(n-l-1)) * (math.factorial(l)/(math.factorial(l+j)*math.factorial(l+j+1)))**2 * (1+ 2*(1+l-j)*(1-l+j)/(l+j))**2
        gjm = 1.0
        for k in range(j):
            gjm*= (k+1)**2 *(1-abh**2) + (abh * m - 2*rplus *omega)**2
        return 2* rplus *Cnlj * gjm *(m * omegaH - omega) * alpha**(2*l+2*j+5)
    def power_gw(self, m, alpha, abh):
        """Returns gravitational wave power, scaled to Mcloud=1"""
        #Non-relativistic fit for m=1 from Siemonsen+ Phys. Rev. D 101, 024019 (2020)
        #All m>1 (uses flat approximation): Baryakhtar et al. Phys. Rev. D96,035019 (2017) (would give 32/5 or 60 for m=1)
        if (m==1):
            return (16.66*alpha**10)
        elif (m==2):
            return (alpha**14/126.0)
        elif (m==3):
            return 6e-6*alpha**18
        elif (m==4):
            return 2e-9*alpha**22
        elif (m==5):
            return 4e-13*alpha**26
        else:
            raise ValueError("Azimuthal index of power_gw() not consistent with max azi_gw")
    def strain_sph_harm(self, m, alpha, abh):
        omegaGW = 2.0*self.omega_real(m, alpha, abh, 0)
        # only considering dominant l = |m| = 2 mode of radiation
        h22 = -2.0*np.sqrt(2.0*np.pi*self.power_gw(m, alpha, abh))/omegaGW
        return np.array([h22])
