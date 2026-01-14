import unittest
import numpy as np
import superrad.ultralight_boson as ulb
import superrad.rel_vec_cloud as rvc
import superrad.rel_sca_cloud as rsc
import superrad.nonrel_cloud as nrc

class TestFrontEnd(unittest.TestCase):

    @classmethod
    def setUpClass(self):
        """Setting up front ends of all waveform models"""
        self.alp = [0.001,0.01,0.1,0.5,1.0]
        self.spi = [0.001,0.1,0.5,0.8,0.99,0.995]
        self.bcwm = []
        model_type = ['relativistic','non-relativistic']
        model_spin = [0,1]
        self.nmodels = 2*len(model_spin)*len(model_type)
        label = 0
        self.conv = {}
        for ty in model_type:
            for sp in model_spin:
                self.bcwm.append(ulb.UltralightBoson(spin=sp,model=ty,nonrel_freq_shift=True))
                self.conv[label] = ty+', spin = '+str(sp)+', test field calculation'
                label += 1
        for ty in model_type:
            for sp in model_spin:
                self.bcwm.append(ulb.UltralightBoson(spin=sp,model=ty,nonrel_freq_shift=False))
                self.conv[label] = ty+', spin = '+str(sp)+', relativistic field calculation'
                label += 1

    def tearDown(self):
        pass

    def test_power_consistency(self):
        """Testing GW power against backend quantity in natural units"""
        tol = 1e-1

        theta = np.linspace(0,np.pi,513)
        for i,mod in enumerate(self.bcwm):
            for al in self.alp:
                for sp in self.spi:
                    try:
                        wm = mod.make_waveform(1,sp,al,units="natural")
                        pw = wm.power_gw(0)
                        wr = 2.0*np.pi*wm.freq_gw(1e20)*wm.mass_bh_final()
                        hp,hx,delta = wm.strain_amp(0, theta)
                        pwstr = wr**2*np.trapz((hp**2+hx**2)*np.sin(theta),theta)*np.pi/(16.0*np.pi)
                        if (abs((pwstr-pw)/pw)>tol):
                            print(self.conv[i])
                            print("alpha = "+str(al))
                            print("spin = "+str(sp))
                            print("diff = "+str(abs((pwstr-pw)/pw)))
                            self.assertTrue(abs((pwstr-pw)/pw)<tol)
                    except ValueError:
                        pass
       


    def test_saturation_conditions(self):
        """
        Testing saturation output of front end in all models given 
        some alpha and spin to within tolerance
        """
        tol = 1e-3

        for i,mod in enumerate(self.bcwm):
            for al in self.alp:
                for sp in self.spi:
                    try:
                        wm = mod.make_waveform(1,sp,al,units="natural")
                        spf = wm.spin_bh_final()
                        mf = wm.mass_bh_final()
                        wr = wm.freq_gw(0)*np.pi*mf
                        mi = wm.azimuthal_num()
                        Oh = 0.5*spf/(1.0+np.sqrt(1.0-spf**2))
                        if (abs((mi*Oh-wr)/wr)>tol):
                            print(self.conv[i])
                            print("alpha = "+str(al))
                            print("spin = "+str(sp))
                            print("diff = "+str(abs((mi*Oh-wr)/wr)))
                            self.assertTrue(abs((mi*Oh-wr)/wr)<tol)
                    except ValueError:
                        pass

    def test_phase(self):
        """
        Test that the time derivative of the GW phase gives the same value as the frequency.
        """
        tol = 1e-8

        for i,mod in enumerate(self.bcwm):
            for al in self.alp:
                for sp in self.spi:
                    try:
                        wm = mod.make_waveform(1,sp,al,units="natural")
                        t = np.linspace(0, 2*wm.gw_time(), 2048)
                        phi_dot = 0
                        phi = wm.phase_gw(t)
                        phi_dot = (phi[1:]-phi[:-1])/(t[1:]-t[:-1])
                        th = 0.5*(t[1:]+t[:-1]) 
                        freq = np.vectorize(wm.freq_gw, excluded=[0]) 
                        f = freq(t[1:-1])
                        rel_err = abs((f-phi_dot/(2.0*np.pi))/f)
                        #plt.plot(th, rel_err, ":")
                        #plt.show()
                        if (rel_err.max()>tol):
                            print(self.conv[i])
                            print("alpha = "+str(al))
                            print("spin = "+str(sp))
                            print("rel error = "+str(rel_err.max()))
                            self.assertTrue(rel_err.max()<tol)
                    except ValueError:
                        pass

if __name__ == '__main__':
    unittest.main()
                    
