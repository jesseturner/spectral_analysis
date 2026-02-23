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
    all_files = get_clavrx_files(high_illum_dates)


    sample_id = 1530
    da_cloud_mask, datetime_str = get_cloud_mask_sample(sample_id, all_files)
    plot_clavrx_cloud_mask(da_cloud_mask, datetime_str, save_path="clavrx_cloud_mask_file")

    orbit = "b42765"
    orbit_files = [f for f in all_files if re.search(orbit, f)]
    print(f"Plotting {len(orbit_files)} files for orbit {orbit}...")

    print(f"Opening multiple files not working yet...")
    # ds_orbit = [xr.open_dataset(f, engine='netcdf4') for f in orbit_files[0:6]]
    # ds_orbit = [
    #     ds.set_coords(["latitude", "longitude"])
    #     for ds in ds_orbit
    # ]
    # ds_orbit_all = xr.concat(
    #     ds_orbit,
    #     dim="scan_lines_along_track_direction"
    # )
    # print(ds_orbit_all)
    # da_cloud_mask_orbit = ds_orbit_all['cloud_mask']
    # valid = np.isfinite(da_cloud_mask_orbit) & np.isfinite(da_cloud_mask_orbit["latitude"]) & np.isfinite(da_cloud_mask_orbit["longitude"])
    # da_cloud_mask_orbit = da_cloud_mask_orbit.where(valid, drop=True)
    # plot_clavrx_cloud_mask(da_cloud_mask_orbit, datetime_str, save_path="clavrx_cloud_mask_orbit")
    
    # ds = xr.open_mfdataset(
    #     orbit_files,
    #     concat_dim="scan_lines_along_track_direction",
    #     engine="netcdf4",
    #     combine="nested",
    #     parallel=True, 
    #     data_vars='minimal', 
    #     coords='minimal', 
    #     compat='override')

    
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
        illumination = (1 + np.cos(np.radians(phase_angle))) / 2
        return illumination * 100

def plot_clavrx_cloud_mask(da_cloud_mask, datetime_str, save_path):
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

    pcm = ax.pcolormesh(
        da_cloud_mask["longitude"],
        da_cloud_mask["latitude"],
        da_cloud_mask,
        cmap=cloud_cmap,
        norm=norm,
        transform=ccrs.PlateCarree()
    )

    ax.set_title(f"Clavrx Cloud Mask \n {datetime_str}", fontsize=20, pad=10)
    ax.coastlines(resolution='50m', color='black', linewidth=1)

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

def get_clavrx_files(date_list):
    clavrx_path = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"

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
    print(f"Total files with high moonlight: {len(all_files)}")
    return all_files

def get_cloud_mask_sample(sample_id, all_files):
    print(f"Setting sample to file {sample_id}...")
    ds_example = xr.open_dataset(
        all_files[sample_id],
        engine='netcdf4')

    match = re.search(r'd(\d{8})_t(\d{6})', all_files[sample_id])
    if match:
        date_part = match.group(1)
        time_part = match.group(2)
        date_formatted = f"{date_part[:4]}-{date_part[4:6]}-{date_part[6:]}"
        time_formatted = f"{time_part[:2]}:{time_part[2:4]}"
        datetime_str = f"{date_formatted} {time_formatted}"
    else:
        datetime_str = "Unknown - File format unexpected."

    da_cloud_mask = ds_example['cloud_mask']
    valid = np.isfinite(da_cloud_mask) & np.isfinite(da_cloud_mask["latitude"]) & np.isfinite(da_cloud_mask["longitude"])
    da_cloud_mask = da_cloud_mask.where(valid, drop=True)

    return da_cloud_mask, datetime_str

#---------------

if __name__ == "__main__":
    main()