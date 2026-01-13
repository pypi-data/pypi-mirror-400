import pandas as pd
import numpy as np
from scipy.ndimage import gaussian_filter1d

import matplotlib.pyplot as plt

class CP:
    def __init__(self, timepoints, volts):
        self.timepoints = timepoints
        self.volts = volts


def loadBioLogicCP(filePath, absoluteTime=False) -> CP:
    df = pd.read_csv(filePath, sep="\t", decimal=".")
    column_order = ["time/s", "Ewe/V"]

    missing_cols = [col for col in column_order if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")

    # convert date time
    # df['time/s'] = pd.to_datetime(df['time/s'], format="%m/%d/%Y %H:%M:%S.%f")
    # df['time/s'] = df['time/s'].astype('int64') // 10**9

    df_reordered = df[column_order]
    matrix = df_reordered.to_numpy()

    if not absoluteTime:
        firstTimepoint = matrix[0,0]
        matrix[:,0] -= firstTimepoint
    
    cp = CP(matrix[:,0], matrix[:,1])
    return cp

def loadSquidstatCP(filePath) -> CP:
    df = pd.read_csv(filePath, sep=",", decimal=".")
    column_order = ["Elapsed Time (s)", "Counter Electrode (V)"]

    missing_cols = [col for col in column_order if col not in df.columns]
    if missing_cols:
        raise ValueError(f"Columns not found in CSV: {missing_cols}")
    
    df_reordered = df[column_order]
    matrix = df_reordered.to_numpy()

    cp = CP(matrix[:,0], matrix[:,1])
    return cp


def plotCPs(cps: list[CP], title="", smoothen=True, smoothenGaussSigma=400):
    # firstTimepoint = cps[0].timepoints[0]

    lastTimePointH = 0

    for cp in cps:
        timepoints = cp.timepoints/3600 + lastTimePointH
        plt.scatter(timepoints, cp.volts, s=0.5, color="lightgrey", label="raw data")
        lastTimePointH = timepoints[-1]

        if smoothen:
            smoothVolts = gaussian_filter1d(cp.volts, smoothenGaussSigma)
            plt.plot(timepoints, smoothVolts, color="#CC1719", linewidth=1, label="smoothened data")

    plt.title(title)
    plt.xlabel("Time [h]")
    plt.ylabel("Potential [V]")
    plt.show()