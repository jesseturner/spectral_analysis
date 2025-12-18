import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import os
import numpy as np

def open_gxs_data(filepath):
    '''
    Dimensions: 
        number_channels: 2402,
        num_scan_line: 615, (y)
        num_fov_per_scan_line: 1201, (x)
        number_layers: 137 (only for profile retrievals)
    '''
    ds = xr.open_dataset(filepath)
    return ds

def _plt_save(fig_dir, fig_name):
    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

def plot_Tb_CLD(ds, channel_index, plot_title, plot_dir, plot_name):
    '''
    Plotting Cloudy Brightness Temperature. 
    
    :param channel_index: between 0 and 2402
    :param freq: between 2252.26 and 680.09 cm-1
    :param ds: from open_gxs_data()
    '''

    freq = ds['freq'][channel_index].values.item()
    print(f"Frequency of {round(freq,2)} cm-1 ({round(10_000/freq, 2)} um)")

    img = ds['Tb_CLR'][channel_index, :, :]
    img = img.where(img != -19998) #--- Missing values to NaNs

    x = img['num_fov_per_scan_line'].values
    y = img['num_scan_line'].values
    z = img.values

    fig, ax = plt.subplots(figsize=(10, 6))

    pcm = ax.pcolormesh(
        x, y, z,
        cmap='Greys',
        shading='nearest'
    )

    clb = fig.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.set_label('Brightness Temperature (K)', fontsize=15)
    clb.ax.tick_params(labelsize=15)
    ax.invert_yaxis()

    ax.set_xlabel('FOV per scan line', fontsize=15)
    ax.set_ylabel('Scan line', fontsize=15)
    ax.set_title(f'{plot_title}\n {round(freq,2)} cm$^{-1}$ ({round(10_000/freq, 2)} µm)')

    _plt_save(plot_dir, f'{plot_name}_{round(freq)}')
    return