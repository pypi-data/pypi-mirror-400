from .cloud_model import CloudModel 
from scipy import interpolate
from scipy import optimize
import numpy as np 
from cmath import sqrt
from pathlib import Path

class RelVector(CloudModel):
    """
    Relativistic (alpha~1) model for vector bosons

    All in inputs are in units where black hole mass=1
    alpha is boson mass (times black hole mass)
    abh is black hole dimensionless spin
    Mcloud is boson cloud mass (as fraction of black hole mass) 
    m is azimuthal number of cloud
    """
    def __init__(self, nonrel_freq_shift=False, no_radiation=False):
        """Caching tabulated and fit data"""
        self._no_radiation = no_radiation
        self._nonrel_freq_shift = nonrel_freq_shift

        """ 
        m=1 modes: 
        """
        m1_data = np.load(Path(__file__).parent.joinpath('data/m1_pr_mds.npz'))
        m1_wr = m1_data['wr'].flatten()
        m1_wi = m1_data['wi'].flatten()
        m1_a = m1_data['a'].flatten()
        m1_y = m1_data['y'].flatten()
        self._f1wr = interpolate.LinearNDInterpolator(list(zip(m1_y,m1_a)),m1_wr)
        self._f1wi = interpolate.LinearNDInterpolator(list(zip(m1_y,m1_a)),m1_wi)
        #If _nonrel_freq_shift  is true, always use non-relativistic cloud mass dependent frequency shift

        """
        shift data (only for m=1):
        """
        if self._nonrel_freq_shift==False:
            shift_data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_m1_interp.npz'))
            alpha = shift_data['alpha'].flatten()
            lin_shift = shift_data['lin_shift'].flatten()
            quad_shift = shift_data['quad_shift'].flatten()
            self._max_numeric_alpha = 0.57
            self._lin_shift = interpolate.interp1d(alpha, lin_shift, kind='cubic')
            self._quad_shift = interpolate.interp1d(alpha, quad_shift, kind='cubic')
            self._min_numericalfit_alpha = 0.1
            self._min_numericalfitandinterp_alpha = 0.09
            self._max_numericalfitandinterp_alpha = max(alpha)


        """
        m=2 modes
        """
        m2_data = np.load(Path(__file__).parent.joinpath('data/m2_pr_mds.npz'))
        m2_wr = m2_data['wr'].flatten()
        m2_wi = m2_data['wi'].flatten()
        m2_a = m2_data['a'].flatten()
        m2_y = m2_data['y'].flatten()
        self._f2wr = interpolate.LinearNDInterpolator(list(zip(m2_y,m2_a)),m2_wr)
        self._f2wi = interpolate.LinearNDInterpolator(list(zip(m2_y,m2_a)),m2_wi)

        if (self._no_radiation==True):
            """
            m=3 modes (zeroth overtone)
            """
            m3_data = np.load(Path(__file__).parent.joinpath('data/m3_pr_mds.npz'))
            m3_wr = m3_data['wr'].flatten()
            m3_wi = m3_data['wi'].flatten()
            m3_a = m3_data['a'].flatten()
            m3_y = m3_data['y'].flatten()
            self._f3wr = interpolate.LinearNDInterpolator(list(zip(m3_y,m3_a)),m3_wr)
            self._f3wi = interpolate.LinearNDInterpolator(list(zip(m3_y,m3_a)),m3_wi)
    
            """
            m=4 modes (zeroth overtone)
            """
            m4_data = np.load(Path(__file__).parent.joinpath('data/m4_pr_mds.npz'))
            m4_wr = m4_data['wr'].flatten()
            m4_wi = m4_data['wi'].flatten()
            m4_a = m4_data['a'].flatten()
            m4_y = m4_data['y'].flatten()
            self._f4wr = interpolate.LinearNDInterpolator(list(zip(m4_y,m4_a)),m4_wr)
            self._f4wi = interpolate.LinearNDInterpolator(list(zip(m4_y,m4_a)),m4_wi)
    
            """
            m=5 modes (zeroth overtone)
            """
            m5_data = np.load(Path(__file__).parent.joinpath('data/m5_pr_mds.npz'))
            m5_wr = m5_data['wr'].flatten()
            m5_wi = m5_data['wi'].flatten()
            m5_a = m5_data['a'].flatten()
            m5_y = m5_data['y'].flatten()
            self._f5wr = interpolate.LinearNDInterpolator(list(zip(m5_y,m5_a)),m5_wr)
            self._f5wi = interpolate.LinearNDInterpolator(list(zip(m5_y,m5_a)),m5_wi)

        """
        Fit coefficients
        """
        fit_data = np.load(Path(__file__).parent.joinpath('data/pr_fits.npz'))
        self._amat1 = fit_data['amat1']
        self._bmat1 = fit_data['bmat1']
        self._cmat1 = fit_data['cmat1']
        self._amat2 = fit_data['amat2']
        self._bmat2 = fit_data['bmat2']
        self._cmat2 = fit_data['cmat2']
        if (self._no_radiation==True):
            fit_data_higher_m = np.load(Path(__file__).parent.joinpath('data/pr_fits_higher_m.npz'))
            self._amat3 = fit_data_higher_m['amat3']
            self._bmat3 = fit_data_higher_m['bmat3']
            self._cmat3 = fit_data_higher_m['cmat3']
            self._amat4 = fit_data_higher_m['amat4']
            self._bmat4 = fit_data_higher_m['bmat4']
            self._cmat4 = fit_data_higher_m['cmat4']
            self._amat5 = fit_data_higher_m['amat5']
            self._bmat5 = fit_data_higher_m['bmat5']
            self._cmat5 = fit_data_higher_m['cmat5']

        """
        Radiation data
        """
        sat_flux_data = np.load(Path(__file__).parent.joinpath('data/pr_sat_gw.npz'))
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
        self._pwm2 = interpolate.interp1d(m2_mu, m2_flux, kind='cubic')
        self._z2rm1 = interpolate.interp1d(m1_mu, m1_Z2r, kind='cubic')
        self._z2im1 = interpolate.interp1d(m1_mu, m1_Z2i, kind='cubic')
        self._z3rm1 = interpolate.interp1d(m1_mu, m1_Z3r, kind='cubic')
        self._z3im1 = interpolate.interp1d(m1_mu, m1_Z3i, kind='cubic')
        self._z4rm2 = interpolate.interp1d(m2_mu, m2_Z4r, kind='cubic')
        self._z4im2 = interpolate.interp1d(m2_mu, m2_Z4i, kind='cubic')
        self._z5rm2 = interpolate.interp1d(m2_mu, m2_Z5r, kind='cubic')
        self._z5im2 = interpolate.interp1d(m2_mu, m2_Z5i, kind='cubic')

        """ 
        Fit numbers from data
        """
        self._freqshift_nonrel_extrapfromreldata_Mcalpha4 = -0.04481897
        self._freqshift_nonrel_extrapfromreldata_Mcalpha5 = -1.94718171
        self._freqshift_nonrel_extrapfromreldata_Mcalpha6 = -3.27331145
        self._freqshift_nonrel_extrapfromreldata_Mc2alpha4 = -2.50867495
        self._freqshift_nonrel_extrapfromreldata_Mc2alpha5 = 8.26894214
        self._freqshift_highalpha_extrapfromreldata_Mcalpha4 = -2.76544476
        self._freqshift_highalpha_extrapfromreldata_Mcalpha5 = 5.77381238
        self._freqshift_highalpha_extrapfromreldata_Mcalpha6 = -4.056506
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha4 = -5.25668187
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha5 = 8.73330989
        self._freqshift_highalpha_extrapfromreldata_Mc2alpha6 = 0

    def boson_spin(self):
        """Spin of boson"""
        return 1
    def max_azi_num(self):
        """Maximum azimuthal number the model is defined for"""
        if (self._no_radiation==True): return 5
        return 2
    def max_spin(self):
        """Maximum spin the model is defined for"""
        return 0.995
    def omega_real(self, m, alpha, abh, Mcloud):
        """Returns real frequency of cloud oscillation"""
        yl, alphamax, Oh = self._y(m, alpha, abh)
        dwr = self._deltaomega(m, alpha, abh, Mcloud)
        if (m==1):
            if (alpha>=0.05 and abh>=self._aswitch(m)):
                wr = alpha*self._f1wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha to large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/2.0-35.0*alpha**4/24.0+8.0*alpha**5*abh/3.0)
                wr += alpha*0.9934826313642444*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat1[p-6,q]
            return wr+Mcloud*dwr
        elif (m==2):
            if (alpha>=0.25 and abh>=self._aswitch(m)):
                wr = alpha*self._f2wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha to large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/8.0-143.0*alpha**4/1920.0+alpha**5*abh/15.0)
                wr += alpha*0.03298155184748759*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat2[p-6,q]
            return wr+Mcloud*dwr
        elif (m==3):
            if (alpha>=0.35 and abh>=self._aswitch(m)):
                wr = alpha*self._f3wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha to large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/18.0-323.0*alpha**4/22680.0+8.0*alpha**5*abh/945.0)
                wr += alpha*(-0.0499152)*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat3[p-6,q]
            return wr+Mcloud*dwr
        elif (m==4):
            if (alpha>=0.5 and abh>=self._aswitch(m)):
                wr = alpha*self._f4wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha to large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/32.0-575.0*alpha**4/129024.0+alpha**5*abh/504.0)
                wr += alpha*(0.0108867)*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat4[p-6,q]
            return wr+Mcloud*dwr
        elif (m==5):
            if (alpha>=0.6 and abh>=self._aswitch(m)):
                wr = alpha*self._f5wr(yl, abh)
            else:
                # Ensures output fails sup. condition if alpha to large
                if (not(self._maxalphaInterp(m, alpha))):
                    return np.nan
                wr = alpha*(1.0-alpha**2/50.0-899.0*alpha**4/495000.0+8.0*alpha**5*abh/12375.0)
                wr += alpha*(-0.00835658)*alpha**5*(abh*np.sqrt(1-abh**2)-abh)
                for p in range(6, 9):
                    for q in range(0, 4):
                        wr += alpha**(p+1)*(1.0-abh**2)**(q/2.0)*self._amat5[p-6,q]
            return wr+Mcloud*dwr
        else:
            raise ValueError("Azimuthal index too large")
    def domegar_dmc(self, m, alpha, abh, Mcloud):
        """Returns derivative of real frequency of cloud w.r.t. cloud mass"""
        return self._lin_shift_withextrap(m,alpha,abh) * Mcloud**0 + 2* self._quad_shift_withextrap(m,alpha,abh) * Mcloud**1
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
                fm = 1-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                for p in range(1, 11):
                    for q in range(0, 2):
                        wi += alpha**p*(abh**(q+1)*self._bmat1[q,p-1]+self._cmat1[q,p-1]*(1.0-abh**2)**(q/2.0))
                wi *= -4.0*(1.0+np.sqrt(1.0-abh**2))*fm*alpha**7*(wr-m*Oh)
                return wi
        elif (m==2):
            if (alpha>=0.25 and abh>=self._aswitch(m)):
                return -np.exp(self._f2wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                for p in range(5, 11):
                    for q in range(0, 2):
                        wi += alpha**p*(abh**(q+1)*self._bmat2[q,p-5]+self._cmat2[q,p-5]*(1.0-abh**2)**(q/2.0))
                fm = 1.0-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 4.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                wi *= fm*(1.0+np.sqrt(1.0-abh**2))*alpha**11*(-wr+m*Oh)/864.0
                return wi
        elif (m==3):
            if (alpha>=0.35 and abh>=self._aswitch(m)):
                return -np.exp(self._f3wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                for p in range(8, 17):
                    for q in range(0, 3):
                        wi += alpha**p*(abh**(q+1)*self._bmat3[q,p-8]+self._cmat3[q,p-8]*(1.0-abh**2)**(q/2.0))
                fm = 1.0-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 4.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 9.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                wi *= fm*(1.0+np.sqrt(1.0-abh**2))*alpha**15*(-wr+m*Oh)*8/199290375.0
                return wi
        elif (m==4):
            if (alpha>=0.5 and abh>=self._aswitch(m)):
                return -np.exp(self._f4wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                for p in range(10, 19):
                    for q in range(0, 3):
                        wi += alpha**p*(abh**(q+1)*self._bmat4[q,p-10]+self._cmat4[q,p-10]*(1.0-abh**2)**(q/2.0))
                fm = 1.0-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 4.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 9.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 16.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                wi *= fm*(1.0+np.sqrt(1.0-abh**2))*alpha**19*(-wr+m*Oh)*2.74607e-13
                return wi
        elif (m==5):
            if (alpha>=0.6 and abh>=self._aswitch(m)):
                return -np.exp(self._f5wi(yl, abh))*(wr-m*Oh)
            else:
                wi = 1.0
                for p in range(18, 29):
                    for q in range(0, 3):
                        wi += alpha**p*(abh**(q+1)*self._bmat5[q,p-18]+self._cmat5[q,p-18]*(1.0-abh**2)**(q/2.0))
                wi += alpha*(-1.7052*abh**3+5.76663*(1-abh**2)**1.5)
                fm = 1.0-abh**2+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 4.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 9.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 16.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                fm *= 25.0*(1.0-abh**2)+(abh*m-2.0*wr*(1.0+np.sqrt(1.0-abh**2)))**2
                wi *= fm*(1.0+np.sqrt(1.0-abh**2))*alpha**23*(-wr+m*Oh)*5.17718e-19
                return wi
        else:
            raise ValueError("Azimuthal index too large")
    def power_gw(self, m, alpha, abh):
        """Returns gravitational wave power, scaled to Mcloud=1 
        Using: omega_R(Mcloud=0), valid only at saturation"""
        if (m==1):
            if (alpha<0.17):
                a10 = 23.6070141940415
                a11 = -115.398015735204
                a12 = 222.729191099650
                return a10*alpha**10+a11*alpha**11+a12*alpha**12
            else:
                return self._pwm1(alpha)
        elif (m==2):
            if (alpha<0.45):
                a14 = 0.00174831340006483
                a15 = -0.00676143664936868
                a16 = 0.00696518854011634
                return a14*alpha**14+a15*alpha**15+a16*alpha**16
            else:
                return self._pwm2(alpha) 
        else:
            raise ValueError("Azimuthal index too large")
    def strain_sph_harm(self, m, alpha, abh):
        """Returns e^{iwt}R h^{ell 2m} (-2-weighted spherical harmonic components)"""
        spsat = self._spinsat(m, alpha)
        wr = 2.0*self.omega_real(m, alpha, spsat, 0)
        if (m==1):
            if (alpha<0.17):
                z2abs = 2.0*np.pi*np.sqrt(wr**2*self.power_gw(m, alpha, spsat))
                return 2.0*np.array([z2abs,0])/(np.sqrt(2.0*np.pi)*wr**2)
            else:
                z2 = self._z2rm1(alpha)+1j*self._z2im1(alpha)
                z3 = self._z3rm1(alpha)+1j*self._z3im1(alpha)
                return -2.0*np.array([z2, z3])/(np.sqrt(2.0*np.pi)*wr**2)
        elif (m==2):
            if (alpha<0.45):
                z4abs = 2.0*np.pi*np.sqrt(wr**2*self.power_gw(m, alpha, spsat))
                return 2.0*np.array([z4abs,0])/(np.sqrt(2.0*np.pi)*wr**2)
            else:
                z4 = self._z4rm2(alpha)+1j*self._z4im2(alpha)
                z5 = self._z5rm2(alpha)+1j*self._z5im2(alpha)
                return -2.0*np.array([z4, z5])/(np.sqrt(2.0*np.pi)*wr**2)
        else:
            raise ValueError("Azimuthal index too large")
    def _aswitch(self, m):
        return 0.6
    def _maxalphaInterp(self, m, alpha):
        """Returns True if alpha is below the saturation-alpha for each m at abh=aswitch(m)"""
        if (m==1):
            return alpha<0.18
        elif (m==2):
            return alpha<0.35
        elif (m==3):
            return alpha<0.52
        elif (m==4):
            return alpha<0.68
        elif (m==5):
            return alpha<0.86
        else:
            raise ValueError("Azimuthal index too large")
    def _y(self, m, alpha, abh, beta=0.91):
        """Returns utility parameter y, approximate maximal alpha, horizon frequency"""
        if (m==1):
            alpha0 = 0.05
        elif (m==2):
            alpha0 = 0.25
        elif (m==3):
            alpha0 = 0.35
        elif (m==4):
            alpha0 = 0.5
        else:
            alpha0 = 0.6
        Oh = 0.5*abh/(1.0+np.sqrt(1.0-abh**2))
        temp = 9.0*m**3*Oh*beta**2+sqrt(3*m**6*beta**4*(27.0*Oh**2-8.0*beta**2))
        alphamaxC = (-3j+sqrt(3.0))*m**2*beta/(3.0**(5.0/6.0)*temp**(1.0/3.0))\
                        +(1.0+sqrt(3.0)*1j)*temp**(1.0/3.0)/(2.0*3.0**(2.0/3.0)*beta)
        alphamax = alphamaxC.real
        yl = (alpha-alpha0)/(alphamax-alpha0)
        return yl, alphamax, Oh
    def _deltaomega(self,m,alpha,abh,Mcloud):
        """Returns the frequency shift due to self-gravity divided by cloud mass (to give a sensible result for Mcloud -> 0)"""
        return self._lin_shift_withextrap(m,alpha,abh) * Mcloud**0 + self._quad_shift_withextrap(m,alpha,abh) * Mcloud**1
    def _alphasat(self, m, abh):
        """Bisection to find saturation point, returns alpha at saturation"""
        yh, amaxh, Ohh = self._y(m, 0, abh)
        yl, amaxl, Ohl = self._y(m, 0, abh, 1.0)
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
        coeffs = [-(5/16), -(93/1024), -(793/18432), -(26333/1048576), -(43191/
  2621440), -(1172755/100663296), -(28539857/3288334336), -(
  1846943453/274877906944), -(14911085359/2783138807808), -(
  240416274739/54975581388800), -(1936010885087/532163627843584), -(
  62306843256889/20266198323167232), -(500960136802799/
  190277084256403456), -(8051112929645937/3530822107858468864), -(
  21555352563374699/10808639105689190400)]
        return coeffs[m-1]
    def _lin_shift_withextrap(self, m, alpha, abh):
        if (m==1 and not self._nonrel_freq_shift):
            non_rel = 2.0*self._shift_factor(m)*alpha**3
            extrap_ha = non_rel + self._freqshift_highalpha_extrapfromreldata_Mcalpha4* alpha**4 + self._freqshift_highalpha_extrapfromreldata_Mcalpha5*alpha**5 + self._freqshift_highalpha_extrapfromreldata_Mcalpha6 *alpha **6
            extrap = non_rel + self._freqshift_nonrel_extrapfromreldata_Mcalpha4* alpha**4 + self._freqshift_nonrel_extrapfromreldata_Mcalpha5*alpha**5 + self._freqshift_nonrel_extrapfromreldata_Mcalpha6 *alpha **6
            if alpha >=self._min_numericalfitandinterp_alpha and alpha<=self._max_numeric_alpha:
                if alpha>0.1:
                    return self._lin_shift(alpha)
                else:
                    return self._lin_shift(alpha) * (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha) + extrap * (1.0 - (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha))
            elif alpha <self._min_numericalfitandinterp_alpha:
                return extrap
            elif self._max_numeric_alpha <alpha <self._max_numericalfitandinterp_alpha:
                return self._lin_shift(alpha) * (alpha - self._max_numericalfitandinterp_alpha)/(self._max_numeric_alpha-self._max_numericalfitandinterp_alpha) + extrap_ha * (1.0 - (alpha - self._max_numericalfitandinterp_alpha)/(self._max_numeric_alpha-self._max_numericalfitandinterp_alpha))
            elif alpha >=self._max_numericalfitandinterp_alpha:
                return extrap_ha
        else:
            return 2.0*self._shift_factor(m)*alpha**3
    def _quad_shift_withextrap(self, m, alpha, abh):
        if (m==1 and not self._nonrel_freq_shift):
            extrap =  self._freqshift_nonrel_extrapfromreldata_Mc2alpha4* alpha**4 + self._freqshift_nonrel_extrapfromreldata_Mc2alpha5*alpha**5
            extrap_ha =  self._freqshift_highalpha_extrapfromreldata_Mc2alpha4* alpha**4 + self._freqshift_highalpha_extrapfromreldata_Mc2alpha5*alpha**5 + self._freqshift_highalpha_extrapfromreldata_Mc2alpha6*alpha**6
            if alpha >=self._min_numericalfitandinterp_alpha and alpha<=self._max_numeric_alpha:
                if alpha>0.1:
                    return self._quad_shift(alpha)
                else:
                    return self._quad_shift(alpha) * (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha) + extrap * (1.0 - (alpha - self._min_numericalfitandinterp_alpha)/(self._min_numericalfit_alpha - self._min_numericalfitandinterp_alpha))
            elif alpha<self._min_numericalfitandinterp_alpha:
                return extrap
            elif alpha>self._max_numeric_alpha:
                return extrap_ha
        else:
            return 0


