import sys
from numpy import *
from matplotlib import pyplot as plt
from matplotlib import cm
from matplotlib import rcParams
from scipy.interpolate import CubicSpline
from pathlib import Path
import os

"""
Plot tabulated growth rates and real frequency of unstable massive spin-2 modes
on black hole spacetime as calculated in https://arxiv.org/abs/2309.05096 (This
does not use the superrad software package.)
"""

current = os.path.dirname(os.path.realpath(__file__))
fpath = os.path.dirname(current)+'/superrad/data/spin2_omega.dat'


# Initialize plots
f1 = plt.figure(1)
a1 = f1.gca()
f2 = plt.figure(2)
a2 = f2.gca()
size = 18
params = {'legend.fontsize': 'large',
          'figure.figsize': (6,5),
          'axes.labelsize': size*0.8,
          'xtick.labelsize': size*0.75,
          'ytick.labelsize': size*0.75}
plt.rcParams.update(params)

# specifying color scheme
cmap = cm.get_cmap('plasma_r')
cindex = [0.05,0.2,0.35,0.5,0.7,0.8,0.9,1.0]
col = cmap(cindex)

lw=1.5
i=0
fi = 0
sn = 15
mi,si,ali,wri,wii = genfromtxt(fpath,unpack=True)
for m in unique(mi):
    sp = unique(si[mi==m])
    sp = flip(sp)
    if (not('spcol' in vars())):
        spcol = { }
        for l,spin in enumerate(sp):
            spcol[str(spin)] = col[l]

    # Looping through spins for each m-mode
    for spin in sp:
        al = ali[mi==m][si[mi==m]==spin]
        wr = wri[mi==m][si[mi==m]==spin]
        wi = wii[mi==m][si[mi==m]==spin]

        # Misc. plotting design
        mrk = "o"
        ln = "-"
        lbl = ""
        if (m==0):
            lbl=(r"$a_{\rm BH}="+str(spin)+"$")
        if (m==1):
            mrk = "s"
            ln = "--"
        if (m==2):
            mrk = "d"
            ln = ":"
        if (m==3):
            mrk = "v"
            ln = "-."

        # plotting growth rates
        if (m==0):
            alphal = linspace(0,al[-1],1024)
            line = CubicSpline(concatenate([[0],al]),concatenate([[0],wi]))
        else:
            alphal = linspace(al[0],al[-1],1024)
            line = CubicSpline(al,wi)
        a1.scatter(al,wi,marker=mrk, color=spcol[str(spin)],s=sn)
        l = a1.semilogy(alphal,line(alphal),ln,lw=lw,color=spcol[str(spin)],label=lbl)

        # plotting oscillation frequency
        if (m>0):
            line = CubicSpline(al,wr)
            a2.scatter(al,wr,marker=mrk, color=spcol[str(spin)],s=sn)
            l = a2.plot(alphal,line(alphal),ln,lw=lw,color=spcol[str(spin)])

plot_lines = []
l1, = a1.plot([10,10],[10,10],marker="o",lw=lw,color='black')
l2, = a1.plot([10,10],[10,10],'--',marker="s",lw=lw,color='black')
l3, = a1.plot([10,10],[10,10],':',marker="d",lw=lw,color='black')
l4, = a1.plot([10,10],[10,10],'-.',marker="v",lw=lw,color='black')
plot_lines.append([l1, l2, l3, l4])
legend1 = a1.legend(plot_lines[0], ["$m=0$", "$m=1$", "$m=2$", "$m=3$"], loc='upper left',ncol=4)
a1.add_artist(legend1)

# generating legend for azimuthal indices
ylab = [r"$\omega_I M$",r"$\omega_R M$"]
for ai,ax in enumerate([a1,a2]):
    # Misc. labeling
    ax.set_xlabel(r"$\mu M$")
    ax.set_ylabel(ylab[ai])
    ax.set_xlim([-0.01,2.1])
    if (ai==0): ax.set_ylim([3e-6,0.3])
    if (ai==1): ax.set_ylim([-0.05,1.4])
    if (ai==0): ax.legend(loc="lower left", fontsize=size-7, ncol=3)
    ax.grid(True, linestyle=':', color='gray', zorder=-100)

# output plot
plt.show()
