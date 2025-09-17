import os
import xarray as xr
import h5py
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
from spectral_utils import modtran_utils as m_utils
import numpy as np

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

        da = xr.DataArray(
            bt,
            dims=["y", "x"],
            coords={
                "Latitude": (("y", "x"), lat),
                "Longitude": (("y", "x"), lon)
            },
            name="Brightness Temperature"
        )

    return da

def replace_viirs_fill_values(da):
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

    clean_da = da.copy()
    summary = {}

    for code, desc in fill_value_dict.items():
        mask = (da == code) | np.isclose(da["Latitude"], code) | np.isclose(da["Longitude"], code)
        clean_da = clean_da.where(~mask, np.nan)
        summary[desc] = int(mask.sum())

    for desc, count in summary.items():
        if count > 0:
            print(f"{desc}: {count} occurrences")

    return clean_da


def plot_viirs_data(da):
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12), subplot_kw={'projection': projection})
    cmap = plt.cm.coolwarm

    #pcm = ax.imshow(da, cmap=cmap)
    pcm = plt.pcolormesh(da["Longitude"], da["Latitude"], da, shading='auto', cmap=cmap)

    # clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    # clb.ax.tick_params(labelsize=15)
    # clb.set_label('(K)', fontsize=15)

    #--- Maybe incorporate this into the validation function?
    #------ However, need to make sure shapes still line up
    valid_mask = np.isfinite(da)
    lat_valid = da["Latitude"].where(valid_mask)
    lon_valid = da["Longitude"].where(valid_mask)

    ax.set_extent([np.min(lon_valid), np.max(lon_valid), np.min(lat_valid), np.max(lat_valid)], crs=ccrs.PlateCarree())
    ax.set_title("VIIRS brightness temperature", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

    m_utils._plt_save("VIIRS_plot", "viirs_example")
    return

