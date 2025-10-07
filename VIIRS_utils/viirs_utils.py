import os
import xarray as xr
import h5py
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
from MODTRAN_utils import modtran_utils as m_utils
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

def print_viirs_file_attrs(file_path, dataset):
    """
    dataset should look like: "Data_Products/VIIRS-M12-SDR/VIIRS-M12-SDR_Gran_0"
    """
    with h5py.File(file_path, "r") as f:
        obj = f[dataset]

        if len(obj.attrs) > 0:
            print(f"Attributes of {obj.name}:")
            for key, value in obj.attrs.items():
                print(f"  {key}: {value}")
        else: print("No attributes found")
    return

def open_viirs_brightness_temp(file_path, band):
    with h5py.File(file_path, 'r') as f:
        bt = f['All_Data'][f'VIIRS-{band.upper()}-SDR_All']['BrightnessTemperature'][()]
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

    da = _replace_viirs_fill_values(da)
    da = _apply_scale_and_offset(file_path, band, da)

    return da

def _replace_viirs_fill_values(da):
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

    #--- Remove the error codes in data and coordinates
    for code, desc in fill_value_dict.items():
        coord_mask = (
            np.isclose(clean_da["Latitude"], code) |
            np.isclose(clean_da["Longitude"], code)
        )
        clean_da = clean_da.where(~coord_mask, np.nan)
        clean_da = clean_da.assign_coords(
            Latitude=clean_da["Latitude"].where(~coord_mask, np.nan),
            Longitude=clean_da["Longitude"].where(~coord_mask, np.nan),
        )
        summary[desc] = int(coord_mask.sum())

    #--- Drop the NaN values, pcolormesh doesn't work with them
    valid = np.isfinite(clean_da["Latitude"]) & np.isfinite(clean_da["Longitude"])
    clean_da = clean_da.where(valid, drop=True)

    print("--- Following error codes removed ---")
    for desc, count in summary.items():
        if count > 0:
            print(f"{desc}: {count} occurrences")

    return clean_da

def _apply_scale_and_offset(file_path, band, da):

    with h5py.File(file_path, "r") as f:
        scale, offset = f['All_Data'][f'VIIRS-{band.upper()}-SDR_All']['BrightnessTemperatureFactors'][()][0:2]
        print(f"Identified scale and offset as {scale}, {offset}")
        clean_da = da * scale + offset
    
    return clean_da


def plot_viirs_data(da, plot_dir, plot_name, plot_title, extent=None):
    """
    extent: [west, east, south, north]
    """
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12), subplot_kw={'projection': projection})
    
    cmap = mcolors.LinearSegmentedColormap.from_list(
        "custom_cmap",
        [(0, "#06BA63"), (0.5, "black"), (1, "white")]
    )
    norm = mcolors.TwoSlopeNorm(vmin=-6, vcenter=0, vmax=1.5)

    pcm = plt.pcolormesh(da["Longitude"], da["Latitude"], da, cmap=cmap, norm=norm, shading="nearest")

    clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('(K)', fontsize=15)
    
    if extent: ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.set_title(plot_title, fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

    m_utils._plt_save(plot_dir, plot_name)
    return

def open_dnb_radiance(file_path):
    with h5py.File(file_path, 'r') as f:
        bt = f['All_Data']['VIIRS-DNB-SDR_All']['Radiance'][()]
        lat = f['All_Data']['VIIRS-DNB-GEO_All']['Latitude'][()]
        lon = f['All_Data']['VIIRS-DNB-GEO_All']['Longitude'][()]

        da = xr.DataArray(
            bt,
            dims=["y", "x"],
            coords={
                "Latitude": (("y", "x"), lat),
                "Longitude": (("y", "x"), lon)
            },
            name="Radiance"
        )

    da = _replace_viirs_fill_values(da)

    return da

def plot_dnb_radiance(da, plot_dir, plot_name, plot_title, extent=None):
    """
    extent: [west, east, south, north]
    """
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12), subplot_kw={'projection': projection})
    
    cmap = "binary_r"
    pcm = plt.pcolormesh(da["Longitude"], da["Latitude"], da, cmap=cmap, shading="nearest", vmin=0.5e-9, vmax=9e-9)

    clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('Radiance (W cm$^{-2}$ sr$^{-1}$)', fontsize=15)

    if extent: ax.set_extent(extent, crs=ccrs.PlateCarree())
    ax.set_title(plot_title, fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

    m_utils._plt_save(plot_dir, plot_name)
    return

def plot_viirs_srf(srf_file):
    """
    Using sensor response function file downloaded from https://ncc.nesdis.noaa.gov/VIIRS/VIIRSSpectralResponseFunctions.php
    """
    srf = np.loadtxt(srf_file)
    x = srf[:, 0]/1000
    y = srf[:, 1]
    band_str = f'VIIRS Band {srf_file.split("_")[7]}'

    plt.plot(x, y, color='black', linewidth=1)
    plt.xlabel('Wavelength (µm)')
    plt.ylabel('Response')
    plt.title(f'{band_str} \n NG Band-Averaged RSRs')

    m_utils._plt_save("VIIRS_spectral_response_functions", f'srf_{band_str.lower().replace(" ", "_")}')
    return