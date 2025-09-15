import os
import xarray as xr
import h5py
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from spectral_utils import modtran_utils as m_utils
import numpy as np

def print_viirs_file_metadata(file_path):
    with h5py.File(file_path, "r") as f:
        f.visititems(_print_h5_structure)
    return

def _print_h5_structure(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(f"Dataset: {name} | shape: {obj.shape} | dtype: {obj.dtype}")
    elif isinstance(obj, h5py.Group):
        print(f"Group: {name}")
    return

def open_viirs_file(file_path):
    with h5py.File(file_path, 'r') as f:
        bt = f['All_Data']['VIIRS-M12-SDR_All']['BrightnessTemperature'][()]
        lat = f['All_Data']['VIIRS-MOD-GEO-TC_All']['Latitude'][()]
        lon = f['All_Data']['VIIRS-MOD-GEO-TC_All']['Longitude'][()]
    return bt, lat, lon

def plot_viirs_data(data, lat, lon):
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})
    cmap = plt.cm.coolwarm
    
    #--- Can handle 2D lat lon coordinates
    pcm = plt.pcolormesh(lon, lat, data, shading='auto', cmap=cmap)

    clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('(K)', fontsize=15)

    ax.set_title("VIIRS brightness temperature", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

    m_utils._plt_save("VIIRS_plot", "viirs_example")
    return