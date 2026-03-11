#--- 03-05 is still a better version of plotting clavrx than this!

import os
from datetime import datetime
import glob
import xarray as xr
import re
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs
import sys

def main():

    clavrx_dir = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"
    clavrx_date_str = "20260306" #YYYYMMDD
    clavrx_dt = datetime.strptime(clavrx_date_str, "%Y%m%d")
    clavrx_julian_str = clavrx_dt.strftime("%Y%j")
    clavrx_pattern = os.path.join(clavrx_dir, f"{clavrx_julian_str}/*.hdf")

    clavrx_files = glob.glob(clavrx_pattern)
    clavrx_files.sort() 

    print(f"Checking for valid nighttime files from {clavrx_dt.strftime("%Y-%m-%d")}...")
    #--- Still too slow, only checking first 100 files
    clavrx_files_valid = only_valid_nighttime_files(clavrx_files[2040:2043])
    print(f"{len(clavrx_files_valid)}/{len(clavrx_files)} are nighttime and valid...")
    if len(clavrx_files_valid) == 0:
        sys.exit()
    clavrx_files_sample = clavrx_files_valid[:3]
    print(f"Using {len(clavrx_files_sample)}/{len(clavrx_files_valid)} of the valid files...")

    print("Creating combined clavrx dataset...")
    ds_combined, datetime_str = get_clavrx_ds_combined(clavrx_files)
    print(ds_combined)

    da_refl_lunar = get_variable(ds_combined, 'refl_lunar_dnb_nom')
    da_cloud_mask = get_variable(ds_combined, 'cloud_mask')
    
    plot_clavrx_cloud_mask(da_cloud_mask, datetime_str, save_path="clavrx_cloud_mask")
    plot_clavrx_dnb_refl(da_refl_lunar, datetime_str, save_path="clavrx_refl_lunar")

    return

#---------------

def only_valid_nighttime_files(file_list):
    good_files = []
    for f in file_list:
        try:
            with xr.open_dataset(f, engine="netcdf4") as ds:
                ds.load()
                if ds['solar_zenith_angle'].max() > 90: # NIGHTTIME
                    good_files.append(f)
        except Exception as e:
            pass
    return good_files

def get_clavrx_ds_combined(clavrx_files):
    ds_combined = xr.open_mfdataset(
        clavrx_files,
        combine="nested",
        preprocess=fix_dims,
        concat_dim="scan_lines_along_track_direction",
        engine='netcdf4')
    
    start_dt = extract_datetime_from_filename(clavrx_files[0])
    end_dt   = extract_datetime_from_filename(clavrx_files[-1])
    if start_dt and end_dt:
        datetime_str = f"{start_dt} - {end_dt}"
    else:
        datetime_str = "Unknown - File format unexpected."

    return ds_combined, datetime_str

def fix_dims(ds):
    ds = ds.drop_dims("FakeDim1D")
    return ds

def extract_datetime_from_filename(filename):
    match = re.search(r'd(\d{8})_t(\d{6})', filename)

    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2)

    date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}"
    time_formatted = f"{time_part[:2]}:{time_part[2:4]}"

    return f"{date_formatted} {time_formatted}"

def get_variable(ds, var_name):

    da_var = ds[var_name]
    valid = np.isfinite(da_var) & np.isfinite(da_var["latitude"]) & np.isfinite(da_var["longitude"])
    da_var = da_var.where(valid.compute(), drop=True)

    return da_var

def plot_clavrx_cloud_mask(da_cloud_mask, datetime_str, save_path):
    print("Plotting clavr-x cloud mask...")
    plt.style.use('dark_background')
    projection = ccrs.PlateCarree(central_longitude=0)
    fig, ax = plt.subplots(1, figsize=(12,12),
                        subplot_kw={'projection': projection})

    cloud_colors = [
        "#4DA6FF",   # 0 clear
        "#A6E3FF",   # 1 probably clear
        "#BDBDBD",   # 2 probably cloudy
        "#FFFFFF"    # 3 cloudy
    ]
    cloud_cmap = ListedColormap(cloud_colors, name="cloud_mask")
    bounds = np.arange(-0.5, 4.5, 1)
    norm = BoundaryNorm(bounds, cloud_cmap.N)

    step = 6
    sc = ax.scatter(
        da_cloud_mask["longitude"][::step],
        da_cloud_mask["latitude"][::step],
        c=da_cloud_mask[::step],
        cmap=cloud_cmap,
        norm=norm,
        s=1,
        marker="s",
        linewidths=0,
        transform=ccrs.PlateCarree()
    )

    ax.set_title(f"Clavrx Cloud Mask \n {datetime_str}", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='white', linewidth=1)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

    labels = [
        "Clear",
        "Probably clear",
        "Probably cloudy",
        "Cloudy"
    ]

    handles = [
        mpatches.Patch(color=cloud_colors[i], label=labels[i])
        for i in range(4)
    ]

    ax.legend(handles=handles, title="Cloud Mask", loc="lower left")

    plt.savefig(f"plots/{save_path}.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return

def plot_clavrx_dnb_refl(da_dnb_refl, datetime_str, save_path):
    print("Plotting clavr-x DNB reflectance...")
    plt.style.use('dark_background')
    projection = ccrs.PlateCarree(central_longitude=0)
    fig, ax = plt.subplots(1, figsize=(12,12),
                        subplot_kw={'projection': projection})

    step = 6
    sc = ax.scatter(
        da_dnb_refl["longitude"][::step],
        da_dnb_refl["latitude"][::step],
        c=da_dnb_refl[::step],
        cmap="Blues_r",
        s=1,
        marker="s",
        linewidths=0,
        vmin=0, 
        vmax=60, 
        transform=ccrs.PlateCarree()
    )

    ax.set_title(f"Clavrx DNB Reflectance \n {datetime_str}", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='white', linewidth=1)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())


    plt.savefig(f"plots/{save_path}.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return

#---------------

if __name__ == "__main__":
    main()