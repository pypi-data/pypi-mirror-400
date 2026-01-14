"""
If units="physical" units of Msolar=1, and use the following units for
input/output:

mu : electronvolts
Mass : solar mass
time : seconds
frequency : Hz
Power : watts
Distance : Mpc

If units="natural" use units where G=c=hbar=1

If "+alpha" is appended to either "physical" or "natural," then units are the
same as above, except the input mu is taken to be in units of (hbar
c^3)/(G*Mbh0), i.e.  mu is set to the dimensionless "fine structure constant"
alpha. 
"""
def set_units(units, Mbh0):
    if (units=="physical" or units=="physical+alpha"):
        tunit = 4.920551932748678e-06 # (G* solar mass/1 sec)/c^3 
        Punit = 3.6283745e52 # c^5/G in Watts 
        dunit = 4.78691895e-20 # (G* solar mass)/(Mpc *c^2)
        hbar = 1.19727031e-76 # (hbar*c/G)/(solar mass)^2 
        if (units=="physical+alpha"):
            muunit = 1.0/Mbh0
        else:
            muunit = 7.48548859e9 # (eV/hbar)(G* solar mass)/c^3    
    elif (units=="natural" or units=="natural+alpha"):
        tunit = 1.0
        Punit = 1.0
        dunit = 1.0
        hbar = 1.0
        if (units=="natural+alpha"):
            muunit = 1.0/Mbh0
        else:
            muunit = 1.0
    else: 
        raise ValueError("Invalid boson cloud waveform units")
    return (tunit, Punit, dunit, hbar, muunit)

"""Electron mass in same units as boson mass above"""
def electron_mass(units): 
    if (units=="physical" or units=="physical+alpha"):
        return 3.825076814891968e15 #(m_e/hbar)(G* solar mass)/c
    elif (units=="natural" or units=="natural+alpha"):
        return 4.18543e-23 # (m_e/m_Planck)
    else: 
        raise ValueError("Invalid boson cloud waveform units")
