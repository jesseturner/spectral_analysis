import pandas as pd
import numpy as np
import subprocess

#--- MODTRAN utils

def open_tp7_file(filepath):
    #--- Set up for a fixed-width file
    col_names = ['FREQ', 'TOT_TRANS', 'THRML_EM', 'THRML_SCT', 'SURF_EMIS', 'MULT_SCAT', 
        'SING_SCAT', 'GRND_RFLT', 'DRCT_RFLT', 'TOTAL_RAD', 'REF_SOL', 'SOL@OBS', 'DEPTH', 
        'DIR_EM', 'TOA_SUN', 'BBODY_T[K]']
    col_widths = [8, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 9, 6, 7, 11, 11]
    df = pd.read_fwf(filepath, widths=col_widths, names=col_names, skiprows=11)

    return df

def open_7sc_file(filepath):
    #--- Set up for a fixed-width file
    col_names = ['FREQ', 'TOT_TRANS', 'THRML_EM', 'THRML_SCT', 'SURF_EMIS', 'MULT_SCAT', 
        'SING_SCAT', 'GRND_RFLT', 'DRCT_RFLT', 'TOTAL_RAD', 'REF_SOL', 'SOL@OBS', 'DEPTH', 
        'DIR_EM', 'TOA_SUN', 'BBODY_T[K]']
    col_widths = [12, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 9, 6, 7, 11, 11]
    df = pd.read_fwf(filepath, widths=col_widths, names=col_names, skiprows=11,
        skipfooter=1, engine="python")

    return df

def run_modtran(json_path):
    '''
    MODTRAN is set up on jpss-cloud6 machine
    '''
    result = subprocess.run(["/home/jturner/modtran6/bin/linux/mod6c_cons", json_path])
    print(result.stdout)
    print(result.stderr)
    print(result.returncode)
    return

def planck_lambda(T, wavelength):
    """
    Get spectral radiance from temperature and wavelength. 
    ----------
    wavelength : [m]
    """
    h = 6.62607015e-34
    c = 299792458.0
    k = 1.380649e-23
    a = 2*h*c**2 / wavelength**5
    x = h*c/(wavelength*k*T)
    B = a / (np.exp(x)-1.0)
    return B

def reverse_planck_lambda(radiance, wavelength):
    """
    Convert spectral radiance (per wavelength) to brightness temperature.
    ----------
    radiance : float or np.ndarray
        Spectral radiance [W / (m²·sr·m)]
        ~1e5 for shortwave IR, ~1e6 for longwave IR
    wavelength : float or np.ndarray
        Wavelength [m]
    """
    
    c = 2.99792458e8       # speed of light [m/s]
    h = 6.62607015e-34     # Planck constant [J·s]
    k = 1.380649e-23       # Boltzmann constant [J/K]
    lam = wavelength
    L_lambda = radiance
    
    numerator = h * c
    denominator = lam * k * np.log((2 * h * c**2) / (L_lambda * lam**5) + 1)
    
    T = numerator / denominator
    return T