import unittest
import numpy as np
import superrad.rel_sca_cloud as rsc
from matplotlib import pyplot as plt
from pathlib import Path

class TestRelSca(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """Sets up the vector cloud model class tested here"""
        # Plot issues if error is found
        self.errpltglb = True
        self._tol= 1e-9

        # Cloud settings
        self.rs_testfield = rsc.RelScalar(nonrel_freq_shift = True)
        self.rs = rsc.RelScalar(nonrel_freq_shift = False)
        self.mmax = self.rs.max_azi_num()
        self.maxspin = self.rs.max_spin()
        self.spi = [0.5*self.maxspin, 0.6*self.maxspin, 0.8*self.maxspin, 1.0*self.maxspin]
        self.alp = [0.001, 0.01, 0.1]

        # Modes data
        self.m1wr99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_wr_a0.99.dat'))
        self.m1wi99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_wi_a0.99.dat'))
        self.m1wr4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_wr_a0.4.dat'))
        self.m1wi4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_wi_a0.4.dat'))
        self.m2wr99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_wr_a0.99.dat'))
        self.m2wi99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_wi_a0.99.dat'))
        self.m2wr4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_wr_a0.4.dat'))
        self.m2wi4 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_wi_a0.4.dat'))
        self.v2_shift = np.loadtxt(Path(__file__).parent.joinpath('./testdata/scalar_freqshift_v2_m1.dat'), unpack=True)
        self.nr_shift_data = np.loadtxt(Path(__file__).parent.joinpath('./testdata/scalar_freqshift_test_m1.dat'), unpack=True)

        # GW emission data
        self.m1pw = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_power_gw.dat'))
        self.m1strain99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m1_strain_a0.99.dat'))
        self.m2pw = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_power_gw.dat'))
        self.m2strain99 = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_m2_strain_a0.99.dat'))

        # Numerical data
        self.m195num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_numerical_m1_a0.95.dat'))
        self.m1605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_numerical_m1_a0.605.dat'))
        self.m295num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_numerical_m2_a0.95.dat'))
        self.m2605num = np.loadtxt(Path(__file__).parent.joinpath('./testdata/rel_sca_numerical_m2_a0.605.dat'))

    def tearDown(self):
        plt.show()

    def test_non_rel_limit(self):
        """Testing non-rel. limit: alpha=0 and Mcloud=0"""

        """omega_R"""
        # alpha -> 0, Mcloud = 1
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(self.rs_testfield.omega_real(1,0,sp,1) < self._tol)
            self.assertTrue(self.rs.omega_real(1,0,sp,1) < self._tol)
            # m=2
            self.assertTrue(self.rs.omega_real(2,0,sp,1) < self._tol)

        """Delta omega_R"""
        # alpha -> 0
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(np.abs(self.rs_testfield._deltaomega(1,0,sp,0)) < self._tol)
            self.assertTrue(np.abs(self.rs._deltaomega(1,0,sp,0)) < self._tol)
            # m=2
            self.assertTrue(np.abs(self.rs._deltaomega(2,0,sp,0)) < self._tol)

        """Mcloud hierarchy"""
        # alpha = 0.1, Mcloud -> 0 vs. alpha = 0.1, Mcloud = 0.1
        for i, sp in enumerate(self.spi):
            # m=1
            self.assertTrue(self.rs_testfield.omega_real(1,0.1,sp,0)>self.rs.omega_real(1,0.1,sp,0.1))
            self.assertTrue(self.rs.omega_real(1,0.1,sp,0)>self.rs.omega_real(1,0.1,sp,0.1))
            # m=2
            self.assertTrue(self.rs.omega_real(2,0.1,sp,0)>self.rs.omega_real(2,0.1,sp,0.1))

    def test_delta_omega_consistency(self):
        """Tests self-consistency of frequency drift, derivative of d omega_R/d Mc and deltaoemga()"""
        mcl = [0.001,0.01,0.1]
        # m=1 test field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rs_testfield.omega_real(1,al,sp,mc)
                    dwr = self.rs_testfield.domegar_dmc(1,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rs_testfield.omega_real(1,al,sp,0))< self._tol)
        # m=1 rel field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rs.omega_real(1,al,sp,mc)
                    dwr = self.rs._deltaomega(1,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rs.omega_real(1,al,sp,0))< self._tol)
        # m=2
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                for k,mc in enumerate(mcl):
                    wr = self.rs.omega_real(2,al,sp,mc)
                    dwr = self.rs.domegar_dmc(2,al,sp,mc)
                    wr -= mc*dwr
                    self.assertTrue(np.abs(wr- self.rs.omega_real(2,al,sp,0))< self._tol)

    def test_omega_imag_hierarchy(self):
        """Testing spin hierarchy for fixed alpha"""
        for i, al in enumerate(self.alp):
            res1tf = 0
            res1 = 0
            res2 = 0
            for j, sp in enumerate(self.spi):
                # m=1 test field
                if (self.rs_testfield.omega_imag(1,al,sp)>res1tf): res1tf=self.rs_testfield.omega_imag(1,al,sp)
                else: 
                    # Plotting quantities to trouble shoot, if test fails
                    print("spin = "+str(sp))
                    print("alpha = "+str(al))
                    alphal = np.linspace(self.alp[0]*0.5,al,201)
                    wil = np.zeros_like(alphal)
                    spl = [sp,0.9*sp,0.8*sp]
                    plt.figure(1)
                    for l in range(0,4):
                        for k,alpl in enumerate(alphal):
                            wil[k] = self.rs_testfield.omega_imag(1,alpl,spl[l])
                        plt.plot(alphal,wil,label='spin = '+str(spl[l]))
                        plt.yscale('log')
                        plt.legend()
                    self.assertTrue(False)
                # m=1 rel field
                if (self.rs.omega_imag(1,al,sp)>res1): res1=self.rs.omega_imag(1,al,sp)
                else:
                    # Plotting quantities to trouble shoot, if test fails
                    print("spin = "+str(sp))
                    print("alpha = "+str(al))
                    alphal = np.linspace(self.alp[0]*0.5,al,201)
                    wil = np.zeros_like(alphal)
                    spl = [sp,0.9*sp,0.8*sp]
                    plt.figure(1)
                    for l in range(0,4):
                        for k,alpl in enumerate(alphal):
                            wil[k] = self.rs.omega_imag(1,alpl,spl[l])
                        plt.plot(alphal,wil,label='spin = '+str(spl[l]))
                        plt.yscale('log')
                        plt.legend()
                    self.assertTrue(False)
                # m=2
                if (self.rs.omega_imag(2,al,sp)>res2): res2=self.rs.omega_imag(2,al,sp)
                else: self.assertTrue(False)

    def test_y_utility(self):
        """Testing y utility function"""
        
        """Tesing alphamax and oh"""
        ra1tf, ro1tf, ra1, ro1, ra2, ro2 = 0, 0, 0, 0, 0, 0
        for i, sp in enumerate(self.spi):
            # For fixed alpha = 0.1
            # m=1 test field
            yl1tf, aml1tf, ohl1tf = self.rs_testfield._y(1,0.1,sp)
            # m=1 rel field
            yl1, aml1, ohl1 = self.rs._y(1,0.1,sp)
            # m=2
            yl2, aml2, ohl2 = self.rs._y(2,0.1,sp)
            if (aml1tf>ra1tf and ohl1tf>ro1tf and aml1>ra1 and ohl1>ro1 and aml2>ra2 and ohl2>ro2): 
                ra1tf, ro1tf, ra1, ro1, ra2, ro2 = aml1tf, ohl1tf, aml1, ohl1, aml2, ohl2
            else:
                self.assertTrue(False)

        """Testing y"""
        ry1tf, ry1, ry2 = 0, 0, 0
        alp1 = [0.05+1e-6,0.25,0.5]
        alp2 = [0.25+1e-6,0.55,0.8]
        for i in range(0,3):
            # For fixed spin = 0.9
            # m=1 test field
            yl1tf, aml1tf, ohl1tf = self.rs_testfield._y(1,alp1[i],0.9)
            # m=1 rel field
            yl1, aml1, ohl1 = self.rs._y(1,alp1[i],0.9)
            # m=2
            yl2, aml2, ohl2 = self.rs._y(2,alp2[i],0.9)
            if (yl1tf>ry1tf and yl1>ry1 and yl2>ry2): 
                ry1tf, ry1, ry2 = yl1tf, yl1, yl2
            else:
                self.assertTrue(False)

    def test_sat_consistency(self):
        """Testing consistency of alphasat() and spinsat() routines to within tolerance"""
        tol = 1e-6
        for i, sp in enumerate(self.spi[:-1]):
            # m=1 test field
            als = self.rs_testfield._alphasat(1, sp)
            sps = self.rs_testfield._spinsat(1,als)
            self.assertTrue(abs((sps-sp)/sp)<tol)
            # m=1 rel field
            als = self.rs._alphasat(1, sp)
            sps = self.rs._spinsat(1,als)
            self.assertTrue(abs((sps-sp)/sp)<tol)
            # m=2
            als = self.rs._alphasat(2, sp)
            sps = self.rs._spinsat(2,als)
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
            spsat = self.rs._spinsat(1,al)
            wr = 2.0*self.rs.omega_real(1,al,spsat,0)
            pw = self.rs.power_gw(1,al,0) # power_gw is spin-independent
            st = self.rs.strain_sph_harm(1,al,spsat)
            pwst = np.sum(abs(st)**2)*wr**2/(8.0*np.pi)
            if (abs((pw-pwst)/pw)>tol):
                # Plotting power in case difference > tol
                alloc = self.m1pw[:,0]
                for l,alk in enumerate(alloc):
                    spsat = self.rs._spinsat(1,alk)
                    wr = 2.0*self.rs.omega_real(1,alk,spsat,0)
                    pwloc = self.rs.power_gw(1,alk,spsat)
                    stloc = np.sum(abs(self.rs.strain_sph_harm(1,alk,spsat))**2)*wr**2/(8*np.pi)
                    plt.yscale('log')
                    plt.scatter(alk,pwloc,color='C0')
                    plt.scatter(alk,stloc,color='C1')
                self.assertTrue(abs((pw-pwst)/pw)<tol)

        # m=2
        for j, al in enumerate(self.alp):
            spsat = self.rs._spinsat(2,al)
            wr = 2.0*self.rs.omega_real(2,al,spsat,0)
            pw = self.rs.power_gw(2,al,0) # power_gw is spin-independent
            st = self.rs.strain_sph_harm(2,al,spsat)
            pwst = np.sum(abs(st)**2)*wr**2/(8.0*np.pi)
            if (abs((pw-pwst)/pw)>tol):
                # Plotting power in case difference > tol
                alloc = self.m1pw[:,0]
                for l,alk in enumerate(alloc):
                    spsat = self.rs._spinsat(2,alk)
                    wr = 2.0*self.rs.omega_real(2,alk,spsat,0)
                    pwloc = self.rs.power_gw(2,alk,spsat)
                    stloc = np.sum(abs(self.rs.strain_sph_harm(2,alk,spsat))**2)*wr**2/(8*np.pi)
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
        spsw = [self.rs._aswitch(1),self.rs._aswitch(2)]

        # m=1 test field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                y, apm, oh = self.rs_testfield._y(1,al,sp)
                if (al>alsw[0] and sp>spsw[0]):
                    self.assertFalse(np.isnan(self.rs_testfield._f1wr(y, sp)))
                    self.assertFalse(np.isnan(self.rs_testfield._f1wi(y, sp)))
                else:
                    self.assertTrue(np.isnan(self.rs_testfield._f1wr(y, sp)))
                    self.assertTrue(np.isnan(self.rs_testfield._f1wi(y, sp)))

        # m=1 rel field
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                y, apm, oh = self.rs._y(1,al,sp)
                if (al>alsw[0] and sp>spsw[0]):
                    self.assertFalse(np.isnan(self.rs._f1wr(y, sp)))
                    self.assertFalse(np.isnan(self.rs._f1wi(y, sp)))
                else:
                    self.assertTrue(np.isnan(self.rs._f1wr(y, sp)))
                    self.assertTrue(np.isnan(self.rs._f1wi(y, sp)))

        # m=2
        for i,al in enumerate(self.alp):
            for j,sp in enumerate(self.spi):
                y, apm, oh = self.rs._y(2,al,sp)
                if (al>alsw[1] and sp>spsw[1]):
                    self.assertFalse(np.isnan(self.rs._f2wr(y, sp)))
                    self.assertFalse(np.isnan(self.rs._f2wi(y, sp)))
                else:
                    self.assertTrue(np.isnan(self.rs._f2wr(y, sp)))
                    self.assertTrue(np.isnan(self.rs._f2wi(y, sp)))

    def test_omegaR_against_v1_data(self):
        """Testing omega_R(alpha,spin) against values obtained for v1 to within tolerance"""
        tol = 1e-6
        errcount = 0 
        errplt = self.errpltglb

        # m=1, a=0.99
        altest = self.m1wr99[:,0]
        wrtest = self.m1wr99[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rs.omega_real(1,altest[i],0.99,0)
            if (abs((wrc-wrt)/wrc)>tol):
                if (errplt):
                    plt.title('Scalar: Test omega_R (wr) against v1 data')
                    plt.plot(altest, wrtest, label='wr_v1, sp=0.99,m=1')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rs.omega_real(1,al,0.99,0)
                    plt.plot(altest,wrltest, label='wr_SuperRad, sp=0.99,m=1')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.99,m=1')
                    plt.yscale('log')
                    #plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # m=1, a=0.4
        altest = self.m1wr4[:,0]
        wrtest = self.m1wr4[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rs.omega_real(1,altest[i],0.4,0)
            if (abs((wrc-wrt)/wrc)>tol):
                if (errplt):
                    plt.plot(altest, wrtest, label='wr_v1, sp=0.4,m=1')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rs.omega_real(1,al,0.4,0)
                    plt.plot(altest,wrltest, label='wr_SuperRad, sp=0.4,m=1')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.4,m=1')
                    plt.yscale('log')
                    #plt.xscale('log')
                    plt.legend()
                errcount += 1
                break


        # m=2, a=0.99
        altest = self.m2wr99[:,0]
        wrtest = self.m2wr99[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rs.omega_real(2,altest[i],0.99,0)
            if (abs((wrc-wrt)/wrc)>tol):
                if (errplt):
                    plt.title('Scalar: Test omega_R (wr) against v1 data')
                    plt.plot(altest, wrtest, label='wr_v1, sp=0.99,m=2')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rs.omega_real(2,al,0.99,0)
                    plt.plot(altest,wrltest, label='wr_SuperRad, sp=0.99,m=2')
                    plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp=0.99,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # m=2, a=0.4
        altest = self.m2wr4[:,0]
        wrtest = self.m2wr4[:,1]
        for i,wrt in enumerate(wrtest):
            wrc = self.rs.omega_real(2,altest[i],0.4,0)
            if (abs((wrc-wrt)/wrc)>tol): 
                if (errplt):
                    plt.plot(altest, wrtest, label='wr_v1, sp=0.4,m=2')
                    wrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wrltest[j] = self.rs.omega_real(2,al,0.4,0)
                    plt.plot(altest,wrltest, label='wr_SuperRad, sp=0.4,m=2')
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
            self.assertTrue(False)

    def test_omegaI_against_v1_data(self):
        """Testing omega_I(alpha,spin) against values obtained for v1 to within tolerance"""
        tol = 1e-6
        errcount = 0
        errplt = self.errpltglb

        # m=1 test field, a=0.99
        altest = self.m1wi99[:,0]
        witest = self.m1wi99[:,1]
        for i,wit in enumerate(witest):
            wic = self.rs_testfield.omega_imag(1,altest[i],0.99)
            if (abs((wic-wit)/wic)>tol):
                if (errplt):
                    plt.title('Scalar: Test omega_I (wi) against v1 data')
                    plt.plot(altest, witest, label='wi_v1, sp=0.99,m=1')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rs_testfield.omega_imag(1,al,0.99)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.99,m=1')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.99,m=1')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # m=1 test field, a=0.4
        altest = self.m1wi4[:,0]
        witest = self.m1wi4[:,1]
        for i,wit in enumerate(witest):
            wic = self.rs_testfield.omega_imag(1,altest[i],0.4)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.4,m=1')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rs_testfield.omega_imag(1,al,0.4)
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
            wic = self.rs.omega_imag(2,altest[i],0.99)
            if (abs((wic-wit)/wic)>tol):
                if (errplt):
                    plt.title('Scalar: Test omega_I (wi) against v1 data')
                    plt.plot(altest, witest, label='wi_v1, sp=0.99,m=2')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rs.omega_imag(2,al,0.99)
                    plt.plot(altest,wiltest, label='wi_SuperRad, sp=0.99,m=2')
                    plt.plot(altest,np.abs((witest-wiltest)/witest), label='rel_diff, sp=0.99,m=2')
                    plt.yscale('log')
                    plt.xscale('log')
                    plt.legend()
                errcount += 1
                break

        # m=2, a=0.4
        altest = self.m2wi4[:,0]
        witest = self.m2wi4[:,1]
        for i,wit in enumerate(witest):
            wic = self.rs.omega_imag(2,altest[i],0.4)
            if (abs((wic-wit)/wic)>tol): 
                if (errplt):
                    plt.plot(altest, witest, label='wi_v1, sp=0.4,m=2')
                    wiltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        wiltest[j] = self.rs.omega_imag(2,al,0.4)
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
            dwrc = self.rs._deltaomega(1,altest[i],0,mctest[i])
            if (abs((dwrc-dwrt)/dwrc)>tol):
                if (errplt):
                    plt.title('Scalar: Test deltaomega (dw) against v2 data')
                    plt.plot(altest, -dwrtest, '.', label='dw_v1, m=1')
                    dwrltest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        dwrltest[j] = self.rs._deltaomega(1,al,0,mctest[j])
                    plt.plot(altest,-dwrltest, '.',label='dw_SuperRad, m=1')
                    print(np.abs((dwrtest-dwrltest)/dwrtest))
                    plt.plot(altest,np.abs((dwrtest-dwrltest)/dwrtest), '.',label='rel_diff, m=1')
                    plt.yscale('log')
                    #plt.xscale('log')
                    plt.legend()
                errcount += 1
                break
        # Raising error if one or more came up
        if (errcount>0):
            print('\n')
            print('Test_deltaomega_against_v2_data: Error count = %d/1' % (errcount))
            self.assertTrue(False)


    def test_omegaR_against_freqshift_data(self):
        """Testing omega_R(alpha,spin,Mc) against numerical data to within tolerance"""
        tol = 1e-2
        errcount = 0
        errplt = self.errpltglb

        # m=1 rel field
        altest = self.nr_shift_data[1]
        wrtest = self.nr_shift_data[2]
        mctest = self.nr_shift_data[0]
        vecspin = np.vectorize(self.rs._spinsat, excluded=[0])
        atest = vecspin(1, altest)
        for i,wrt in enumerate(wrtest):
            # non test field version doesn't include spin correction
            dwr = self.rs.omega_real(1,altest[i],atest[i],mctest[i])-self.rs.omega_real(1,altest[i],atest[i],0)
            dwrt =wrt-self.rs.omega_real(1,altest[i],atest[i],0)
            if (abs((dwr-dwrt)/dwr)>tol and mctest[i]>0.02):
                if (errplt):
                    plt.title('Scalar: Test omega_R (wr) against freq shift data')
                    dwrltest = np.zeros_like(altest)
                    dwrtest = np.zeros_like(altest)
                    for j,al in enumerate(altest):
                        dwrltest[j] = -self.rs.omega_real(1,al,atest[j],mctest[j])+self.rs.omega_real(1,al,atest[j],0)
                        dwrtest[j] = -wrtest[j]+self.rs.omega_real(1,altest[j],atest[j],0)
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

    def test_modes_against_numerical_data(self):
        """Testing omega_R and omega_I against values obtained directly from the field's eom"""
        tol = 1e2
        errcount = 0
        errplt = self.errpltglb

        # m\in {1,2} test field, a\in {0.95,0.605}
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
                    wrc = self.rs_testfield.omega_real(aziin[l],altest[i],spinin[k],0)
                    wrt = wrtest[i]
                    wic = self.rs_testfield.omega_imag(aziin[l],altest[i],spinin[k])
                    wit = witest[i]
                    if (abs((wrc-wrt)/wrt)>tol or abs((wic-wit)/wit)>tol):
                        if (errplt):
                            plt.figure(1)
                            plt.title('Scalar: Test omega_R (wr) against numerical data')
                            plt.plot(altest, wrtest/altest)
                            wrltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wrltest[j] = self.rs_testfield.omega_real(aziin[l],al,spinin[k],0)
                            plt.plot(altest,wrltest/altest, label='wr_SuperRad, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.plot(altest,np.abs((wrtest-wrltest)/wrtest), label='rel_diff, sp='+str(spinin[k])+',m='+str(aziin[l]))
                            plt.yscale('log')
                            plt.xscale('log')
                            plt.legend()
                            plt.figure(2)
                            plt.title('Scalar: Test omega_I (wi) against numerical data')
                            plt.plot(altest, witest)
                            wiltest = np.zeros_like(altest)
                            for j,al in enumerate(altest):
                                wiltest[j] = self.rs_testfield.omega_imag(aziin[l],al,spinin[k])
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

    def test_power_against_v1_data(self):
        """Testing dot{E}(alpha,spin=spin_sat) against values obtained for v1 to within tolerance"""
        tol = 1e-6

        # m=1, spin-independent
        altest = self.m1pw[:,0]
        pwtest = self.m1pw[:,1]
        for i,pwt in enumerate(pwtest):
            pwc = self.rs.power_gw(1,altest[i],0)
            if (abs((pwc-pwt)/pwc)>tol): self.assertTrue(False)

        # m=2, spin-independent
        altest = self.m2pw[:,0]
        pwtest = self.m2pw[:,1]
        for i,pwt in enumerate(pwtest):
            pwc = self.rs.power_gw(2,altest[i],0)
            if (abs((pwc-pwt)/pwc)>tol): self.assertTrue(False)

    def test_strain_against_v1_data(self):
        """Testing h^{lm} against values obtained for v1 to within tolerance"""
        tol = 1e-6

        # m=1, a=0.99
        altest = self.m1strain99[:,0]
        strtest = self.m1strain99[:,1]
        for i,strt in enumerate(strtest):
            strc = np.sum(abs(self.rs.strain_sph_harm(1,altest[i],0.99))**2)
            if (abs((strc-strt)/strc)>tol): self.assertTrue(False)

        # m=2, a=0.99
        altest = self.m2strain99[:,0]
        strtest = self.m2strain99[:,1]
        for i,strt in enumerate(strtest):
            strc = np.sum(abs(self.rs.strain_sph_harm(2,altest[i],0.99))**2)
            if (abs((strc-strt)/strc)>tol): self.assertTrue(False)

