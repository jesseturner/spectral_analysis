import pandas as pd
import re, os
from io import StringIO
import matplotlib.pyplot as plt


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

def filter_freq_to_range(df, range_start, range_end):
    filtered_df = df[((df["FREQ"] >= range_start) & (df["FREQ"] <= range_end))]
    return filtered_df

def plot_bt_dual_ranges(df1, df2=None, fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot',
    df1_name='', df2_name='', range1=None, range2=None):

    fig, ax = plt.subplots(figsize=(10, 5))

    _plot_continuous(ax, df1, df1_name, color='blue')
    _plot_continuous(ax, df2, df2_name, color='red')

    _plt_labels(ax)
    _plt_save(fig_dir, fig_name)

    return