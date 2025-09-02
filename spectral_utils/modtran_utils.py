import pandas as pd
import re, os
from io import StringIO
import matplotlib.pyplot as plt
import json


#--- MODTRAN utils

def open_tp7_file(filepath):

    #--- Set up for a fixed-width file
    col_names = ['FREQ', 'TOT_TRANS', 'THRML_EM', 'THRML_SCT', 'SURF_EMIS', 'MULT_SCAT', 
        'SING_SCAT', 'GRND_RFLT', 'DRCT_RFLT', 'TOTAL_RAD', 'REF_SOL', 'SOL@OBS', 'DEPTH', 
        'DIR_EM', 'TOA_SUN', 'BBODY_T[K]']
    col_widths = [8, 11, 11, 11, 11, 11, 11, 11, 11, 11, 11, 9, 6, 7, 11, 11]

    df = pd.read_fwf(filepath, widths=col_widths, names=col_names, skiprows=11)

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

def _plot_continuous(ax, df, df_name, color='black'):
    x = 10000/df['FREQ']
    y = df['BBODY_T[K]']
    ax.plot(x, y, color=color, linewidth=1, label=df_name)
    return

def _plt_labels(ax):
    #ax.set_title(f"MODTRAN {fig_name}")
    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("Temperature (K)")
    ax.legend(loc="upper right")
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

    fig, ax = plt.subplots(figsize=(10, 5))

    df1_range = _filter_freq_to_range(df1, freq_range[0], freq_range[1])
    _plot_continuous(ax, df1_range, df1_name, color='blue')
    if df2:
        df2_range = _filter_freq_to_range(df2, freq_range[0], freq_range[1])
        _plot_continuous(ax, df2_range, df2_name, color='red')

    _plt_labels(ax)
    _plt_save(fig_dir, fig_name)

    return

def plot_btd_freq_range(df, df_name='', 
    fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot',
    freq_range1=None, freq_range2=None):

    fig, ax = plt.subplots(figsize=(10, 5))

    df_range1 = _filter_freq_to_range(df, freq_range1[0], freq_range1[1])
    _plot_continuous(ax, df_range1, df_name, color='black')

    ax2 = ax.twiny()
    df_range2 = _filter_freq_to_range(df, freq_range2[0], freq_range2[1])
    _plot_continuous(ax2, df_range2, df_name=None, color='black')
    
    
    _plt_labels(ax)
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