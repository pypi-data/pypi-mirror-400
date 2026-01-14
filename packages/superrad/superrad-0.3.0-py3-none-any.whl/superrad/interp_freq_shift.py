import numpy as np
from scipy import interpolate
from pathlib import Path

"""
Reads in data from numerical black hole-cloud solutions, uses spline
interpolation, and then fits for the frequency shift as a second-order
polynomial in cloud mass.
"""

"""First Scalar case"""
shift_data = np.load(Path(__file__).parent.joinpath('data/scalar_freqshift_m1_ha.npz'))
Mc_ha = shift_data['Mc'].flatten()
alpha_ha = shift_data['alpha'].flatten()
freqs_ha = shift_data['freqs'].flatten()
omega_ha = interpolate.SmoothBivariateSpline(alpha_ha, Mc_ha, freqs_ha, kx=5, ky=5)
alphai_ha = np.linspace(min(alpha_ha), max(alpha_ha), 256)
shift_data = np.load(Path(__file__).parent.joinpath('data/scalar_freqshift_m1_la.npz'))
Mc_xla = shift_data['Mc'].flatten()
alpha_xla = shift_data['alpha'].flatten()
freqs_xla = shift_data['freqs'].flatten()
omega_xla = interpolate.SmoothBivariateSpline(alpha_xla, Mc_xla, freqs_xla, kx=5, ky=5)
alphai_xla = np.linspace(min(alpha_xla), max(alpha_xla), 256)

