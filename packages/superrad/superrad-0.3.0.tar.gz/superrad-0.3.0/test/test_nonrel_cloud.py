import unittest
import superrad.nonrel_cloud as nrc
import numpy as np

class TestNonRel(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """Sets up the cloud model class tested here"""
        self.nrm = [nrc.NonrelScalar(),nrc.NonrelVector()]
        self.maxspin = 1.0
        self.spi = [0.5*self.maxspin, 0.6*self.maxspin, 0.8*self.maxspin, 1.0*self.maxspin]
        self.alp = [0.001, 0.01, 0.1]

    def tearDown(self):
        pass

    def test_non_rel_limit(self):
        """Testing non-rel. limit: alpha=0 and Mcloud=0"""

        for mod in self.nrm:
            """\omega_R"""
            # alpha -> 0, Mcloud = 1
            for i, sp in enumerate(self.spi):
                for j in range(1,mod.max_azi_num()):
                    self.assertEqual(mod.omega_real(j,0,sp,1), 0)
        
            """Mcloud hierarchy"""
            # alpha = 0.1, Mcloud -> 0 vs. alpha = 0.1, Mcloud = 0.1
            for i, sp in enumerate(self.spi):
                for j in range(1,mod.max_azi_num()):
                    self.assertTrue(mod.omega_real(j,0.1,sp,0)>mod.omega_real(j,0.1,sp,0.1))

    def test_delta_omega_consistency(self):
        """Tests self-consistency of frequency drift, derivative of d omega_R/d Mc and deltaoemga()"""
        mcl = [0.001,0.01,0.1]

        for mod in self.nrm:
            for l in range(1,mod.max_azi_num()):
                for i,al in enumerate(self.alp):
                    for j,sp in enumerate(self.spi):
                        for k,mc in enumerate(mcl):
                            wr = mod.omega_real(l,al,sp,mc)
                            dwr = mod.domegar_dmc(l,al,sp,mc)
                            wr -= mc*dwr
                            self.assertEqual(wr, mod.omega_real(l,al,sp,0)) #Mcloud=0


    def test_omega_imag_hierarchy(self):
        """Testing spin hierarchy of \omega_I for fixed alpha"""
        for mod in self.nrm:
            for m in range(1,mod.max_azi_num()):
                for i, al in enumerate(self.alp):
                    res = 0
                    for j, sp in enumerate(self.spi):
                        if (mod.omega_imag(m,al,sp)>res): 
                            res=mod.omega_imag(m,al,sp)
                        else:
                            self.assertTrue(False)

    def test_power_hierarchy(self):
        """Testing azimuthal index hierarchy of power for fixed alpha"""
        for mod in self.nrm:
                for i, al in enumerate(self.alp):
                    res = 0
                    for m in range(mod.max_azi_num(),0,-1):
                        if (mod.power_gw(m,al,0)>res): #power_gw() is spin-independent
                            res=mod.power_gw(m,al,0)
                        else:
                            self.assertTrue(False)

    def test_power_consistency(self):
        """
        Testing power_gw() vs. strain_sph_harm() routines 
        to within tolerance in non-relativistic regimes
        """
        tol = 1e-3
        for mod in self.nrm:
            for m in range(1,mod.max_azi_num()):
                for j, al in enumerate(self.alp):
                    for i, sp in enumerate(self.spi):
                        wr = 2.0*mod.omega_real(m,al,sp,0)
                        pw = mod.power_gw(m,al,sp) 
                        st = mod.strain_sph_harm(m,al,sp)
                        pwst = np.sum(abs(st)**2)*wr**2/(8.0*np.pi)
                        if (abs((pw-pwst)/pw)>tol):
                            self.assertTrue(abs((pw-pwst)/pw)<tol)


