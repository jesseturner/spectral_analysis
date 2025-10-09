import pandas as pd
import re, os
from io import StringIO
import matplotlib.pyplot as plt
import json
import xarray as xr
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

def plot_bt(df, df_name='', fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot'):
    
    fig, ax = plt.subplots(figsize=(10, 5))

    _plot_continuous(ax, df, df_name, color='black')

    _plt_labels(ax)
    _plt_save(fig_dir, fig_name)

    return

def plot_bt_dual(df1, df2, df1_name='', df2_name='', fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot'):
    
    fig, ax = plt.subplots(figsize=(10, 5))

    _plot_continuous(ax, df1, df1_name, color='blue')
    _plot_continuous(ax, df2, df2_name, color='red')

    _plt_labels(ax)
    _plt_save(fig_dir, fig_name)

    return

def _plot_continuous(ax, df, df_name=None, color='black'):
    x = 10000/df['FREQ']
    y = df['BBODY_T[K]']
    ax.plot(x, y, color=color, linewidth=1, label=df_name)
        
    return

def _plt_labels(ax, ylim=None):
    '''
    ylim: tuple like (270, 291)
    '''
    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("Temperature (K)")
    #--- Only create legend if the labels are defined
    handles, labels = ax.get_legend_handles_labels()
    if handles:
        ax.legend(loc="upper right")
    if ylim:
        ax.set_ylim(ylim)
    return

def _plt_save(fig_dir, fig_name):
    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

def _filter_freq_to_range(df, range_start, range_end):
    filtered_df = df[((df["FREQ"] >= range_start) & (df["FREQ"] <= range_end))]
    return filtered_df

def plot_bt_dual_freq_range(df1, df2=None, df1_name='', df2_name='', 
    fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot',
    freq_range=None):
    """
    Comparing two different cases of the same spectra range.
    """
    fig, ax = plt.subplots(figsize=(10, 5))

    df1_range = _filter_freq_to_range(df1, freq_range[0], freq_range[1])
    _plot_continuous(ax, df1_range, df1_name, color='blue')
    if df2:
        df2_range = _filter_freq_to_range(df2, freq_range[0], freq_range[1])
        _plot_continuous(ax, df2_range, df2_name, color='red')

    _plt_labels(ax)
    _plt_save(fig_dir, fig_name)

    return

def plot_btd_freq_range(df, title_name='', 
    fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot',
    freq_range1=None, freq_range2=None, ylim=None):
    """
    Visualizing the brightness temperature difference between two different spectra ranges.
    freq_range format: [2430, 2555]
    ylim: tuple like (271, 280)
    """

    fig, ax = plt.subplots(figsize=(10, 5))

    df_range1 = _filter_freq_to_range(df, freq_range1[0], freq_range1[1])
    _plot_continuous(ax, df_range1, color="blue")
    ax.xaxis.label.set_color("blue")
    ax.tick_params(axis="x", colors="blue")

    ax2 = ax.twiny()
    df_range2 = _filter_freq_to_range(df, freq_range2[0], freq_range2[1])
    _plot_continuous(ax2, df_range2, color="red")
    ax2.xaxis.label.set_color("red")
    ax2.tick_params(axis="x", colors="red")
    
    ax.set_title(f"MODTRAN {title_name}")
    _plt_labels(ax, ylim=ylim)
    _plt_save(fig_dir, fig_name)

    return

def read_wyo_radiosonde_rtf_file(filepath):
    #--- Set up for a fixed-width file
    col_names = ['PRES', 'HGHT', 'TEMP', 'DWPT', 'RELH', 'MIXR', 'DRCT', 'SKNT', 'THTA', 'THTE', 'THTV']
    col_widths = [7]*len(col_names)

    df = pd.read_fwf(filepath, widths=col_widths, names=col_names, skiprows=16, skipfooter=32)
    return df

def build_modtran_custom_json(df):
    press_json = df["PRES"].tolist()
    temp_k_json = (round(df["TEMP"] + 273.15, 2)).tolist()
    water_vapor_ppmv_json = (round(df["MIXR"]* 1.607e3, 2)).tolist()
    return press_json, temp_k_json, water_vapor_ppmv_json

def plot_custom_json(filepath):
    with open(filepath, "r") as f:
        data = json.load(f)

    profiles = data["MODTRAN"][0]["MODTRANINPUT"]["ATMOSPHERE"]["PROFILES"]

    pressure = profiles[0]["PROFILE"]  # millibar
    temperature = profiles[1]["PROFILE"]  # Kelvin
    h2o = profiles[2]["PROFILE"]  # ppmv

    fig, ax1 = plt.subplots(figsize=(6, 8))

    ax1.plot(temperature, pressure, "r-", label="Temperature (K)")
    ax1.set_xlabel("Temperature (K)", color="r")
    ax1.tick_params(axis="x", labelcolor="r")
    ax1.set_ylabel("Pressure (mbar)")
    ax1.invert_yaxis()  # Pressure decreasing with altitude

    ax2 = ax1.twiny()
    ax2.plot(h2o, pressure, "b-", label="H2O (ppmv)")
    ax2.set_xlabel("H2O (ppmv)", color="b")
    ax2.tick_params(axis="x", labelcolor="b")

    plt.title("MODTRAN Format Temperature & H2O")
    ax1.grid(True, linestyle="--", alpha=0.6)

    _plt_save("MODTRAN_json", "custom_atmosphere")
    return 

def profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat, lon):
    gfs_t, gfs_q, gfs_p = _read_gfs_point(gfs_filepath, lat, lon)
    sst = _read_sst_point(sst_filepath, lat, lon)

    profile_p = np.insert(gfs_p, 0, 1020) #--- Lower pressure level added
    profile_t = np.insert(gfs_t, 0, sst)
    profile_q = np.insert(gfs_q, 0, gfs_q[0]) #--- Repeated because lengths must match

    data = {
        "Pressure (hPa)": profile_p, 
        "Temperature (K)": profile_t,
        "Specific Humidity (kg/kg)": profile_q,
    }

    df = pd.DataFrame(data)
    return df

def plot_skew_t_from_profile(df, title, fig_dir, fig_name):
    """
    Using the result from profile_from_gfs_and_sst(), plot the skew-t. 
    """
    from metpy.plots import SkewT
    from metpy.units import units
    from metpy.calc import dewpoint

    pressure = df["Pressure (hPa)"].to_numpy() * units.hPa
    #--- Converting from specific humidity to dewpoint
    specific_humidity = df["Specific Humidity (kg/kg)"].to_numpy()
    mixing_ratio = specific_humidity / (1 - specific_humidity)
    vapor_pressure = (mixing_ratio * pressure) / (0.622 + mixing_ratio)
    dewpoints = dewpoint(vapor_pressure)
    #--- Temperature in C
    temps_K = df["Temperature (K)"].to_numpy() * units.degK
    temps_C = temps_K.to(units.degC)    


    fig = plt.figure(figsize=(9, 9))
    skew = SkewT(fig, aspect=220, rotation=0)

    skew.plot(pressure, temps_C, 'k', label='Temperature')
    skew.plot(pressure, dewpoints, 'k', label='Dewpoint')

    skew.plot_dry_adiabats(colors='lightgray')
    skew.plot_moist_adiabats(colors='lightgray')
    skew.plot_mixing_lines(colors='lightgray')

    skew.ax.set_ylim(1050, 700)
    skew.ax.set_yticks(np.arange(1000, 700 - 1, -50))
    skew.ax.set_xlim(-20, 30)
    skew.ax.set_xlabel('Temperature (C)', size=18, labelpad=10)
    skew.ax.set_ylabel('Pressure (hPa)', size=18)
    skew.ax.tick_params(axis='both', which='major', labelsize=14)

    skew.ax.set_title(title, size=18, pad=10)
    _plt_save(fig_dir, fig_name)
    return


def _read_gfs_point(filepath, lat, lon):
    gfs_ds = xr.open_dataset(filepath, engine="cfgrib",backend_kwargs={'filter_by_keys': {'typeOfLevel':'isobaricInhPa'}})
    point = gfs_ds.sel(latitude=lat, longitude=lon+360, method='nearest')
    print(f"GFS coordinates selected: {point.latitude.values}, {point.longitude.values}")
    
    #---GFS 2m height (opened separately)
    gfs_2m = xr.open_dataset(filepath, engine="cfgrib",backend_kwargs={'filter_by_keys':{'typeOfLevel': 'heightAboveGround','level':2}})
    point_2m = gfs_2m.sel(latitude=lat, longitude=lat, method='nearest')

    gfs_p = point.isobaricInhPa.values
    gfs_p = np.insert(gfs_p, 0, 1010)

    gfs_t = point.t.values
    gfs_t = np.insert(gfs_t, 0, point_2m.t2m.values)

    gfs_q = point.q.values
    gfs_q = np.insert(gfs_q, 0, point_2m.sh2.values)

    return gfs_t, gfs_q, gfs_p

def _read_sst_point(filepath, lat, lon):
    sst_ds = xr.open_dataset(filepath)
    sst_ds =  sst_ds.squeeze()
    sst_ds.sst.values = sst_ds.sst.values+273.15
    surface = sst_ds.sel(lat=lat, lon=lon+360, method='nearest')
    print(f"SST coordinates selected: {surface.lat.values}, {surface.lon.values}")
    return surface.sst.values

def create_modtran_json_from_df(df, json_path):
    water_vapor = _q_to_ppmv(df["Specific Humidity (kg/kg)"]).tolist()
    temperature = df["Temperature (K)"].tolist()
    pressure = df["Pressure (hPa)"].tolist()

    n_layers = len(pressure)

    modtran_dict = {
        "MODTRAN": [
            {
                "MODTRANINPUT": {
                    "NAME": "flc_custom1",
                    "DESCRIPTION": "",
                    "CASE": 0,
                    "RTOPTIONS": {
                        "MODTRN": "RT_MODTRAN",
                        "LYMOLC": False,
                        "T_BEST": False,
                        "IEMSCT": "RT_THERMAL_ONLY",
                        "IMULT": "RT_NO_MULTIPLE_SCATTER"
                    },
                    "ATMOSPHERE": {
                        "MODEL": "ATM_USER_PRESS_PROFILE",
                        "MDEF": 1,
                        "CO2MX": 0.0,
                        "HMODEL": "New Atm Profile",
                        "NPROF": 3,
                        "NLAYERS": n_layers,
                        "PROFILES": [
                            {
                                "TYPE": "PROF_PRESSURE",
                                "UNITS": "UNT_PMILLIBAR",
                                "PROFILE": pressure
                            },
                            {
                                "TYPE": "PROF_TEMPERATURE",
                                "UNITS": "UNT_TKELVIN",
                                "PROFILE": temperature
                            },
                            {
                                "TYPE": "PROF_H2O",
                                "UNITS": "UNT_DPPMV",
                                "PROFILE": water_vapor
                            }
                        ]
                    },
                    "AEROSOLS": {
                        "IHAZE": "AER_MARITIME",
                        "VIS": 0.0
                    },
                    "GEOMETRY": {},
                    "SURFACE": {
                        "SURFTYPE": "REFL_CONSTANT",
                        "NSURF": 1,
                        "SALBFL": ""
                    },
                    "SPECTRAL": {
                        "V1": 650.0,
                        "V2": 2550.0,
                        "DV": 1.0,
                        "FWHM": 2.0,
                        "YFLAG": "R",
                        "MLFLX": -1
                    },
                    "FILEOPTIONS": {}
                }
            }
        ]
    }

    # --- write JSON file ---
    with open(json_path, "w") as f:
        json.dump(modtran_dict, f, indent=2)

    print(f"MODTRAN JSON saved to {json_path}")

    return

def _q_to_ppmv(q):
    """
    Convert specific humidity (kg/kg) to ppmv for water vapor.
    
    Parameters
    ----------
    q : float or array
        Specific humidity in kg/kg.
    
    Returns
    -------
    ppmv : float or array
        Water vapor concentration in ppmv.
    """
    eps = 0.622  # ratio of molar masses (Mv / Md)
    w = q / (1 - q)                  # mixing ratio (kg/kg dry air)
    x_v = (w / eps) / (1 + w / eps)  # mole fraction of water vapor
    ppmv = x_v * 1e6
    return ppmv

def run_modtran(json_path):
    result = subprocess.run(["/home/jturner/modtran6/bin/linux/mod6c_cons", json_path])
    print(result.stdout)
    print(result.stderr)
    print(result.returncode)
    return

def get_Tb_from_srf(spectra_df, srf_file, central_wl):
    """
    Use MODTRAN spectra and SRF to get brightness temperature.
    
    ----------
    spectra_df : from open_7sc_file()
    srf_file : downloaded .dat file
    central_wl : float in [m]
    """

    #--- Convert spectral steps from cm-1 to µm, flipping direction to match to SRF
    #--- Convert radiance to from wavenumber-based to wavelength-based, using Jacobian conversion
    modtran_wl = np.array(1e4 / spectra_df["FREQ"])[::-1]
    modtran_rad = np.array(spectra_df["TOTAL_RAD"][::-1] * 1e4 / (modtran_wl**2))

    #--- Load SRF, which is in wavelengths and proportions
    srf = np.loadtxt(srf_file)
    srf_wl = np.array(srf[:, 0]/1000) # Convert from nm to µm
    srf_response = np.array(srf[:, 1])

    #--- Interpolate BT onto the SRF wavelength grid
    from scipy.interpolate import interp1d
    interp_rad = interp1d(modtran_wl, modtran_rad, kind='linear', bounds_error=True)
    rad_on_srf = interp_rad(srf_wl)
    #------ Compute the response-weighted average brightness temperature
    #------ Using trapezoid method to estimate the integral of radiance and SRF with respect to wavelength
    #------ Convert radiance to Tb using the central wavelength from VIIRS documentation
    weighted_rad = np.trapz(rad_on_srf * srf_response, srf_wl) / np.trapz(srf_response, srf_wl)
    weighted_rad_m = weighted_rad*1e6*1e4
    Tb = radiance_to_brightness_temp_wavelength(weighted_rad_m, central_wl)

    print(f"Sensor brightness temperature: {Tb:.3f} K")
    return

def radiance_to_brightness_temp_wavelength(radiance, wavelength):
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
    
    T_B = numerator / denominator
    return T_B
