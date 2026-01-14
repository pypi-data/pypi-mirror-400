import numpy as np
from scipy.integrate import solve_ivp

fields = ["Mc", "Mbh", "Jbh"]
Nfields = len(fields)
d = dict()
for n in range(Nfields):
        d[fields[n]] = n

def EOM(t, y, m, mu, cloud_model):
    """
    Coupled evolution of the boson cloud mass (Mc),
    black hole mass (Mbh), and angular momentum (Jbh).
    """
    ydot = np.zeros_like(y)
    Mc = y[d["Mc"]]
    Mbh = y[d["Mbh"]]
    abh = y[d["Jbh"]]/Mbh**2
    alpha = mu*Mbh
    Pgw = cloud_model.power_gw(m, alpha, abh)*(Mc/Mbh)**2
    omegaR = cloud_model.omega_real(m, alpha, abh, Mc/Mbh)/Mbh
    omegaI = cloud_model.omega_imag(m, alpha, abh)/Mbh
    ydot[d["Mc"]] = 2.0*omegaI*Mc-Pgw
    ydot[d["Mbh"]] = -2.0*omegaI*Mc
    ydot[d["Jbh"]] = -2.0*m/omegaR*omegaI*Mc
    return ydot

class EvolveCloud(object):
    """
    Object for calculating superradiant growth, saturation, and dissipation due to GWs of boson cloud.
    """
    def __init__(self, cloud_model, m, mu, Mbh0, Jbh0, Mc0, t, rtol=1.0e-9):
        #Initial conditions
        y = np.zeros(Nfields)
        y[d["Mbh"]] = Mbh0 
        y[d["Jbh"]] = Jbh0 
        y[d["Mc"]] = Mc0 

        #Integrate ODEs
        sol = solve_ivp(EOM, [t[0],t[-1]], y, args=(m, mu, cloud_model), 
                        method="DOP853", dense_output=True, rtol=rtol, atol=0, max_step=2*(t[1]-t[0]))
        f = sol.sol(t)

        self._m = m
        self._mu = mu
        self._Mc = f[d["Mc"],]
        self._Mbh = f[d["Mbh"],]
        self._abh = f[d["Jbh"],]/f[d["Mbh"],]**2
        alpha = self._Mbh*mu
        Pgw_vec = np.vectorize(cloud_model.power_gw, excluded=[0])
        Pgw = Pgw_vec(m, alpha, self._abh)*(self._Mc/self._Mbh)**2
        omegaI_vec = np.vectorize(cloud_model.omega_imag, excluded=[0])
        omegaI = omegaI_vec(m, alpha, self._abh)/self._Mbh
        self._Mcdot = 2.0*omegaI*self._Mc-Pgw 
    def mass_cloud(self):
        return (self._Mc)
    def mass_cloud_dot(self):
        return (self._Mcdot)
    def mass_bh(self):
        return (self._Mbh)
    def spin_bh(self):
        return (self._abh)

