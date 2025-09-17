import os
import xarray as xr
import h5py
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from spectral_utils import modtran_utils as m_utils
import numpy as np
import pandas as pd

def print_viirs_file_metadata(file_path):
    with h5py.File(file_path, "r") as f:
        #--- this visits every item in the HDF5 file
        f.visititems(_print_h5_structure)
    return

def _print_h5_structure(name, obj):
    if isinstance(obj, h5py.Dataset):
        print(f"Dataset: {name} | shape: {obj.shape} | dtype: {obj.dtype}")
    elif isinstance(obj, h5py.Group):
        print(f"Group: {name}")
    return

def print_viirs_file_attrs(file_path):
    with h5py.File(file_path, "r") as f:
        obj = f["Data_Products/VIIRS-M12-SDR/VIIRS-M12-SDR_Gran_0"]

        if len(obj.attrs) > 0:
            print(f"Attributes of {obj.name}:")
            for key, value in obj.attrs.items():
                print(f"  {key}: {value}")
        else: print("No attributes found")
    return

def open_viirs_file(file_path):
    with h5py.File(file_path, 'r') as f:
        bt = f['All_Data']['VIIRS-M12-SDR_All']['BrightnessTemperature'][()]
        lat = f['All_Data']['VIIRS-MOD-GEO-TC_All']['Latitude'][()]
        lon = f['All_Data']['VIIRS-MOD-GEO-TC_All']['Longitude'][()]

        data = {
            "Latitude": np.array(lat).flatten(), 
            "Longitude": np.array(lon).flatten(),
            "Brightness Temperature": np.array(bt).flatten(),
            }
        df = pd.DataFrame(data)
    
    return df

def replace_viirs_fill_values(df):
    fill_value_dict = {
        65535: "N/A (16-bit)",
        65534: "MISS (16-bit)",
        65533: "OBPT (16-bit)",
        65532: "OGBT (16-bit)",
        65531: "ERR (16-bit)", 
        65530: "ELINT (16-bit)",
        65529: "VDNE (16-bit)",
        65528: "SOUB (16-bit)",
        -999.9: "N/A (32-bit)",
        -999.8: "MISS (32-bit)",
        -999.7: "OBPT (32-bit)",
        -999.6: "OGPT (32-bit)", 
        -999.5: "ERR (32-bit)",
        -999.4: "ELINT (32-bit)",
        -999.3: "VDNE (32-bit)",
        -999.2: "SOUB (32-bit)"
    }

    clean_df = df.copy()
    summary = {}

    for code, desc in fill_value_dict.items():
        mask = (df["Brightness Temperature"] == code) | np.isclose(df["Latitude"], code) | np.isclose(df["Longitude"], code)
        clean_df[mask] = np.nan
        count = np.sum(mask)
        summary[desc] = count

    for desc, count in summary.items():
        print(f"{desc}: {count} occurrences")

    return clean_df


def plot_viirs_data(df):
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12), subplot_kw={'projection': projection})
    cmap = plt.cm.coolwarm

    mask = (lat == -999.3) | (lon == -999.3)
    data = np.ma.array(data, mask=mask) 
    print(np.max(data), np.min(data))

    #--- Can handle 2D lat lon coordinates
    pcm = plt.pcolormesh(lon, lat, data, shading='auto', cmap=cmap)
    #pcm = ax.imshow(data)

    clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('(K)', fontsize=15)

    ax.set_title("VIIRS brightness temperature", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

    m_utils._plt_save("VIIRS_plot", "viirs_example")
    return

