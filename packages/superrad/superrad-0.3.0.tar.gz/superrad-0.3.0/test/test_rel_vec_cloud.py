import unittest
import numpy as np
import superrad.rel_vec_cloud as rvc
from matplotlib import pyplot as plt
from pathlib import Path

class TestRelVec(unittest.TestCase):

    @classmethod
    def setUpClass(self):    
        """Sets up the vector cloud model class tested here"""
        # PLotting issues if error is found
        self.errpltglb = True
        self._tol = 1e-9

        # Setting up cloud
        self.rv_testfield = rvc.RelVector(nonrel_freq_shift = True)
        self.rv_higher_m = rvc.RelVector(no_radiation = True)
        self.rv = rvc.RelVector()
        self.mmax = self.rv.max_azi_num()
        self.maxspin = self.rv.max_spin()
        self.spi = [0.5*self.maxspin, 0.6*self.maxspin, 0.8*self.maxspin, 1.0*self.maxspin]
        self.alp = [0.001, 0.01, 0.1]

        # Modes data
        self.m1wr99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_wr_a0.99.dat'))
        self.m1wi99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_wi_a0.99.dat'))
        self.m2wr99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_wr_a0.99.dat'))
        self.m2wi99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_wi_a0.99.dat'))
        self.m1wr4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_wr_a0.4.dat'))
        self.m1wi4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_wi_a0.4.dat'))
        self.m2wr4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_wr_a0.4.dat'))
        self.m2wi4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_wi_a0.4.dat'))
        self.v2_shift = np.loadtxt(Path(__file__).parent.joinpath('./testdata/vector_freqshift_v2_m1.dat'), unpack=True)
        self.nr_shift_data = np.loadtxt(Path(__file__).parent.joinpath('./testdata/vector_freqshift_test_m1.dat'), unpack=True)

        # GW emission data
        self.m1pw = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_power_gw.dat'))
        self.m2pw = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_power_gw.dat'))
        self.m1strain99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m1_strain_a0.99.dat'))
        self.m2strain99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_m2_strain_a0.99.dat'))

        # Numerical data
        self.m195num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m1_a0.95.dat'))
        self.m1605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m1_a0.605.dat'))
        self.m295num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m2_a0.95.dat'))
        self.m2605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m2_a0.605.dat'))

        self.m395num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m3_a0.95.dat'))
        self.m3605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m3_a0.605.dat'))
        self.m494num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m4_a0.94.dat'))
        self.m4605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m4_a0.605.dat'))
        self.m595num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m5_a0.95.dat'))
        self.m5605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_vec_numerical_m5_a0.605.dat'))

    def tearDown(self):
        plt.show()

    def test_non_rel_limit(self):
        """Testing non-rel. limit: alpha=0 and Mcloud=0"""

        """omega_R"""
        # alpha -> 0, Mcloud = 1
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(np.abs(self.rv.omega_real(1,0,sp,1))<self._tol)
            # m=2
            self.assertTrue(np.abs(self.rv.omega_real(2,0,sp,1))<self._tol)

        """Delta omega_R"""
        # alpha -> 0
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(np.abs(self.rv._deltaomega(1,0,sp,0))<self._tol)
            # m=2
            self.assertTrue(np.abs(self.rv._deltaomega(2,0,sp,0))<self._tol)

        """Mcloud hierarchy"""
        # alpha = 0.1, Mcloud -> 0 vs. alpha = 0.1, Mcloud = 0.1
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(self.rv.omega_real(1,0.1,sp,0)>self.rv.omega_real(1,0.1,sp,0.1))
            # m=2
            self.assertTrue(self.rv.omega_real(2,0.1,sp,0)>self.rv.omega_real(2,0.1,sp,0.1))

    def test_delta_omega_consistency(self):
        """Tests self-consistency of frequency drift, derivative of d omega_R/d Mc and deltaoemga()"""
        mcl = [0.001,0.01,0.1]
        # m=1 test field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rv_testfield.omega_real(1,al,sp,mc)
                    dwr = self.rv_testfield.domegar_dmc(1,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rv.omega_real(1,al,sp,0))<self._tol)
        # m=1 rel field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rv.omega_real(1,al,sp,mc)
                    dwr = self.rv._deltaomega(1,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rv.omega_real(1,al,sp,0))<self._tol)
        # m=2
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rv.omega_real(2,al,sp,mc)
                    dwr = self.rv.domegar_dmc(2,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rv.omega_real(2,al,sp,0))<self._tol)


    def test_omega_imag_hierarchy(self):
        """Testing spin hierarchy of omega_I(alpha,a) for fixed alpha"""
        for i, al in enumerate(self.alp):
            res1 = 0
            res2 = 0
            for j, sp in enumerate(self.spi):
                # m=1
                if (self.rv.omega_imag(1,al,sp)>res1): res1=self.rv.omega_imag(1,al,sp)
                else: self.assertTrue(False)
                # m=2
                if (self.rv.omega_imag(2,al,sp)>res2): res2=self.rv.omega_imag(2,al,sp)
                else: self.assertTrue(False)

    def test_omega_real_hierarchy(self):
        """Testing spin hierarchy of omega_R(alpha,a) for fixed alpha"""

        alpl = [0.05,0.06,0.07,0.08,0.09,0.1]
        for i, al in enumerate(alpl):
            res1 = 0
            res2 = 0
            for j, sp in enumerate(self.spi):
                # m=1
                if (self.rv.omega_real(1,al,sp,0)>res1): res1=self.rv.omega_real(1,al,sp,0)
                else: self.assertTrue(False)
                # m=2
                if (self.rv.omega_real(2,al,sp,0)>res2): res2=self.rv.omega_real(2,al,sp,0)
                else: self.assertTrue(False)

    def test_y_utility(self):
        """Testing y utility function"""
        
        """Tesing alphamax and oh"""
        ra1, ro1, ra2, ro2 = 0, 0, 0, 0
        for i, sp in enumerate(self.spi):
            # For fixed alpha = 0.1
            # m=1
            yl1, aml1, ohl1 = self.rv._y(1,0.1,sp)
            # m=2
            yl2, aml2, ohl2 = self.rv._y(2,0.1,sp)
            if (aml1>ra1 and ohl1>ro1 and aml2>ra2 and ohl2>ro2): 
                ra1, ro1, ra2, ro2 = aml1, ohl1, aml2, ohl2
            else:
                self.assertTrue(False)

        """Testing y"""
        ry1, ry2 = 0, 0
        alp1 = [0.05+1e-6,0.25,0.5]
        alp2 = [0.25+1e-6,0.55,0.9]
        for i in range(0,3):
            # For fixed spin = 0.9
            # m=1
            yl1, aml1, ohl1 = self.rv._y(1,alp1[i],0.9)
            # m=2
            yl2, aml2, ohl2 = self.rv._y(2,alp2[i],0.9)
            if (yl1>ry1 and yl2>ry2): 
                ry1, ry2 = yl1, yl2
            else:
                self.assertTrue(False)

    def test_sat_consistency(self):
        """Testing consistency of alphasat() and spinsat() routines to within tolerance"""
        tol = 1e-6
        for i, sp in enumerate(self.spi[:-1]):
            # m=1
            als = self.rv._alphasat(1, sp)
            sps = self.rv._spinsat(1,als)
            self.assertTrue(abs((sps-sp)/sp)<tol)
            # m=2
            als = self.rv._alphasat(2, sp)
            sps = self.rv._spinsat(2,als)
            self.assertTrue(abs((sps-sp)/sp)<tol)

    def test_power_consistency(self):
        """
        Testing power_gw() vs. strain_sph_harm() routines 
        to within tolerance in relativistic regimes:
        The two agree only at the saturated spin for a 
        given alpha (power_gw() assumes saturated state)
        """
        tol = 1e-3

        # m=1 
        for j, al in enumerate(self.alp):
            spsat = self.rv._spinsat(1,al)
            wr = 2.0*self.rv.omega_real(1,al,spsat,0)
            pw = self.rv.power_gw(1,al,0) # power_gw is spin-independent
            st = self.rv.strain_sph_harm(1,al,spsat)
            pwst = np.sum(abs(st)**2)*wr**2/(8.0*np.pi)
            if (abs((pw-pwst)/pw)>tol):
                # Plotting power in case difference > tol
                alloc = self.m1pw[:,0]
                for l,alk in enumerate(alloc):
                    spsat = self.rv._spinsat(1,alk)
                    wr = 2.0*self.rv.omega_real(1,alk,spsat,0)
                    pwloc = self.rv.power_gw(1,alk,spsat)
                    stloc = np.sum(abs(self.rv.strain_sph_harm(1,alk,spsat))**2)*wr**2/(8*np.pi)
                    plt.yscale('log')
                    plt.scatter(alk,pwloc,color='C0')
                    plt.scatter(alk,stloc,color='C1')
                self.assertTrue(abs((pw-pwst)/pw)<tol)

        # m=2
        alp2 = [0.05,0.2,0.4]
        for j, al in enumerate(alp2):
            spsat = self.rv._spinsat(1,al)
            wr = 2.0*self.rv.omega_real(2,al,spsat,0)
            pw = self.rv.power_gw(2,al,0) # power_gw is spin-independent
            st = self.rv.strain_sph_harm(2,al,spsat)
            pwst = np.sum(abs(st)**2)*wr**2/(8.0*np.pi)
            if (abs((pw-pwst)/pw)>tol):
                # Plotting power in case difference > tol
                alloc = self.m2pw[:,0]
                for l,alk in enumerate(alloc):
                    spsat = self.rv._spinsat(2,alk)
                    wr = 2.0*self.rv.omega_real(2,alk,spsat,0)
                    pwloc = self.rv.power_gw(2,alk,spsat)
                    stloc = np.sum(abs(self.rv.strain_sph_harm(2,alk,spsat))**2)*wr**2/(8*np.pi)
                    plt.yscale('log')
                    plt.scatter(alk,pwloc,color='C0')
                    plt.scatter(alk,stloc,color='C1')
                self.assertTrue(abs((pw-pwst)/pw)<tol)

    def test_data_interpolation_boundaries(self):
        """
        Tests output of interpolation routines in extrapolation
        regions (=nan, following scipy.interpolate.LinearNDInterpolator() conventions)
        """
        alsw = [0.05,0.25]
        spsw = [self.rv._aswitch(1),self.rv._aswitch(2)]

        # m=1 test field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                y, apm, oh = self.rv._y(1,al,sp)
                if (al>alsw[0] and sp>spsw[0]):
                    self.assertFalse(np.isnan(self.rv._f1wr(y, sp)))
                    self.assertFalse(np.isnan(self.rv._f1wi(y, sp)))
                else:
                    self.assertTrue(np.isnan(self.rv._f1wr(y, sp)))
                    self.assertTrue(np.isnan(self.rv._f1wi(y, sp)))

        # m=2
        alp2 = [0.1,0.2,0.3,0.5]
        for i,al in enumerate(alp2):
            for j,sp in enumerate(self.spi):
                y, apm, oh = self.rv._y(2,al,sp)
                if (al>alsw[1] and sp>spsw[1]):
                    self.assertFalse(np.isnan(self.rv._f2wr(y, sp)))
                    self.assertFalse(np.isnan(self.rv._f2wi(y, sp)))
                else:
                    self.assertTrue(np.isnan(self.rv._f2wr(y, sp)))
                    self.assertTrue(np.isnan(self.rv._f2wi(y, sp)))

    def test_omegaR_against_v1_data(self):
        """Testing omega_R(alpha,spin) against values obtained for v1 to within tolerance"""
        tol = 1e-6
        errcount = 0
        errplt = self.errpltglb

        # m=1, a=0.99
        altest = self.m1wr99[:,0]
        wrtest = self.m1wr99[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rv.omega_real(1,altest[i],0.99,0)
            if (abs((wrc-wrt)/wrt)>tol):
                if (errplt):
                    plt.plot(altest, wrtest/altest, label='wr_v1, sp=0.99,m=1')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rv.omega_real(1,al,0.99,0)
                    plt.plot(altest,wrltest/altest, label, label='wr_SuperRad, sp=0.99,m=1')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.99,m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # m=1, a=0.4
        altest = self.m1wr4[:,0]
        wrtest = self.m1wr4[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rv.omega_real(1,altest[i],0.4,0)
            if (abs((wrc-wrt)/wrt)>tol):
                if (errplt):
                    plt.plot(altest, wrtest/altest, label='wr_v1, sp=0.4,m=1')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rv.omega_real(1,al,0.4,0)
                    plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp=0.4,m=1')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.4,m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=2, a=0.99
        altest = self.m2wr99[:,0]
        wrtest = self.m2wr99[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rv.omega_real(2,altest[i],0.99,0)
            if (abs((wrc-wrt)/wrt)>tol):
                if (errplt):
                    plt.plot(altest, wrtest/altest, label='wr_v1, sp=0.99,m=2')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rv.omega_real(2,al,0.99,0)
                    plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp=0.99,m=2')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.99,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=2, a=0.4
        altest = self.m2wr4[:,0]
        wrtest = self.m2wr4[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rv.omega_real(2,altest[i],0.4,0)
            if (abs((wrc-wrt)/wrt)>tol):
                if (errplt):
                    plt.plot(altest, wrtest/altest, label='wr_v1, sp=0.4,m=2')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rv.omega_real(2,al,0.4,0)
                    plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp=0.4,m=2')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.4,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_omegaR_against_v1_data: Error count = %d/4' % (errcount))
            plt.title('Vector: Testing omega_R (wr) against v1 data')
            plt.legend()
            self.assertTrue(False)

    def test_omegaI_against_v1_data(self):
        """Testing omega_I(alpha,spin) against values obtained for v1 to within tolerance"""
        tol = 1e-6
        errcount = 0
        errplt = self.errpltglb

        # m=1, a=0.99
        altest = self.m1wi99[:,0]
        witest = self.m1wi99[:,1]
        for i,wit in enumerate(witest):
            wic = self.rv.omega_imag(1,altest[i],0.99)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.99,m=1')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rv.omega_imag(1,al,0.99)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.99,m=1')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.99,m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=1, a=0.4
        altest = self.m1wi4[:,0]
        witest = self.m1wi4[:,1]
        for i,wit in enumerate(witest):
            wic = self.rv.omega_imag(1,altest[i],0.4)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.4,m=1')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rv.omega_imag(1,al,0.4)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.4,m=1')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.4,m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=2, a=0.99
        altest = self.m2wi99[:,0]
        witest = self.m2wi99[:,1]
        for i,wit in enumerate(witest):
            wic = self.rv.omega_imag(2,altest[i],0.99)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.99,m=2')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rv.omega_imag(2,al,0.99)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.99,m=2')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.99,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=2, a=0.4
        altest = self.m2wi4[:,0]
        witest = self.m2wi4[:,1]
        for i,wit in enumerate(witest):
            wic = self.rv.omega_imag(2,altest[i],0.4)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.4,m=2')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rv.omega_imag(2,al,0.4)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.4,m=2')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.4,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_omegaI_against_v1_data: Error count = %d/4' % (errcount))
            plt.title('Vector: Testing omega_I (wi) against v1 data')
            plt.legend()
            self.assertTrue(False)
    
    def test_modes_against_numerical_data(self):
        """Testing omega_R(alpha,spin) against values obtained directly from the field's eom"""
        tol = 1e2
        errcount = 0
        errplt = self.errpltglb

        # m\in {1,2}, a\in {0.95,0.605}
        for l in range(0, 2): # m loop
            for k in range(0, 2): # spin loop
                if (k==0 and l==0):
                    altest = self.m195num[:,0]
                    wrtest = self.m195num[:,1]
                    witest = self.m195num[:,2]
                elif (k==1 and l==0):
                    altest = self.m1605num[:,0]
                    wrtest = self.m1605num[:,1]
                    witest = self.m1605num[:,2]
                elif (k==0 and l==1):
                    altest = self.m295num[:,0]
                    wrtest = self.m295num[:,1]
                    witest = self.m295num[:,2]
                elif (k==1 and l==1):
                    altest = self.m2605num[:,0]
                    wrtest = self.m2605num[:,1]
                    witest = self.m2605num[:,2]
                spinin = [0.95,0.605]
                aziin = [1,2]
                for i in range(0,len(wrtest)):
                    wrc = self.rv.omega_real(aziin[l],altest[i],spinin[k],0)
                    wrt = wrtest[i]
                    wic = self.rv.omega_imag(aziin[l],altest[i],spinin[k])
                    wit = witest[i]
                    if (abs((wrc-wrt)/wrt)>tol or abs((wic-wit)/wit)>tol):
                        if (errplt):
                            plt.figure(1)
                            plt.title('Vector: Testing omega_R (wr) against numerical data')
                            plt.plot(altest, wrtest/altest)
                            wrltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wrltest[j] = self.rv.omega_real(aziin[l],al,spinin[k],0)
                            plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.yscale('log')
                            plt.xscale('log')
                            plt.legend()
                            plt.figure(2)
                            plt.title('Vector: Testing omega_I (wi) against numerical data')
                            plt.plot(altest, witest)
                            wiltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wiltest[j] = self.rv.omega_imag(aziin[l],al,spinin[k])
                            plt.plot(altest,wiltest, label='wi_SuperRad, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.yscale('log')
                            plt.xscale('log')
                            plt.legend()
                        errcount += 1
                        break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_modes_against_numerical_data: Error count = %d/4' % (errcount))
            self.assertTrue(False)


    def test_higher_m_modes_against_numerical_data(self):
        """Testing omega_R(alpha,spin) against values obtained directly from the field's eom for m >= 3"""
        tol = 2.5e-1
        errcount = 0
        errplt = self.errpltglb

        # m\in {3,4,5}, a\in {0.95,0.605}
        for l in range(0, 3): # m loop
            for k in range(0, 2): # spin loop
                if (k==0 and l==0):
                    altest = self.m395num[:,0]
                    wrtest = self.m395num[:,1]
                    witest = self.m395num[:,2]
                elif (k==1 and l==0):
                    altest = self.m3605num[:,0]
                    wrtest = self.m3605num[:,1]
                    witest = self.m3605num[:,2]
                elif (k==0 and l==1):
                    altest = self.m494num[:,0]
                    wrtest = self.m494num[:,1]
                    witest = self.m494num[:,2]
                elif (k==1 and l==1):
                    altest = self.m4605num[:,0]
                    wrtest = self.m4605num[:,1]
                    witest = self.m4605num[:,2]
                elif (k==0 and l==2):
                    altest = self.m595num[:,0]
                    wrtest = self.m595num[:,1]
                    witest = self.m595num[:,2]
                elif (k==1 and l==2):
                    altest = self.m5605num[:,0]
                    wrtest = self.m5605num[:,1]
                    witest = self.m5605num[:,2]

                spinin = [0.95,0.605]
                if (l==1): spinin = [0.94,0.605]
                aziin = [3,4,5]
                for i in range(0,len(wrtest)):
                    wrc = self.rv_higher_m.omega_real(aziin[l],altest[i],spinin[k],0)
                    wrt = wrtest[i]
                    wic = self.rv_higher_m.omega_imag(aziin[l],altest[i],spinin[k])
                    wit = witest[i]
                    if (abs((wrc-wrt)/wrt)>tol or abs((wic-wit)/wit)>tol):
                        if (errplt):
                            plt.figure(1)
                            plt.title('Vector: Testing omega_R (wr) against numerical data')
                            plt.plot(altest, wrtest/altest)
                            wrltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wrltest[j] = self.rv_higher_m.omega_real(aziin[l],al,spinin[k],0)
                            plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.yscale('log')
                            plt.xscale('log')
                            plt.legend()

                            plt.figure(2)
                            plt.title('Vector: Testing omega_I (wi) against numerical data')
                            plt.plot(altest, witest)
                            wiltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wiltest[j] = self.rv_higher_m.omega_imag(aziin[l],al,spinin[k])
                            plt.plot(altest,wiltest, label='wi_SuperRad, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.yscale('log')
                            plt.xscale('log')
                            plt.legend()
                        errcount += 1
                        break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_modes_against_numerical_data: Error count = %d/6' % (errcount))
            self.assertTrue(False)


    def test_deltaomega_against_v2_data(self):
        """Testing /_deltaomega(alpha,Mc) against values obtained for v2 to within tolerance"""
        tol = 1e-8
        errcount = 0
        errplt = self.errpltglb

        altest = self.v2_shift[1]
        mctest = self.v2_shift[0]
        dwrtest = self.v2_shift[2]
        for i,dwrt in enumerate(dwrtest):
            dwrc = self.rv._deltaomega(1,altest[i],0,mctest[i])
            if (abs((dwrc-dwrt)/dwrc)>tol):
                if (errplt):
                    plt.title('Vector: Test deltaomega (dw) against v2 data')
                    plt.plot(altest, -dwrtest, '.', label='dw_v1, m=1')
                    dwrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        dwrltest[j] = self.rv._deltaomega(1,al,0,mctest[j])
                    plt.plot(altest,-dwrltest, '.', label='dw_SuperRad, m=1')
                    plt.plot(altest,np.abs((dwrtest-dwrltest)/dwrtest), '.', label='rel_diff, m=1')
                    plt.yscale('log')
                    #plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_deltaomega_against_numerical_data: Error count = %d/1' % (errcount))
            self.assertTrue(False)


    def test_omegaR_against_freqshift_data(self):
        """Testing omega_R(alpha,spin,Mc) against numerical data to within tolerance"""
        tol = 2*1e-2
        errcount = 0
        errplt = self.errpltglb

        # m=1 rel field
        altest = self.nr_shift_data[1]
        wrtest = self.nr_shift_data[2]
        mctest = self.nr_shift_data[0]
        vecspin = np.vectorize(self.rv._spinsat, excluded=[0])
        atest = vecspin(1, altest)
        for i,wrt in enumerate(wrtest):
            # non test field version doesn't include spin correction
            dwr = self.rv.omega_real(1,altest[i],atest[i],mctest[i])-self.rv.omega_real(1,altest[i],atest[i],0)
            dwrt =wrt-self.rv.omega_real(1,altest[i],atest[i],0)
            if (abs((dwr-dwrt)/dwr)>tol):
                if (errplt):
                    plt.title('Vector: Test omega_R (wr) against freq shift data')
                    dwrltest = np.zeros_like(altest)
                    dwrtest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        dwrltest[j] = -self.rv.omega_real(1,al,atest[j],mctest[j])+self.rv.omega_real(1,al,atest[j],0)
                        dwrtest[j] = -wrtest[j]+self.rv.omega_real(1,altest[j],atest[j],0)
                    plt.plot(altest,dwrltest, '.',label='wr_SuperRad, m=1')
                    plt.plot(altest, dwrtest, '.',label='wr_data, m=1')
                    plt.plot(altest,np.abs((dwrtest-dwrltest)/dwrtest), '.', label='rel_diff, m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break
        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_omegaR_against_freqshift_data: Error count = %d/1' % (errcount))
            self.assertTrue(False)

    def test_power_against_v1_data(self):
        """Testing dot{E}(alpha,spin=spin_sat) against values obtained for v1 to within tolerance"""
        tol = 1e-6

        # m=1, spin-independent
        altest = self.m1pw[:,0]
        pwtest = self.m1pw[:,1]
        for i,pwt in enumerate(pwtest):
            pwc = self.rv.power_gw(1,altest[i],0)
            if (abs((pwc-pwt)/pwc)>tol): self.assertTrue(False)

        # m=2, spin-independent
        altest = self.m2pw[:,0]
        pwtest = self.m2pw[:,1]
        for i,pwt in enumerate(pwtest):
            pwc = self.rv.power_gw(2,altest[i],0)
            if (abs((pwc-pwt)/pwc)>tol): self.assertTrue(False)

    def test_strain_against_v1_data(self):
        """Testing h^{lm} against values obtained for v1 to within tolerance"""
        tol = 1e-6
        errcount = 0
        errplt = self.errpltglb

        # m=1, a=0.99
        altest = self.m1strain99[:,0]
        strtest = self.m1strain99[:,1]
        for i,strt in enumerate(strtest):
            strc = np.sum(abs(self.rv.strain_sph_harm(1,altest[i],0.99))**2)
            if (abs((strc-strt)/strc)>tol):
                if (errplt):
                    plt.plot(altest, strtest)
                    strltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        strltest[j] = np.sum(abs(self.rv.strain_sph_harm(1,al,0.99))**2)
                    plt.plot(altest,strltest)
                    plt.plot(altest,np.abs((strtest-strltest)/strtest))
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # m=2, a=0.99
        altest = self.m2strain99[:,0]
        strtest = self.m2strain99[:,1]
        for i,strt in enumerate(strtest):
            strc = np.sum(abs(self.rv.strain_sph_harm(2,altest[i],0.99))**2)
            if (abs((strc-strt)/strc)>tol):
                if (errplt):
                    plt.plot(altest, strtest)
                    strltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        strltest[j] = np.sum(abs(self.rv.strain_sph_harm(2,al,0.99))**2)
                    plt.plot(altest,strltest)
                    plt.plot(altest,np.abs((strtest-strltest)/strtest))
                    plt.yscale('log')
                    plt.xscale('log')
                errcount += 1
                break

        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_strain_against_v1_data: Error count = %d/2' % (errcount))
            self.assertTrue(False)

