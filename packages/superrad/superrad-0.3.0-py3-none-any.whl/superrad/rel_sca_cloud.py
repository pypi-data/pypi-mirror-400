from .cloud_model import CloudModel 
from scipy import interpolate
from scipy import optimize
import numpy as np 
from cmath import sqrt
from pathlib import Path

class RelScalar(CloudModel):
    """
    Relativistic (alpha~1) model for scalar bosons

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    m is azimuthal number of cloud
    """
    def __init__(self,nonrel_freq_shift = False):
        """Caching tabulated and fit data"""

        """ 
        m=1 modes: 
        """
        m1_data = np.load(Path(__file__).parent.joinpath('data/m1_sc_mds.npz'))
        m1_wr = m1_data['wr'].flatten()
        m1_wi = m1_data['wi'].flatten()
        m1_a = m1_data['a'].flatten()
        m1_y = m1_data['y'].flatten()
        self._f1wr = interpolate.LinearNDInterpolator(list(zip(m1_y,m1_a)),m1_wr)
        self._f1wi = interpolate.LinearNDInterpolator(list(zip(m1_y,m1_a)),m1_wi)
        #If _nonrel_freq_shift  is true, always use non-relativistic cloud mass dependent frequency shift
        self._nonrel_freq_shift = nonrel_freq_shift
        
        """
        shift data (only for m=1):
        """
        if self._nonrel_freq_shift==False:
            shift_data = np.load(Path(__file__).parent.joinpath('data/scalar_freqshift_m1_interp.npz'))
            alpha = shift_data['alpha'].flatten()
            lin_shift = shift_data['lin_shift'].flatten()
            quad_shift = shift_data['quad_shift'].flatten()
            self._max_numeric_alpha = 0.57
            self._lin_shift = interpolate.interp1d(alpha, lin_shift, kind='cubic')
            self._quad_shift = interpolate.interp1d(alpha, quad_shift, kind='cubic')
            self._min_numericalfit_alpha = 0.23
            self._min_numericalfitandinterp_alpha = 0.200067
            self._max_numeric_alpha = max(alpha)

        """ 
        m=2 modes: 
        """
        m2_data = np.load(Path(__file__).parent.joinpath('data/m2_sc_mds.npz'))
        m2_wr = m2_data['wr'].flatten()
        m2_wi = m2_data['wi'].flatten()
        m2_a = m2_data['a'].flatten()
        m2_y = m2_data['y'].flatten()
        self._f2wr = interpolate.LinearNDInterpolator(list(zip(m2_y,m2_a)),m2_wr)
        self._f2wi = interpolate.LinearNDInterpolator(list(zip(m2_y,m2_a)),m2_wi)

        """
        Fit coefficients
        """
        fit_data = np.load(Path(__file__).parent.joinpath('data/sc_fits.npz'))
        self._amat1 = fit_data['amat1']
        self._bmat1 = fit_data['bmat1']
        self._cmat1 = fit_data['cmat1']
        self._amat2 = fit_data['amat2']
        self._bmat2 = fit_data['bmat2']
        self._cmat2 = fit_data['cmat2']

        """
        Radiation data
        """
        sat_flux_data = np.load(Path(__file__).parent.joinpath('data/sc_sat_gw.npz'))
        m1_flux = sat_flux_data['m1_flux']
        m1_mu = sat_flux_data['m1_mu']
        m1_Z2r = sat_flux_data['m1_z2r']
        m1_Z2i = sat_flux_data['m1_z2i']
        m1_Z3r = sat_flux_data['m1_z3r']
        m1_Z3i = sat_flux_data['m1_z3i']
        m2_flux = sat_flux_data['m2_flux']
        m2_mu = sat_flux_data['m2_mu']
        m2_Z4r = sat_flux_data['m2_z4r']
        m2_Z4i = sat_flux_data['m2_z4i']
        m2_Z5r = sat_flux_data['m2_z5r']
        m2_Z5i = sat_flux_data['m2_z5i']

        self._pwm1 = interpolate.interp1d(m1_mu, m1_flux, kind='cubic')
        self._z2rm1 = interpolate.interp1d(m1_mu, m1_Z2r, kind='cubic')
        self._z2im1 = interpolate.interp1d(m1_mu, m1_Z2i, kind='cubic')
        self._z3rm1 = interpolate.interp1d(m1_mu, m1_Z3r, kind='cubic')
        self._z3im1 = interpolate.interp1d(m1_mu, m1_Z3i, kind='cubic')
        self._pwm2 = interpolate.interp1d(m2_mu, m2_flux, kind='cubic')
        self._z4rm2 = interpolate.interp1d(m2_mu, m2_Z4r, kind='cubic')
        self._z4im2 = interpolate.interp1d(m2_mu, m2_Z4i, kind='cubic')
        self._z5rm2 = interpolate.interp1d(m2_mu, m2_Z5r, kind='cubic')
        self._z5im2 = interpolate.interp1d(m2_mu, m2_Z5i, kind='cubic')

        """
        Fit numbers from data
        """
        self._nonrel_freq_spincomponent_m1 = 0.0028391854462700
        self._nonrel_freq_spincomponent_m2 = 0.0024403837275569847
        self._omegai_nonrel_alpha12fac_m2 = -1.1948426572069112e11
        self._omegai_nonrel_alpha13fac_m2 = 2.609027546773062e12
        self._gwpower_nonrel_m1_a14 = 0.0109289473739731
        self._gwpower_nonrel_m1_a15 = -0.0290105840870259
        self._gwpower_nonrel_m2_a18 = 6.46575425669374e-7
        self._gwpower_nonrel_m2_a19 = -1.12205283686066e-6
        self._aswitchval = 0.6

        self._freqshift_nonrel_extrapfromreldata_Mcalpha4 = -0.03370322
        self._freqshift_nonrel_extrapfromreldata_Mcalpha5 = -0.18433376 
        self._freqshift_nonrel_extrapfromreldata_Mcalpha6 = -0.2922884
        self._freqshift_nonrel_extrapfromreldata_Mc2alpha4 = -0.35184631
        self._freqshift_nonrel_extrapfromreldata_Mc2alpha5 = 0.13244306
        self._freqshift_nonrel_extrapfromreldata_Mc2alpha6 = 0
        self._freqshift_highalpha_extrapfromreldata_Mcalpha4 = -0.70667268
        self._freqshift_highalpha_extrapfromreldata_Mcalpha5 = 3.30927045
        self._freqshift_highalpha_extrapfromreldata_Mcalpha6 = -4.92869613
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha4 = 1.0725927  
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha5 = -3.44415853 
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha6 = 0

    def boson_spin(self):
        """Spin of boson"""
        return 0
    def max_azi_num(self):
        """Maximum azimuthal number the model is defined for"""
        return 2
    def max_spin(self):
        """Maximum spin the model is defined for"""
        return 0.995 
    def omega_real(self, m, alpha, abh, Mcloud):
        """Returns real frequency of cloud oscillation"""
        yl, alphamax, Oh = self._y(m, alpha, abh)
        dwr = self._deltaomega(m, alpha, abh, Mcloud)*Mcloud
        if (m==1):
            if (alpha>=0.05 and abh>=self._aswitch(m)):
                wr = alpha*self._f1wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha too large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/8.0-17.0*alpha**4/128.0+abh*alpha**5/12.0)
                wr += alpha*self._nonrel_freq_spincomponent_m1*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat1[p-6,q]
            return wr+dwr
        elif (m==2):
            if (alpha>=0.25 and abh>=self._aswitch(m)):
                wr = alpha*self._f2wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha too large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/18.0-23.0*alpha**4/1080.0+4.0*abh*alpha**5/405.0)
                wr += alpha*self._nonrel_freq_spincomponent_m2*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat2[p-6,q]
            return wr+dwr
        else:
            raise ValueError("Azimuthal index too large")
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        """Returns derivative of real frequency of cloud w.r.t. cloud mass"""
        return self._lin_shift_withextrap(m,alpha,abh) + 2* self._quad_shift_withextrap(m,alpha,abh) * Mcloud
    def omega_imag(self, m, alpha, abh):
        """Returns imaginary frequency, 
           i.e. growth rate of superradiant instability"""
        yl, alphamax, Oh = self._y(m, alpha, abh)
        wr = self.omega_real(m, alpha, abh, 0)
        if (m==1):
            if (alpha>=0.05 and abh>=self._aswitch(m)):
                return -np.exp(self._f1wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                glm = 1-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                for p in range(1, 4):
                    for q in range(0, 4):
                        wi += alpha**p*(abh**(q+1)*self._bmat1[q,p-1]+self._cmat1[q,p-1]*(1.0-abh**2)**(q/2.0))
                wi *= -2.0*(1.0+np.sqrt(1.0-abh**2))*glm*alpha**9*(wr-m*Oh)/48.0
                return wi
        elif (m==2):
            if (alpha>=0.25 and abh>=self._aswitch(m)):
                return -np.exp(self._f2wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                glm = 1-abh**2+(2.0*abh-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                glm *= 4.0*(1-abh**2)+(2.0*abh-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                wi += self._omegai_nonrel_alpha12fac_m2*alpha**12+self._omegai_nonrel_alpha13fac_m2*alpha**13
                for p in range(12, 23):
                    wi += self._cmat2[p-12]*alpha**p*(1.0-abh**2)**0.5
                    for q in range(0, 3):
                        wi += alpha**(p+2)*abh**q*self._bmat2[q,p-12]
                wi *= -2.0*(1.0+np.sqrt(1.0-abh**2))*glm*alpha**13*(wr-m*Oh)*4.0/885735.0
                return wi
        else:
            raise ValueError("Azimuthal index too large")
    def power_gw(self, m, alpha, abh):
        """Returns gravitational wave power, scaled to Mcloud=1 
        Using: omega_R(Mcloud=0), valid only at saturation"""
        if (m==1):
            if (alpha<0.2):
                return self._gwpower_nonrel_m1_a14*alpha**14+self._gwpower_nonrel_m1_a15*alpha**15
            else:
                return self._pwm1(alpha)
        elif (m==2):
            if (alpha<0.34):
                return self._gwpower_nonrel_m2_a18*alpha**18+self._gwpower_nonrel_m2_a19*alpha**19
            else:
                return self._pwm2(alpha)
        else:
            raise ValueError("Azimuthal index too large")
    def strain_sph_harm(self, m, alpha, abh):
        """Returns e^{iwt}R h^{ell 2m} (-2-weighted spherical harmonic components)"""
        spsat = self._spinsat(m, alpha)
        wr = 2.0*self.omega_real(m, alpha, spsat, 0)
        if (m==1):
            if (alpha<0.2):
                z2abs = 2.0*np.pi*np.sqrt(wr**2*self.power_gw(m, alpha, spsat))
                return 2.0*np.array([z2abs,0])/(np.sqrt(2.0*np.pi)*wr**2)
            else:
                z2 = self._z2rm1(alpha)+1j*self._z2im1(alpha)
                z3 = self._z3rm1(alpha)+1j*self._z3im1(alpha)
                return -2.0*np.array([z2, z3])/(np.sqrt(2.0*np.pi)*wr**2)
        elif (m==2):
            if (alpha<0.34):
                z4abs = 2.0*np.pi*np.sqrt(wr**2*self.power_gw(m, alpha, spsat))
                return 2.0*np.array([z4abs,0])/(np.sqrt(2.0*np.pi)*wr**2)
            else:
                z4 = self._z4rm2(alpha)+1j*self._z4im2(alpha)
                z5 = self._z5rm2(alpha)+1j*self._z5im2(alpha)
                return -2.0*np.array([z4, z5])/(np.sqrt(2.0*np.pi)*wr**2)
        else:
            raise ValueError("Azimuthal index too large")
    def _aswitch(self, m):
        return self._aswitchval
    def _maxalphaInterp(self, m, alpha):
        """Returns True if alpha is below the saturation-alpha for each m at abh=aswitch(m)"""       
        if (m==1):
            return alpha<0.18
        elif (m==2):
            return alpha<0.4
        else:
            raise ValueError("Azimuthal index too large") 
    def _y(self, m, alpha, abh, beta=0.9):
        """Returns utility parameter y, approximate maximal alpha, horizon frequency"""
        if (m==1):
            alpha0 = 0.05
        else:
            alpha0 = 0.25
        Oh = 0.5*abh/(1.0+np.sqrt(1.0-abh**2))
        temp = 9.0*m*(m+1)**2*Oh*beta**2+sqrt(81*m**2*(1+m)**4*Oh**2*beta**4-24*(1+m)**6*beta**6)
        alphamaxC = ((3**(1.0/3.0)+1j*3**(5.0/6.0))*temp**(2.0/3.0)-4.0*(-3.0)**(2.0/3.0)*(m+1)**2*beta**2)/(6.0*temp**(1.0/3.0)*beta)
        alphamax = alphamaxC.real
        yl = (alpha-alpha0)/(alphamax-alpha0)
        return yl, alphamax, Oh
    def _deltaomega(self,m,alpha,abh,Mcloud):
        """Returns the frequency shift due to self-gravity divided by cloud mass (to give a sensible result for Mcloud -> 0)"""
        return self._lin_shift_withextrap(m,alpha,abh) + self._quad_shift_withextrap(m,alpha,abh) * Mcloud
    def _alphasat(self, m, abh):
        """Bisection to find saturation point, returns alpha at saturation"""
        yh, amaxh, Ohh = self._y(m, 0, abh)
        yl, amaxl, Ohl = self._y(m, 0, abh, 1.1)
        def _sat(al):
            satout = self.omega_real(m, al, abh, 0)-m*0.5*abh/(1.0+np.sqrt(1.0-abh**2))
            if (np.isnan(satout)): satout = 1e10
            return satout
        return optimize.bisect(_sat, amaxl, amaxh)
    def _spinsat(self, m, al,mc=0):
        """Bisection to find saturation point, returns spin at saturation"""
        mcin = mc
        def _sat(abh):
            satout = self.omega_real(m, al, abh, mcin)-m*0.5*abh/(1.0+np.sqrt(1.0-abh**2))
            if (np.isnan(satout)): satout = 1e10
            return satout
        return optimize.bisect(_sat, self.max_spin(), 0)    
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
    def _lin_shift_withextrap(self, m, alpha, abh):
        if (m==1 and not self._nonrel_freq_shift):
            non_rel = 2.0*self._shift_factor(m)*alpha**3
            extrap_ha = non_rel + self._freqshift_highalpha_extrapfromreldata_Mcalpha4* alpha**4 + self._freqshift_highalpha_extrapfromreldata_Mcalpha5*alpha**5 + self._freqshift_highalpha_extrapfromreldata_Mcalpha6 *alpha **6
            extrap = non_rel + self._freqshift_nonrel_extrapfromreldata_Mcalpha4* alpha**4 + self._freqshift_nonrel_extrapfromreldata_Mcalpha5*alpha**5 + self._freqshift_nonrel_extrapfromreldata_Mcalpha6 *alpha **6
            if alpha >self._min_numericalfitandinterp_alpha and alpha<=self._max_numeric_alpha:
                    if alpha>0.23:
                        return self._lin_shift(alpha)
                    else:
                        return self._lin_shift(alpha) * (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha) + extrap * (1.0 - (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha))
            elif alpha <=self._min_numericalfitandinterp_alpha:
                return extrap
            elif alpha >self._max_numeric_alpha:
                return extrap_ha
        else:
            return 2.0*self._shift_factor(m)*alpha**3
    def _quad_shift_withextrap(self, m, alpha, abh):
        if (m==1 and not self._nonrel_freq_shift):
            extrap_ha =  self._freqshift_highalpha_extrapfromreldata_Mc2alpha4* alpha**4 + self._freqshift_highalpha_extrapfromreldata_Mc2alpha5*alpha**5 + self._freqshift_highalpha_extrapfromreldata_Mc2alpha6*alpha**6
            extrap =  self._freqshift_nonrel_extrapfromreldata_Mc2alpha4* alpha**4 + self._freqshift_nonrel_extrapfromreldata_Mc2alpha5*alpha**5 + self._freqshift_nonrel_extrapfromreldata_Mc2alpha6*alpha **6
            if alpha >=self._min_numericalfitandinterp_alpha and alpha<=self._max_numeric_alpha:
                    if alpha>0.23:
                        return self._quad_shift(alpha)
                    else:
                        return self._quad_shift(alpha) * (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha) + extrap * (1.0 - (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha))
            elif alpha <self._min_numericalfitandinterp_alpha:
                return extrap
            elif alpha >self._max_numeric_alpha:
                return extrap_ha
        else: 
            return 0


