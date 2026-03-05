from datetime import datetime, timedelta, timezone
from skyfield.api import load
import numpy as np
import os, glob
import xarray as xr
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs
import re

def main():
    time_span_previous_days = 30
    moon_illumination_threshold = 90
    print(f"Getting dates from last {time_span_previous_days} days with >{moon_illumination_threshold}% moon illumination...")

    high_illum_dates = get_high_illum_dates(time_span_previous_days)
    print(f"Found {len(high_illum_dates)} days...")

    print("Getting clavrx files for each date...")
    clavrx_path = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"
    all_files = get_clavrx_files(clavrx_path, high_illum_dates)
    print(f"Total files with high moonlight: {len(all_files)}")

    print("Filtering to NOAA-20 (clavrx files on NOAA-21 are corrupted, CrIS is discontinued on S-NPP)...")
    all_files = filter_to_sat(all_files, "j01")

    print("Getting most recent NOAA-20 orbit...")
    orbit = get_orbit(all_files[-600])

    orbit_files = [f for f in all_files if re.search(orbit, f)]
    print(f"{len(orbit_files)} files in orbit {orbit}...")
    print(f"Files starting from {extract_datetime_from_filename(orbit_files[0])}...")

    sample_start, sample_end = 24, 27
    print(f"Setting sample to file {sample_start} to {sample_end}...")
    orbit_files_select = only_valid_nighttime_files(orbit_files[sample_start:sample_end])
    print(f"Sampling {len(orbit_files_select)}/{len(orbit_files)} valid nighttime files in orbit {orbit}...")

    da_cris, datetime_str_cris = create_cris_da(orbit_files_select)
    ds_combined, datetime_str = get_combined_multiple_files(orbit_files_select)
    da_refl_lunar = get_variable(ds_combined, 'refl_lunar_dnb_nom')
    da_cloud_mask = get_variable(ds_combined, 'cloud_mask')
    
    plot_clavrx_cloud_mask(da_cloud_mask, datetime_str, save_path="clavrx_cloud_mask")
    plot_clavrx_dnb_refl(da_refl_lunar, datetime_str, save_path="clavrx_refl_lunar")
    plot_cris_spatial(da_cris, datetime_str_cris, save_path="cris_rad")

    return

#---------------

def get_high_illum_dates(time_span_previous_days):
    today = datetime.now(timezone.utc).date()
    start_date = today - timedelta(days=time_span_previous_days)

    high_illum_dates = []

    current = start_date
    while current <= today:
        illum = moon_illumination(current)
        if illum > 90:
            high_illum_dates.append((current))
        current += timedelta(days=1)
    return high_illum_dates

def moon_illumination(date):
        ts = load.timescale()
        eph = load('de421.bsp')
        sun = eph['sun']
        moon = eph['moon']
        earth = eph['earth']
        
        t = ts.utc(date.year, date.month, date.day)

        # Get positions
        e = earth.at(t)
        s = e.observe(sun).apparent()
        m = e.observe(moon).apparent()

        # Phase angle between Sun and Moon
        phase_angle = s.separation_from(m).degrees

        # Illumination fraction formula
        illumination = (1 - np.cos(np.radians(phase_angle))) / 2
        return illumination * 100

def get_clavrx_files(clavrx_path, date_list):

    all_files = []

    for date_obj in date_list:
        year = date_obj.year
        julian_day = date_obj.timetuple().tm_yday
        dir_name = f"{year}{julian_day:03d}"
        full_dir = os.path.join(clavrx_path, dir_name)

        if os.path.exists(full_dir):
            pattern = os.path.join(full_dir, "*.level2.hdf")
            all_files.extend(glob.glob(pattern))

    all_files.sort()
    return all_files

def filter_to_sat(clavrx_files, sat_str):
    clavrx_files_filtered = [f for f in clavrx_files if sat_str.lower() in f.lower()]
    return clavrx_files_filtered

def get_orbit(clavrx_path):
    match = re.search(r'_b(\d+)', clavrx_path)

    if match:
        orbit_tag = match.group(0)[1:]

    return orbit_tag

def only_valid_nighttime_files(file_list):
    good_files = []
    for f in file_list:
        try:
            with xr.open_dataset(f, engine="netcdf4") as ds:
                ds.load()
                if ds['solar_zenith_angle'].max() > 90: # NIGHTTIME
                    good_files.append(f)
        except Exception as e:
            print(f"Skipping corrupted file: {f} ({e})")
    return good_files

def get_combined_multiple_files(orbit_files):
    ds_combined = xr.open_mfdataset(
        orbit_files,
        combine="nested",
        preprocess=fix_dims,
        concat_dim="scan_lines_along_track_direction",
        engine='netcdf4')
    
    start_dt = extract_datetime_from_filename(orbit_files[0])
    end_dt   = extract_datetime_from_filename(orbit_files[-1])
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


def extract_datetime_from_filename_cris(filename):
    match = re.search(r'CRIS.(\d{8})T(\d{4})', filename)

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

def plot_cris_spatial(da_cris, datetime_str, save_path):
    print("Plotting CrIS radiance (manually selected)...")
    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

    c = ax.pcolormesh(da_cris['lon'], da_cris['lat'], da_cris, cmap='Greys', shading='auto')

    ax.coastlines(resolution='50m', color='white', linewidth=1)
    ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())


    ax.set_title(f"CrIS Radiance (648.75 cm-1) \n {datetime_str}", fontsize=20, pad=10)

    plt.savefig(f"plots/{save_path}.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return

def create_cris_da(orbit_files_select):
    print("Getting matching CrIS files...")

    cris_files = find_matching_cris_files(orbit_files_select)
    if cris_files:
        print(f"{len(cris_files)} matching CrIS files found...")
    else:
        print("No CrIS files found, likely need downloading...")

    ds = xr.open_mfdataset(
        cris_files,
        combine="nested",
        concat_dim="atrack")

    ds_sel = ds.sel(atrack=slice(0, 18), xtrack=slice(0, 18), fov=0, wnum_lw=648.75)
    da_cris = ds_sel['rad_lw']

    start_dt = extract_datetime_from_filename_cris(cris_files[0])
    end_dt   = extract_datetime_from_filename_cris(cris_files[-1])
    if start_dt and end_dt:
        datetime_str = f"{start_dt} - {end_dt}"
    else:
        datetime_str = "Unknown - File format unexpected."

    return da_cris, datetime_str

def extract_date_time_from_clavrx(path):
    """
    Extract YYYYMMDD and first 3 digits of time from CLAVR-x filename.
    """
    filename = os.path.basename(path)
    
    match = re.search(r'd(\d{8})_t(\d{7})', filename)
    if not match:
        return None, None
    
    date = match.group(1)
    time_prefix = match.group(2)[:3]
    
    return date, time_prefix

def find_matching_cris_files(clavrx_paths, cris_base_dir="data/cris/from_earthaccess"):
    matching_files = []

    # Get all CRIS files once
    cris_files = glob.glob(os.path.join(cris_base_dir, "*.nc"))

    for clavrx_path in clavrx_paths:
        date, time_prefix = extract_date_time_from_clavrx(clavrx_path)
        if not date:
            continue

        for cris_file in cris_files:
            cris_name = os.path.basename(cris_file)

            # Match YYYYMMDD
            if date not in cris_name:
                continue

            # Match first 3 digits of time (after T)
            time_match = re.search(r'T(\d{4})', cris_name)
            if not time_match:
                continue

            cris_time_prefix = time_match.group(1)[:3]

            if cris_time_prefix == time_prefix:
                matching_files.append(cris_file)

    return matching_files

#---------------

if __name__ == "__main__":
    main()