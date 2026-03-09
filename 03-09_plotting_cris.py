import earthaccess
import os
import xarray as xr
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import re
import glob
from datetime import datetime, timedelta
import numpy as np


def main():

    cris_dir = "data/cris/from_earthaccess"
    cris_date = "20260306" #YYYYMMDD
    cris_pattern = os.path.join(cris_dir, f"SNDR.J1.CRIS.{cris_date}*")

    cris_files = glob.glob(cris_pattern)
    cris_files.sort() 
    print(f"{len(cris_files)} CrIS files found...")
    if not cris_files:
        print("CrIS files not found, downloading...")
        date_obj = datetime.strptime(cris_date, "%Y%m%d")
        sel_day_formatted = date_obj.strftime("%Y-%m-%d")
        next_day_formatted = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
        cris_files = download_cris_data(sel_day_formatted, next_day_formatted, cris_dir=cris_dir)

    cris_files_sample = cris_files[:]
    print(f"Using {len(cris_files_sample)}/{len(cris_files)} of the files...")

    da_cris, datetime_str = create_cris_da(cris_files_sample, wnum_sel=750)
    
    plot_cris_spatial(da_cris, datetime_str, save_path="cris_rad")


    return

#---------------

def download_cris_data(date_start, date_end, lon_west=None, lat_south=None, lon_east=None, lat_north=None, cris_dir="CrIS_data"):
    """
    date_start and date_end format: "2025-06-25"
    coordinate format: -105.31
    """
    #--- Earthaccess docs: https://earthaccess.readthedocs.io/en/latest/quick-start/
    auth = earthaccess.login()

    print("Currently only searches NOAA-20")

    #--- Search for the granule by DOI
    #------ Suomi NPP Normal Spectral Resolution 10.5067/OZZPDWENP2NC
    #------ Suomi NPP Full Spectral Resolution 10.5067/ZCRSHBM5HB23
    #------ NOAA-20 / JPSS-1 Full Spectral Resolution 10.5067/LVEKYTNSRNKP
    #------ NOAA-21 / JPSS-2 Full Spectral Resolution 
    results = earthaccess.search_data(
        doi='10.5067/LVEKYTNSRNKP',
        temporal=(date_start, date_end), 
        # bounding_box=(lon_west, lat_south, lon_east, lat_north)
    )
    os.makedirs(f"{cris_dir}", exist_ok=True)
    files = earthaccess.download(results, cris_dir)
    print(f"{len(files)} downloaded.")
    return files

def create_cris_da(cris_files, wnum_sel):
    print("Creating CrIS dataset...")

    ds = xr.open_mfdataset(
        cris_files,
        combine="nested",
        concat_dim="atrack")

    ds_sel = ds.sel(fov=0, wnum_lw=wnum_sel)
    da_cris = ds_sel['rad_lw']

    start_dt = extract_datetime_from_filename_cris(cris_files[0])
    end_dt   = extract_datetime_from_filename_cris(cris_files[-1])
    if start_dt and end_dt:
        datetime_str = f"{start_dt} - {end_dt}"
    else:
        datetime_str = "Unknown - File format unexpected."

    return da_cris, datetime_str

def extract_datetime_from_filename_cris(filename):
    match = re.search(r'CRIS.(\d{8})T(\d{4})', filename)

    if not match:
        return None

    date_part = match.group(1)
    time_part = match.group(2)

    date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}"
    time_formatted = f"{time_part[:2]}:{time_part[2:4]}"

    return f"{date_formatted} {time_formatted}"

def plot_cris_spatial(da_cris, datetime_str, save_path):
    wnum_sel = da_cris['wnum_lw'].values
    print(f"Plotting CrIS radiance ({wnum_sel} cm-1)...")
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

    c = ax.pcolormesh(da_cris['lon'], da_cris['lat'], da_cris, cmap='Greys', shading='auto')
    # sc = ax.scatter(
    #     da_cris['lon'],
    #     da_cris['lat'],
    #     c=da_cris,
    #     cmap="Blues_r",
    #     s=1,
    #     marker="s",
    #     linewidths=0,
    #     vmin=50,
    #     vmax=66,
    #     transform=ccrs.PlateCarree()
    # )

    ax.coastlines(resolution='50m', color='black', linewidth=1)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

    cbar = plt.colorbar(c, ax=ax, orientation='vertical', pad=0.02, shrink=0.3)
    cbar.set_label("mW/(m2 sr cm-1)")
    ax.set_title(f"CrIS Radiance ({wnum_sel} cm-1) \n {datetime_str}", fontsize=20, pad=10)

    plt.savefig(f"plots/{save_path}.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return

#---------------

if __name__ == "__main__":
    main()