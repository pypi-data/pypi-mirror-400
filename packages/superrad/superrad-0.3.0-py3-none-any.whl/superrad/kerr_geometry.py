from .geometry import Geometry
import numpy as np
from pathlib import Path
from scipy.optimize import fsolve
from scipy.optimize import least_squares

class KerrGeometry:
    """
    Geometric quantities for black holes with dimensionless spin abh

    All in inputs are in units where black hole mass=1
    Outputs for abh > 1 are ill defined.
    """
    def __init__(self,abh):
        self._abh = np.array(abh).flatten()
        self._risco = np.zeros_like(self._abh)
        self._tdot = np.zeros_like(self._abh)
        self._phidot = np.zeros_like(self._abh)
        for n,a in enumerate(self._abh):
            try:
                self._risco[n], self._tdot[n], self._phidot[n] = self._calculate_Kerr_traj(a)
            except:
                self._risco[n], self._tdot[n], self._phidot[n] = 0,0,0
    def LightRing_radius(self):
        """Returns prograde light ring circumferential radius"""
        a = self._abh
        M = 1
        r = 2*M*(1 + np.cos(2.0/3.0 * np.arccos(-a/M)))
        r_circ = np.sqrt(((r**2+a**2)/r)**2 - a**2*(r**2-2*M*r+a**2)/(r**2))
        return r_circ
    def ISCO_radius(self):
        """Returns prograde ISCO circumferential radius"""
        a = self._abh
        M = 1
        Z1 = 1 + (1 - (a/M)**2)**(1.0/3.0) *((1 + a/M)**(1.0/3.0) + (1 - a/M)**(1.0/3.0))
        Z2 = np.sqrt(3 *(a/M)**2 + Z1**2)
        r = M *(3 + Z2 - np.sqrt((3 - Z1)* (3 + Z1 + 2 *Z2)))
        r_circ = np.sqrt(((r**2+a**2)/r)**2 - a**2*(r**2-2*M*r+a**2)/(r**2))
        return r_circ
    def ISCO_orbital_freq(self):
        """Returns orbital frequency at the prograde ISCO"""
        return -self._phidot
    #/self._tdot*np.abs(1-2*self._risco/(self._risco**2))**(-0.5)
    def ISCO_redshift(self):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the same direction"""
        a = self._abh
        M = 1
        r,tdot,phidot = self._risco,self._tdot,self._phidot
        freq=( 0.5e0 * phidot * ( 0.4e1 * a * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + (-0.1e1) * ( ( 0.16e2 * ( a )**( 2 ) * ( M )**( 2 ) * ( r )**( -2 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + (-0.4e1) * ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) * ( (-0.1e1) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + 0.2e1 * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) ) ) )**( 1/2 ) ) + ( (-0.1e1) * ( (-0.1e1) + 0.2e1 * M * ( r )**( -1 ) ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) * tdot + 0.2e1 * a * M * ( r )**( -1 ) * ( (-0.1e1) * phidot * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + 0.5e0 * ( ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) )**( -1 ) * ( 0.4e1 * a * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + (-0.1e1) * ( ( 0.16e2 * ( a )**( 2 ) * ( M )**( 2 ) * ( r )**( -2 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + (-0.4e1) * ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) * ( (-0.1e1) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + 0.2e1 * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + (-0.2e1) * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( 0.2e1 * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) ) ) )**( 1/2 ) ) * tdot ) ) )
        return -freq
    def ISCO_blueshift(self):
        """Returns redshift from a particle traveling along the prograde ISCO to infinity.
        Here the redshift is calculated for a light ray tangent to the particle's motion and travelling in the opposite direction.
        This geodesic stops escaping the black hole for higher spins (approximately abh = 0.94) when the ISCO radius enters the ergoregion."""
        r,tdot,phidot = self._risco,self._tdot,self._phidot
        a = self._abh
        M = 1
        freq = ( 0.5e0 * phidot * ( 0.4e1 * a * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + ( ( 0.16e2 * ( a )**( 2 ) * ( M )**( 2 ) * ( r )**( -2 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + (-0.4e1) * ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) * ( (-0.1e1) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + 0.2e1 * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) ) ) )**( 1/2 ) ) + ( (-0.1e1) * ( (-0.1e1) + 0.2e1 * M * ( r )**( -1 ) ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) * tdot + 0.2e1 * a * M * ( r )**( -1 ) * ( (-0.1e1) * phidot * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + 0.5e0 * ( ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) )**( -1 ) * ( 0.4e1 * a * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -1 ) + ( ( 0.16e2 * ( a )**( 2 ) * ( M )**( 2 ) * ( r )**( -2 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + (-0.4e1) * ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( -1 ) + ( r )**( 2 ) ) ) * ( (-0.1e1) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) + 0.2e1 * M * ( r )**( -1 ) * ( ( (-0.1e1) + ( 0.2e1 * M * ( r )**( -1 ) + 0.2e1 * a * M * ( r )**( -1 ) * ( ( ( r )**( 4 ) + ( a )**( 2 ) * r * ( 0.2e1 * M + r ) ) )**( -1 ) * ( (-0.2e1) * a * M * r + ( r )**( 2 ) * ( ( r )**( -2 ) * ( 0.4e1 * ( a )**( 2 ) * ( M )**( 2 ) + (-0.1e1) * ( 0.2e1 * M + (-0.1e1) * r ) * ( ( r )**( 3 ) + ( a )**( 2 ) * ( 0.2e1 * M + r ) ) ) )**( 1/2 ) ) ) ) )**( -2 ) ) ) )**( 1/2 ) ) * tdot ) ) )
        return -freq
    def _calculate_Kerr_traj(self, abh):
        """Returns isco radius in Kerr-Schild units along with four velocity of a massive observer at the ISCO"""
        M = 1
        a = abh
        Z1 = 1 + (1 - (a/M)**2)**(1.0/3.0) *((1 + a/M)**(1.0/3.0) + (1 - a/M)**(1.0/3.0))
        Z2 = np.sqrt(3 *(a/M)**2 + Z1**2)
        r = M *(3 + Z2 - np.sqrt((3 - Z1)* (3 + Z1 + 2 *Z2)))
        def to_opt(inp,last=False):
            LnIn = inp[0]
            EnIn = inp[1]
            V =0.5e0 * ( r )**( -3 ) * ( 0.4e1 * a * EnIn * LnIn * M + ( ( LnIn )**( 2 ) * ( 0.2e1 * M + (-0.1e1) * r ) + ( ( r )**( 2 ) * ( 0.2e1 * M + ( (-0.1e1) + ( EnIn )**( 2 ) ) * r ) + ( a )**( 2 ) * ( (-0.1e1) * r + ( EnIn )**( 2 ) * ( 0.2e1 * M + r ) ) ) ) )
            drV =( r )**( -4 ) * ( (-0.6e1) * a * EnIn * LnIn * M + ( (-0.1e1) * M * ( r )**( 2 ) + ( ( LnIn )**( 2 ) * ( (-0.3e1) * M + r ) + ( a )**( 2 ) * ( r + (-0.1e1) * ( EnIn )**( 2 ) * ( 0.3e1 * M + r ) ) ) ) )
            dr2V = ( r )**( -5 ) * ( 0.24e2 * a * EnIn * LnIn * M + ( 0.3e1 * ( LnIn )**( 2 ) * ( 0.4e1 * M + (-0.1e1) * r ) + ( 0.2e1 * M * ( r )**( 2 ) + 0.3e1 * ( a )**( 2 ) * ( (-0.1e1) * r + ( EnIn )**( 2 ) * ( 0.4e1 * M + r ) ) ) ) )
            return np.array([np.abs(V),np.abs(drV),np.abs(dr2V)]).flatten()
        Lstart = -np.sqrt(12 *M**2)
        Estart = 1
        x0 = np.array([Lstart, Estart])
        opt_params = least_squares(to_opt, x0,bounds=([-np.inf, -np.inf], [0,np.inf]))
        EE =opt_params.x[1]
        L = opt_params.x[0]
        phidot = (-0.1e1) * ( L * ( 0.1e1 + (-0.2e1) * M * ( r )**( -1 ) ) + (-0.2e1) \
* a * EE * M * ( r )**( -1 ) ) * ( ( (-0.4e1) * ( a )**( 2 ) * ( M \
)**( 2 ) * ( r )**( -2 ) + (-0.1e1) * ( 0.1e1 + (-0.2e1) * M * ( r \
)**( -1 ) ) * ( ( a )**( 2 ) + ( 0.2e1 * ( a )**( 2 ) * M * ( r )**( \
-1 ) + ( r )**( 2 ) ) ) ) )**( -1 )
        tdot =0.5e0 * ( M )**( -1 ) * ( r )**( -1 ) * ( ( (-0.1e1) * ( a )**( 2 ) * ( r )**( 4 ) + ( 0.2e1 * M * ( r )**( 5 ) + (-0.1e1) * ( r )**( 6 ) ) ) )**( -1 ) * ( (-0.4e1) * ( a )**( 2 ) * EE * ( M )**( 2 ) * ( r )**( 4 ) + ( (-0.4e1) * a * L * ( M )**( 2 ) * ( r )**( 4 ) + ( (-0.2e1) * ( a )**( 2 ) * EE * M * ( r )**( 5 ) + (-0.2e1) * EE * M * ( r )**( 7 ) ) ) )
        return r,tdot,phidot

