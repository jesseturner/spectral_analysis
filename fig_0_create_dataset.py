# Get list of moonlit dates
# Create dataset of samples from clavrx, DNB, and CrIS

from datetime import datetime, timedelta, timezone
from skyfield.api import load
from skyfield.framelib import ecliptic_frame
import numpy as np
import os, glob
import xarray as xr

time_span_previous_days = 30
moon_illumination_threshold = 90
print(f"Getting dates from last {time_span_previous_days} days with >{moon_illumination_threshold}% moon illumination...")

ts = load.timescale()
eph = load('de421.bsp')

sun = eph['sun']
moon = eph['moon']
earth = eph['earth']

def moon_illumination(date):
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

today = datetime.now(timezone.utc).date()
start_date = today - timedelta(days=time_span_previous_days)

high_illum_dates = []

current = start_date
while current <= today:
    illum = moon_illumination(current)
    if illum > 90:
        high_illum_dates.append((current))
    current += timedelta(days=1)


print(f"Found {len(high_illum_dates)} days...")

print("Getting clavrx files for each date...")
clavrx_path = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"

all_files = []

for date_obj in high_illum_dates:
    year = date_obj.year
    julian_day = date_obj.timetuple().tm_yday
    dir_name = f"{year}{julian_day:03d}"
    full_dir = os.path.join(clavrx_path, dir_name)

    if os.path.exists(full_dir):
        pattern = os.path.join(full_dir, "*.level2.hdf")
        all_files.extend(glob.glob(pattern))

total_files = len(all_files)
print(f"Total files to process: {total_files}")

datasets = []
failed_files = []
success_count = 0
failure_count = 0
processed = 0

for file in all_files:
    processed += 1

    print(f"Processing file {processed}/{total_files} "
          f"({processed/total_files*100:.1f}%)",
          end="\r")  # overwrites same line

    try:
        ds = xr.open_dataset(file, engine="netcdf4")
        datasets.append(ds)
        success_count += 1

    except Exception as e:
        failure_count += 1
        failed_files.append(file)

print("\nDone.")
print(f"Successfully opened {success_count}/{total_files} files.")

