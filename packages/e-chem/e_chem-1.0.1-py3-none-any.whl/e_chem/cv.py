import pandas as pd
import numpy as np
from scipy.signal import find_peaks
import matplotlib.pyplot as plt

# Define a class representing a single Cyclic Voltammetry (CV) dataset
class CV:
    def __init__(self, volts, amps):
        # volts: array of potential values (in Volts)
        # amps: array of current values (in Amperes)
        self.volts = volts
        self.amps = amps
    
    def getPotentialAt(self, current: float) -> float:
        """
        Returns the potential (voltage) value that corresponds most closely 
        to a given current value.
        """
        ampsDiffs = np.abs(self.amps - current)        # Difference between each current and the target
        closestAmpsIndex = np.argmin(ampsDiffs)        # Find the index of the closest current value
        return self.volts[closestAmpsIndex]            # Return corresponding voltage
    
    def shiftPotential(self, Overpotential: float) -> float:
        """
        Shifts the entire potential (voltage) curve by a given overpotential value.
        Returns a new CV object with adjusted voltages.
        """
        corrected_potential = np.array(self.volts) + Overpotential
        return CV(corrected_potential, self.amps)
    
    def getCurrentAt(self, atVolts) -> float:
        """
        Returns the current value that corresponds most closely to a given voltage.
        """
        index = np.argmin(np.abs(self.volts - atVolts))
        return self.amps[index]
    
    # ---- Methods for splitting the CV curve around vertex points ---- #
    def beforeRightVertex(self):
        """
        Returns a new CV object containing data before the maximum voltage (right vertex).
        """
        vertexIndex = np.argmax(self.volts)
        return CV(self.volts[:vertexIndex+1], self.amps[:vertexIndex+1])

    def afterRightVertex(self):
        """
        Returns a new CV object containing data after the maximum voltage (right vertex).
        """
        vertexIndex = np.argmax(self.volts)
        return CV(self.volts[vertexIndex:], self.amps[vertexIndex:])
    
    def beforeLeftVertex(self):
        """
        Returns a new CV object containing data before the minimum voltage (left vertex).
        """
        vertexIndex = np.argmin(self.volts)
        return CV(self.volts[:vertexIndex+1], self.amps[:vertexIndex+1])
    
    def afterLeftVertex(self):
        """
        Returns a new CV object containing data after the minimum voltage (left vertex).
        """
        vertexIndex = np.argmin(self.volts)
        return CV(self.volts[vertexIndex:], self.amps[vertexIndex:])
    
    def iRCompensate(self, resistance):
        """
        Applies iR compensation to correct for potential drop due to internal resistance.
        New voltage = measured voltage - (resistance * current)
        """
        compensatedVolts = self.volts - resistance * self.amps
        return CV(compensatedVolts, self.amps)
    
    def findPeaks(self, n_peaks=5, distance=50, prominence=None, x_min=None, x_max=None):
        """
        Finds up to n_peaks local minima (negative peaks) in the current signal
        within an optional voltage range.
        """
        mask = np.ones_like(self.volts, dtype=bool)
        if x_min is not None:
            mask &= self.volts >= x_min
        if x_max is not None:
            mask &= self.volts <= x_max

        xv = self.volts[mask]
        yv = self.amps[mask]

        if len(xv) == 0:
            return np.array([]), np.array([])
 
        idx_local = _find_lower_peaks(xv, yv, n_peaks=n_peaks, distance=distance, prominence=prominence)
                                                       
        if idx_local.size == 0:
            return np.array([]), np.array([])

        return xv[idx_local], yv[idx_local]

# ---- Functions for loading CV data from different instrument formats ---- #

def loadPalmSensCVs(filePath) -> list[CV]:
    """
    Loads cyclic voltammetry data from a PalmSens CSV file.
    Converts current values from µA to A.
    Returns a list of CV objects (for each sweep).
    """
    data = pd.read_csv(filePath, sep=",", skiprows=5)
    matrix = data.to_numpy()

    numberOfCVs = round(len(data.columns) / 2)
    cvs: list[CV] = []

    for i in range(numberOfCVs):
        volts = matrix[0:-1, 2*i].astype(float)
        amps = matrix[0:-1, 2*i+1] * 1e-6  # µA → A
        thisCV = CV(volts, amps)
        cvs.append(thisCV)
    
    return cvs

