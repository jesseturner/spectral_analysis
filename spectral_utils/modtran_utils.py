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

def plot_brightness_temperature(df1, df2=None, fig_dir='MODTRAN_plot', fig_name='MODTRAN_plot',
    df1_name='', df2_name=''):
    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(10000/df1['FREQ'], df1['BBODY_T[K]'], color='blue', linewidth=1, label=df1_name)
    if isinstance(df2, pd.DataFrame): ax.plot(10000/df2['FREQ'], df2['BBODY_T[K]'], color='red', linewidth=1, label=df2_name)

    #ax.set_title(f"MODTRAN {fig_name}")
    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("Temperature (K)")

    if df1_name or df2_name: ax.legend(loc="upper right")

    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

    return

