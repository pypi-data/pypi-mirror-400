# Example of constraining ultralight bosons with spin down.

from matplotlib import pyplot as plt
import numpy as np
from scipy.interpolate import interp1d 

import sys
import os
from pathlib import Path
current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

from superrad.nonrel_cloud import NonrelScalar, NonrelVector
from superrad.rel_vec_cloud import RelVector
from superrad.rel_sca_cloud import RelScalar

from superrad import spin_down

#Planck mass in eV
mpl = 1.220890e28
#10^5 years in secs
yr_to_sec = 3600.0*24*365.25

#Boson spin: s=1 (vector) or s=0 (scalar)
s = 1

#Set to true to use relativistic calculation
use_rel_cm = False 

#Spindown time
tage = 1.0e5*yr_to_sec 

#Choose cloud model
from superrad.hybrid_cloud import HybridCloudModel
nrv_cm = NonrelVector() 
#Use azimuthal numbers up to 15
nrv_cm._max_m = 15
if (s==0 and use_rel_cm):
    cm = HybridCloudModel(RelScalar(),NonrelScalar()) 
elif (s==0):
    cm = NonrelScalar() 
elif (s==1 and use_rel_cm):
    cm = HybridCloudModel(RelVector(no_radiation=True),nrv_cm) 
elif (s==1):
    cm = nrv_cm 

#Range of boson masses considered in eV
log10mu = np.linspace(-14.5, -11, 64)
mu=10**log10mu

#Range of black hole masses considered, in solar masses
Mbh = np.linspace(41, 204, 32)

Xmax = spin_down.max_spin(mu, tage, cm, Mbh[0], Mbh[-1], len(Mbh), units="physical")

#Make 2D color plot
logmug, Mbhg = np.meshgrid(log10mu, Mbh, indexing='ij')
plt.figure(1)
plt.pcolormesh(logmug, Mbhg, Xmax, cmap='rainbow')
plt.colorbar(label=r"$\chi_{\rm max}$")
plt.contour(logmug, Mbhg, Xmax, levels=[0.7])
plt.title(r"$s=%d$, $t_{\rm age}=%1.1e$ yr" % (s,tage/yr_to_sec))
plt.xlabel(r"$\log_{10}(\mu_b/{\rm eV})$")
plt.ylabel(r"$M_{\rm BH}\ (M_{\odot})$ ")

chi_max_mbh_interp = interp1d(Mbh, Xmax, axis=1, kind="linear")

#Create some fake posteriors
Nsamples = 1000
m1_pos = Mbh[0]+np.random.rand(Nsamples)*(Mbh[-1]-Mbh[0])
m2_pos = Mbh[0]+np.random.rand(Nsamples)*(Mbh[-1]-Mbh[0])
a1_pos = 0.5+np.random.rand(Nsamples)*0.49
a2_pos = 0.5+np.random.rand(Nsamples)*0.49

#Calculate fraction of samples that are allowed for each boson mass
a1_max_pos = chi_max_mbh_interp(m1_pos)
a2_max_pos = chi_max_mbh_interp(m2_pos)
Iallowed = np.logical_and(a1_max_pos > a1_pos, a2_max_pos > a2_pos)
Pmu = np.sum(Iallowed, axis=1)/Nsamples 

#Threshold for placing constraints
Pth = 0.1
#Constrained range
Ic = Pmu<Pth
mu_c = mu[Ic]
#Number of extra samples below threshold
Nc = ((Pth-Pmu[Ic])*Nsamples).astype(int)

#Constraints on interactions
from superrad.boson_couplings import ScalarQuarticInteraction
from superrad.boson_couplings import KineticMixedDarkPhoton 
from superrad.boson_couplings import HiggsAbelian 
if (s==0):
    scQI =  ScalarQuarticInteraction(cm, tage, units="physical")
    qi_max_coup_vec = np.vectorize(scQI.max_coupling, excluded=[0])
    couplings = [qi_max_coup_vec]
elif (s==1): 
    kmdp =  KineticMixedDarkPhoton(cm, units="physical")
    dp_max_coup_vec = np.vectorize(kmdp.max_coupling, excluded=[0])
    ha =  HiggsAbelian(cm, units="physical")
    ha_max_coup_vec = np.vectorize(ha.max_coupling, excluded=[0])
    couplings = [dp_max_coup_vec, ha_max_coup_vec]

eps_min = np.ones_like(mu_c)

for m,max_coup_vec in enumerate(couplings):
    for n,mu0 in enumerate(mu_c):
        I1 = a1_max_pos[Ic,][n,] < a1_pos
        I2 = a2_max_pos[Ic,][n,] < a2_pos
        if (np.any(I1) and np.any(I2)):
            eps1=max_coup_vec(mu0, m1_pos[I1], a1_pos[I1])
            eps2=max_coup_vec(mu0, m2_pos[I2], a2_pos[I2])
            #If both BHs are excluded, we can take the max coupling between the two
            Iboth = np.logical_and(I1, I2)
            Ixor = np.logical_xor(I1, I2)
            eps1[Iboth[I1]] = np.fmax(eps1[Iboth[I1]], eps2[Iboth[I2]])
            eps = np.concatenate([eps1, eps2[Ixor[I2]]])
            eps_min[n] = np.partition(eps, Nc[n])[Nc[n]] 
        elif (not(np.any(I1)) and not(np.any(I2))):
            continue
        elif (not(np.any(I2))):
            eps1=max_coup_vec(mu0, m1_pos[I1], a1_pos[I1])
            eps_min[n] = np.partition(eps1, Nc[n])[Nc[n]] 
        else:
            eps2=max_coup_vec(mu0, m2_pos[I2], a2_pos[I2])
            eps_min[n] = np.partition(eps2, Nc[n])[Nc[n]] 
    plt.figure()
    if (s==1 and max_coup_vec==dp_max_coup_vec):
        plt.loglog(mu_c, eps_min)
        plt.ylabel(r"$\epsilon$")
    elif (s==1 and max_coup_vec==ha_max_coup_vec):
        plt.loglog(mu_c, eps_min)
        plt.ylabel(r"$g M_{\rm pl}/(\lambda^{1/2}v)$")
    elif (s==0 and max_coup_vec==qi_max_coup_vec):
        plt.loglog(mu_c, (1e9*eps_min/mpl))
        plt.ylabel(r"GeV$/f$")
    plt.xlabel(r"$\mu_b$ (eV)")

plt.show()