def loadBioLogicCVs(filePath) -> list[CV]:
    """
    Loads CV data from a BioLogic CSV file.
    Handles multiple cycles and converts mA → A.
    """
    df = pd.read_csv(filePath, sep="\t", decimal=",")
    columnOrder = ["Ewe/V", "<I>/mA", "cycle number"]

    # Check if expected columns exist
    missing_cols = [col for col in columnOrder if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")
    
    data = df[columnOrder].to_numpy()
    cycleCount = int(data[-1, -1])
    cvs: list[CV] = []

    # Separate each cycle into an individual CV object
    for i in range(1, cycleCount + 1):
        cvData = data[data[:, 2] == i]
        cv = CV(cvData[:, 0], cvData[:, 1] * 1e-3)  # mA → A
        cvs.append(cv)

    return cvs

def loadSquidstatCV(filePath) -> CV:
    """
    Loads a single CV from a Squidstat CSV file (legacy format).
    """
    df = pd.read_csv(filePath, sep=",", decimal=".")
    columnOrder = ["Working Electrode (V)", "Current (A)"]

    missing_cols = [col for col in columnOrder if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")
    
    data = df[columnOrder].to_numpy()
    return CV(data[:, 0], data[:, 1])

def loadSquidstatCVs(filePath) -> list[CV]:
    """
    Loads multiple CV cycles from a Squidstat CSV file.
    Groups data by step number and repeat number.
    """
    df = pd.read_csv(filePath, sep=",", decimal=".")
    columnOrder = ["Working Electrode (V)", "Current (A)", "Step number", "Repeats"]
    missing_cols = [col for col in columnOrder if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")
    
    data = df[columnOrder].to_numpy()
    stepCount = int(data[-1, 2])
    cvs: list[CV] = []

    for stepRef in range(1, stepCount + 1):
        stepData = data[data[:, 2] == stepRef]
        cycleCount = int(stepData[-1, -1])

        for cycleRef in range(1, cycleCount + 1):
            cycleData = stepData[stepData[:, 3] == cycleRef]
            thisCV = CV(cycleData[:, 0], cycleData[:, 1])
            cvs.append(thisCV)

    return cvs

# ---- Helper functions for fitting and plotting ---- #

def _find_lower_peaks(x, y, n_peaks=5, distance=50, prominence=None):
    """
    Finds up to n_peaks minima (negative peaks) in the signal.
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    
    # find_peaks(-y) → finds minima of y
    peaks, props = find_peaks(-y, distance=distance, prominence=prominence)
  
    order = np.argsort(y[peaks])   # Sort peaks by current (lowest values first)
    sel = peaks[order][:n_peaks]
    return np.sort(sel)
  

def _exp_fit_through_points(x, y):
    """
    Fits an exponential curve through given points.
    Returns parameters A and b of the model y = -A * exp(bx)
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)
    if x.size < 2:  
        return None, None
    yp = -y
    m = yp > 0
    if np.count_nonzero(m) < 2:
        return None, None

    xv = x[m]; yv = yp[m]
    c = np.polyfit(xv, np.log(yv), 1)  # Linear fit in log-space
    b = c[0]; a = c[1]
    A = np.exp(a)
    return A, b


def _lower_peaks_exp_curve(x, y,
    n_peaks=5, distance=50, prominence=None,
    n_pts=600, clip_to_data=True, start_x=None):
    """
    Generates an exponential curve that fits the minima of the CV curve.
    """
    x = np.asarray(x, float)
    y = np.asarray(y, float)

    idx = _find_lower_peaks(x, y, n_peaks=n_peaks, distance=distance, prominence=prominence)
    if idx.size == 0:
        return np.array([]), np.array([])

    A, b = _exp_fit_through_points(x[idx], y[idx])
    if A is None:
        return np.array([]), np.array([])
    
    xmin = x.max() if start_x is None else min(start_x, x.max())
    xmax = x.min()

    xs = np.linspace(xmin, xmax, n_pts)
    yhat = -A * np.exp(b * xs)

    if clip_to_data:
        # Prevent curve from exceeding experimental data
        yref = np.interp(xs, x, y)
        yhat = np.minimum(yhat, yref)

    return xs, yhat


def plotCVs(cvs, title="", areacm2=1.0, redline=0.0,
            labels=None,
            show_lower_exp=False, n_peaks=5, peak_distance=50, peak_prominence=None,
            startx=None, cliptodata=False,
            scatter=False, scatter_kwargs=None):
    """
    Plots one or multiple CVs with optional exponential fits and customization.
    """
    if isinstance(cvs, CV):
        cvs = [cvs]
    n = len(cvs)

    # Default labels if none provided
    if labels is None:
        labels = []
    labels = list(labels) + [f"CV {i+1}" for i in range(len(labels), n)]

    def _pick(val, i, default=None):
        """
        Helper: pick a per-curve parameter from a list or default value.
        """
        if isinstance(val, (list, tuple, np.ndarray)):
            if len(val) == 0:
                return default
            return val[i] if i < len(val) else val[-1]
        return val if val is not None else default

    if scatter_kwargs is None:
        scatter_kwargs = {}

    plt.figure()
    for i, cv in enumerate(cvs):
        jd = np.asarray(cv.amps, float) / float(areacm2)  # Convert to current density if area given
        lbl = labels[i]

        use_scatter = _pick(scatter, i, False)
        if use_scatter:
            plt.scatter(cv.volts, jd, label=lbl, **scatter_kwargs)
        else:
            plt.plot(cv.volts, jd, label=lbl)

        if show_lower_exp:
            n_peaks_i   = _pick(n_peaks, i, 5)
            peak_dist_i = _pick(peak_distance, i, 50)
            prom_i      = _pick(peak_prominence, i, None)
            startx_i    = _pick(startx, i, None)
            clip_i      = _pick(cliptodata, i, False)

            xs2, yh2 = _lower_peaks_exp_curve(
                cv.volts, jd,
                n_peaks=n_peaks_i,
                distance=peak_dist_i,
                prominence=prom_i,
                n_pts=600,
                clip_to_data=clip_i,
                start_x=startx_i
            )
            if hasattr(xs2, "size") and xs2.size:
                plt.plot(xs2, yh2, label=f"{lbl} Fit")

    if redline != 0:
        plt.axhline(y=redline, color='r', linestyle='--',
                    label=f'Redline at {redline:g} A/cm²')

    plt.xlabel("Voltage [V]")
    plt.ylabel("Current density [A/cm²]" if areacm2 != 1.0 else "Current [A]")
    plt.title(title)
    plt.grid(True)
    plt.legend()
    plt.tight_layout()
    plt.show()
