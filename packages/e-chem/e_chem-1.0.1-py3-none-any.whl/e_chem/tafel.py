import numpy as np
import matplotlib.pyplot as plt

from lib import cv

def tafel_slope(cv, area_cm2=1.0, potential_shift=0.0, volts_lower_bound=-10e-3, volts_upper_bound=-1e-3, Ru_ohm=0.0, comp_frac=1.0, return_fit=False):
  
    branch = cv.beforeLeftVertex()
    V_raw = np.asarray(branch.volts, dtype=float)
    I_raw = np.asarray(branch.amps,  dtype=float)  

    V_corr = V_raw - I_raw * Ru_ohm * comp_frac


    V = V_corr + potential_shift


    j = I_raw / float(area_cm2)


    idx_low  = int(np.argmin(np.abs(V - volts_lower_bound)))
    idx_high = int(np.argmin(np.abs(V - volts_upper_bound)))
    i0, i1 = sorted((idx_low, idx_high))


    V_slice = V[i0:i1+1]
    j_slice = j[i0:i1+1]

  
    mask = np.isfinite(V_slice) & np.isfinite(j_slice) & (j_slice != 0)
    V_lin = V_slice[mask]
    logj  = np.log10(np.abs(j_slice[mask]))

    if V_lin.size < 2:
        raise ValueError("Zu wenige Punkte im ausgewählten Spannungsfenster nach Filterung.")

   
    m, b = np.polyfit(logj, V_lin, deg=1)

    if not return_fit:
        return m 

    #error
    yhat = m * logj + b
    ss_res = np.sum((V_lin - yhat)**2)
    ss_tot = np.sum((V_lin - np.mean(V_lin))**2)
    r2 = 1.0 - ss_res/ss_tot if ss_tot > 0 else np.nan

    return m, b, r2, V_lin.size


def plotTafel(cv, upperbound: float, lowerbound: float, potential_shift: float ,area_cm2=1.0):

    branch = cv.beforeLeftVertex()
    volts = np.array(branch.volts) + potential_shift
    amps = np.array(branch.amps) / area_cm2 

    plt.figure()
    plt.semilogx(np.abs(amps), volts, color='black', label='log(|I|) über V')
    plt.axhline(y=upperbound, color='red', linestyle='--', label=f'')
    plt.axhline(y=lowerbound, color='blue', linestyle='--', label=f'')
    
    plt.xlabel("j")
    plt.ylabel("E")
    plt.title("Tafel-Plot mit Grenzen")
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