shift_data = np.load(Path(__file__).parent.joinpath('data/scalar_freqshift_m1.npz'))
Mc = shift_data['Mc'].flatten()
alpha = shift_data['alpha'].flatten()
freqs = shift_data['freqs'].flatten()
numeric_frequencies = interpolate.SmoothBivariateSpline(alpha, Mc, freqs, kx=5, ky=5,s=1.0)
Mci = np.linspace(0.01, 0.1, 256)
alphai_la = np.linspace(min(alpha), max(alpha), 256)
pAlpha_la = np.zeros((len(alphai_la),3))
for n,alpha0 in enumerate(alphai_la):
    omega0 = numeric_frequencies(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_la[n,:] = coef[:]
pAlpha_ha = np.zeros((len(alphai_ha),3))
for n,alpha0 in enumerate(alphai_ha):
    omega0 = omega_ha(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_ha[n,:] = coef[:]
pAlpha_xla = np.zeros((len(alphai_xla),3))
for n,alpha0 in enumerate(alphai_xla):
    omega0 = omega_xla(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_xla[n,:] = coef[:]
alphai = np.linspace(min(alpha), max(alpha_ha), 256)
pAlpha = np.zeros((len(alphai),3))
for i in range(3):
    xlowa_points = interpolate.interp1d(alphai_xla, pAlpha_xla[:,i],kind='cubic')
    lowa_points = interpolate.interp1d(alphai_la, pAlpha_la[:,i],kind='cubic')
    higha_points = interpolate.interp1d(alphai_ha, pAlpha_ha[:,i],kind='cubic')
    for n,alpha0 in enumerate(alphai):
        if 0.24>=alpha0:
            pAlpha[n,i] = xlowa_points(alpha0)
        if 0.24<alpha0<min(alpha_ha):
            pAlpha[n,i] = lowa_points(alpha0)
        if min(alpha_ha)<alpha0<0.43:
            pAlpha[n,i] = lowa_points(alpha0)*((alpha0-0.43)/(min(alpha_ha)-0.43))+higha_points(alpha0)*((alpha0-min(alpha_ha))/(0.43-min(alpha_ha)))
        elif 0.43<alpha0:
            pAlpha[n,i] = higha_points(alpha0)

np.savez('data/scalar_freqshift_m1_interp',alpha=alphai,lin_shift=pAlpha[:,1],quad_shift=pAlpha[:,2])



"""Now vector case"""
# first loading numerical errors for fit weighting
data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_error.npz'))
Mc_err = data['Mc'].flatten()
alpha_err = data['alpha'].flatten()
errs = data['err'].flatten()
for n,al in enumerate(alpha_err):
    if 0.15<al<0.22:
        errs[n]*=(al**4/0.15**3)
data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_error_la.npz'))
Mc_err_la = data['Mc'].flatten()
alpha_err_la = data['alpha'].flatten()
errs_la = data['err'].flatten()
for n,al in enumerate(alpha_err_la):
    if 0.1285<al<0.15:
        errs_la[n]*=(al**4/0.11**3)
    elif al<0.1285:
        errs_la[n]*= (0.1285**4/0.11**3)
data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_error_ha.npz'))
Mc_err_ha = data['Mc'].flatten()
alpha_err_ha = data['alpha'].flatten()
errs_ha = data['errs'].flatten()
for n,al in enumerate(alpha_err_ha):
    if 0<al<0.27:
        errs_ha[n]=1
# now loading data
shift_data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_m1_la.npz'))
Mc_la = shift_data['Mc'].flatten()
alpha_la = shift_data['alpha'].flatten()
freqs_la = shift_data['freqs'].flatten()
freq_errs_la = interpolate.griddata((Mc_err_la,alpha_err_la), errs_la, (Mc_la, alpha_la), method='nearest')
weights_la = 1/freq_errs_la
omega_la = interpolate.SmoothBivariateSpline(alpha_la, Mc_la, freqs_la, w=weights_la, kx=5, ky=5)
shift_data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_m1_ma.npz'))
Mc_ma = shift_data['Mc'].flatten()
alpha_ma = shift_data['alpha'].flatten()
freqs_ma = shift_data['freqs'].flatten()
freq_errs = interpolate.griddata((Mc_err,alpha_err), errs, (Mc_ma, alpha_ma), method='nearest')
weights = 1/freq_errs
omega_ma = interpolate.SmoothBivariateSpline(alpha_ma, Mc_ma, freqs_ma, w=weights, kx=5, ky=5)
shift_data = np.load(Path(__file__).parent.joinpath('data/vector_freqshift_m1_ha.npz'))
Mc_ha = shift_data['Mc'].flatten()
alpha_ha = shift_data['alpha'].flatten()
freqs_ha = shift_data['freqs'].flatten()
freq_errs_ha = interpolate.griddata((Mc_err_ha,alpha_err_ha), errs_ha, (Mc_ha, alpha_ha), method='nearest')
weights_ha = 1/freq_errs_ha
omega_ha = interpolate.SmoothBivariateSpline(alpha_ha, Mc_ha, freqs_ha, w=weights_ha, kx=5, ky=5)
# fitting with quadratic in cloud mass
Mci = np.linspace(0.01, 0.12, 256)
alphai_la = np.linspace(min(alpha_la), 0.15, 256)
alphai_ma = np.linspace(0.15, 0.28, 256)
alphai = np.linspace(min(alpha_la), max(alpha_ha), 256)
pAlpha_la = np.zeros((len(alphai_la),3))
for n,alpha0 in enumerate(alphai_la):
    omega0 = omega_la(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_la[n,:] = coef[:]
pAlpha_ma = np.zeros((len(alphai_ma),3))
for n,alpha0 in enumerate(alphai_ma):
    omega0 = omega_ma(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_ma[n,:] = coef[:]
pAlpha_ha = np.zeros((len(alphai),3))
for n,alpha0 in enumerate(alphai):
    omega0 = omega_ha(alpha0, Mci)[0,]
    p=np.polynomial.polynomial.Polynomial.fit(Mci, omega0,2)
    coef = p.convert().coef
    pAlpha_ha[n,:] = coef[:]
# now matching results for smooth shift
pAlpha = np.zeros((len(alphai),3))
for i in range(3):
    lowa_points = interpolate.interp1d(alphai_ma, pAlpha_ma[:,i],kind='cubic')
    xlowa_points = interpolate.interp1d(alphai_la, pAlpha_la[:,i],kind='cubic')
    for n,alpha0 in enumerate(alphai):
        if alpha0<0.15:
            pAlpha[n,i] = xlowa_points(alpha0)
        if 0.15<alpha0<0.27:
            pAlpha[n,i] = lowa_points(alpha0)
        elif 0.27<alpha0<0.28:
            pAlpha[n,i] = lowa_points(alpha0)*((alpha0-0.28)/(-0.01)) + pAlpha_ha[n,i]*((alpha0 - 0.27)/0.01)
        elif alpha0>0.28:
            pAlpha[n,i] =  pAlpha_ha[n,i]

np.savez('data/vector_freqshift_m1_interp',alpha=alphai,lin_shift=pAlpha[:,1],quad_shift=pAlpha[:,2])


