from typing import List, Optional, Dict, Any, Tuple

import numpy as np
import matplotlib.pyplot as plt
from impedance.visualization import plot_nyquist
from impedance import preprocessing
from impedance.models.circuits import CustomCircuit
from impedance.models.circuits.fitting import wrapCircuit
from impedance.visualization import plot_nyquist
from scipy.optimize import curve_fit
import os
import numpy as np
from typing import Optional, Tuple
from typing import Optional, Tuple
import numpy as np


def convert_biologic_peis_in_memory(
    input_file: str,
    skiprows: int = 1,
    delimiter_in: Optional[str] = None,
    biologic_format: str = "f,-im,re",
    return_converted_table: bool = False
) -> Tuple[np.ndarray, np.ndarray] | Tuple[np.ndarray, np.ndarray, np.ndarray]:
    """
    Loads BioLogic PEIS export and converts it in memory to impedance.py format.

    Supported BioLogic formats:
    - "f,-im,re"  (your case: Frequency, -Im(Z), Re(Z))
    - "f,re,im"   (classic: Frequency, Re(Z), Im(Z))
    - "f,re,-im"  (Frequency, Re(Z), -Im(Z))

    Returns
    -------
    freqs : np.ndarray
    Z : np.ndarray (complex, for fitting)
    table (optional) : Nx3 (Frequency, Re(Z), -Im(Z))
    """

    data = np.loadtxt(input_file, skiprows=skiprows, delimiter=delimiter_in)

    if data.shape[1] < 3:
        raise ValueError(f"Expected at least 3 columns, got {data.shape[1]}")

    f = data[:, 0]

    if biologic_format.lower() == "f,-im,re":
        minus_im = data[:, 1]
        re = data[:, 2]
        im = -minus_im              # convert -Im -> Im
        Z = re + 1j * im
        table = np.column_stack([f, re, minus_im])  # Frequency, Re, -Im (exactly your 'nachher')

    elif biologic_format.lower() == "f,re,im":
        re = data[:, 1]
        im = data[:, 2]
        Z = re + 1j * im
        table = np.column_stack([f, re, -im])

    elif biologic_format.lower() == "f,re,-im":
        re = data[:, 1]
        minus_im = data[:, 2]
        im = -minus_im
        Z = re + 1j * im
        table = np.column_stack([f, re, minus_im])

    else:
        raise ValueError(
            f"Unknown biologic_format='{biologic_format}'. Use one of: "
            "'f,-im,re', 'f,re,im', 'f,re,-im'"
        )

    if return_converted_table:
        return f, Z, table

    return f, Z

def get_arc_diameters(params: np.ndarray, param_names: List[str]) -> Dict[str, float]:
    """
    Extract arc diameters from fitted parameters.
    Arc diameter = resistance of each R in a parallel R||C or R||CPE branch.

    Parameters
    ----------
    params : np.ndarray
        Array of fitted parameter values (from circuit.parameters_).
    param_names : list of str
        Names of parameters, aligned with `params`.

    Returns
    -------
    dict
        Dictionary mapping each R_k (except R_0) to its arc diameter.
    """
    arc_dict = {}

    for name, val in zip(param_names, params):
        if name.startswith("R_") and name != "R_0":
            arc_dict[name] = float(val)

    return arc_dict



def fit_and_plot_eis(
    frequencies: np.ndarray,
    Z: np.ndarray,
    circuit,
    param_names: Optional[List[str]] = None,
    ax: Optional[plt.Axes] = None,
    title: str = "Nyquist Plot: Experimental Data vs. Custom Circuit Fit",
    print_results: bool = True,
    show: bool = True,
) -> Dict[str, Any]:
   
    # ------------------------------------------------------------------
    # 1) Fit the model parameters to the impedance data
    # ------------------------------------------------------------------
    circuit.fit(frequencies, Z)

    # Predicted impedance values from the fitted circuit
    Z_fit = circuit.predict(frequencies)

    # Extract optimized parameters
    params = np.array(circuit.parameters_)

    # Determine parameter names if not explicitly given
    if param_names is None:
        if hasattr(circuit, "parameter_names_"):
            param_names = list(circuit.parameter_names_)
        else:
            param_names = [f"p{i}" for i in range(len(params))]

    # ------------------------------------------------------------------
    # 2) Compute fit quality (RMSE)
    # ------------------------------------------------------------------
    residuals = Z - Z_fit
    rmse = float(np.sqrt(np.mean(np.abs(residuals) ** 2)))

    # ------------------------------------------------------------------
    # 3) Print results (optional)
    # ------------------------------------------------------------------
    if print_results:
        print("=== Fit Results ===")
        for name, val in zip(param_names, params):
            print(f"{name:6s} = {val:.4e}")
        print(f"\nRMSE = {rmse:.3e} Ohm\n")

    # ------------------------------------------------------------------
    # 4) Nyquist plot (data vs. fit)
    # ------------------------------------------------------------------
    created_fig = False
    if ax is None:
        fig, ax = plt.subplots(figsize=(6, 5))
        created_fig = True
    else:
        fig = ax.figure

    # Experimental impedance data
    plot_nyquist(Z, ax=ax, fmt='o', markersize=4, label='Data')

    # Fitted impedance response
    plot_nyquist(Z_fit, ax=ax, fmt='-', linewidth=2, label='Fit')

    ax.set_xlabel(r"$Z'(\omega)\ [\Omega]$")
    ax.set_ylabel(r"$-Z''(\omega)\ [\Omega]$")
    ax.set_title(title)
    ax.legend()
    ax.grid(True, alpha=0.3)

    fig.tight_layout()

    if show and created_fig:
        plt.show()

    # ------------------------------------------------------------------
    # 5) Return everything useful to the caller
    # ------------------------------------------------------------------
    return {
        "params": params,
        "rmse": rmse,
        "Z_fit": Z_fit,
        "frequencies": frequencies,
        "fig": fig,
        "ax": ax,
    }
