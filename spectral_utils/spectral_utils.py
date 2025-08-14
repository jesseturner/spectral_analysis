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

def plot_brightness_temperature(df, fig_dir, fig_name):
    x = df['FREQ']
    y = df['BBODY_T[K]']

    fig, ax = plt.subplots(figsize=(10, 5))

    ax.plot(x, y, color='blue', linewidth=1)

    #ax.set_title(f"MODTRAN {fig_name}")
    ax.set_xlabel("Wavenumber (cm$^{-1}$)")
    ax.set_ylabel("Temperature (K)")

    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

    return df