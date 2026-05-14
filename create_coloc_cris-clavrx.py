from readers import clavrx_utils as clavrx
from readers import cris_utils as cris

from datetime import datetime, timedelta
import os
import glob
import re
import xarray as xr

#--- Access the CLAVR-x data

today_date_str = datetime.now().strftime("%Y_%m_%d")
clavrx_dir = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"
clavrx_date_str = "20250312"  # YYYYMMDD
start_time = "0634" # HHmm
end_time = "0638" # HHmm
sat_str = "j01"
clavrx_date = datetime.strptime(clavrx_date_str, "%Y%m%d")
clavrx_julian_str = clavrx_date.strftime("%Y%j")

clavrx_pattern = os.path.join(clavrx_dir, f"{clavrx_julian_str}/*.hdf")
filepath_list = glob.glob(clavrx_pattern)
filepath_list_sat = [s for s in filepath_list if re.search(rf"{sat_str}", s)]
filepath_list_sat.sort()

pattern = re.compile(r"_t(\d{4})\d*")
filepath_list_sat_time = [
    f for f in filepath_list_sat
    if (m := pattern.search(f)) and start_time <= m.group(1) <= end_time
]

#--- Much faster after the first one is loaded!

latitudes = clavrx.opening_clavrx(filepath_list_sat_time, dataset='latitude')
longitudes = clavrx.opening_clavrx(filepath_list_sat_time, dataset='longitude')
cloud_mask = clavrx.opening_clavrx(filepath_list_sat_time, dataset='cloud_mask')

#--- Create the dataset with CLAVR-x

ds = xr.Dataset(
    data_vars={
        "clavrx_cloud_mask": (("y", "x"), cloud_mask)
    },
    coords={
        "latitude": (("y", "x"), latitudes),
        "longitude": (("y", "x"), longitudes),
    },
)

#--- Access the CrIS data

cris_dir = "data/cris/from_earthaccess"
cris_date = "20250312" #YYYYMMDD
cris_pattern = os.path.join(cris_dir, f"SNDR.J1.CRIS.{cris_date}*")

cris_files = glob.glob(cris_pattern)
cris_files.sort() 
print(f"{len(cris_files)} CrIS files found...")
if not cris_files:
    print("CrIS files not found, downloading...")
    date_obj = datetime.strptime(cris_date, "%Y%m%d")
    sel_day_formatted = date_obj.strftime("%Y-%m-%d")
    next_day_formatted = (date_obj + timedelta(days=1)).strftime("%Y-%m-%d")
    cris_files = cris.download_cris_data(sel_day_formatted, next_day_formatted, cris_dir=cris_dir)

"Opening CrIS data..."
cris_ds = xr.open_mfdataset(
        cris_files,
        combine="nested",
        concat_dim="atrack")

import numpy as np
from scipy.spatial import cKDTree

print("Creating target grid (CLAVR-x)...")
lat1 = ds["latitude"].values   # (y, x)
lon1 = ds["longitude"].values 
ny, nx = ds["latitude"].shape
# Flatten target coordinates
target_points = np.column_stack([
    lat1.ravel(),
    lon1.ravel()
])

print("Creating kd-tree of source points (CrIS)...")
lat2 = cris_ds["lat"].values   # (atrack, xtrack, fov)
lon2 = cris_ds["lon"].values

rad2 = cris_ds["rad_lw"].values # shape: (90, 30, 9, 717)
source_points = np.column_stack([
    lat2.ravel(),
    lon2.ravel()
])
nchan = rad2.shape[-1]
rad2_flat = rad2.reshape(-1, nchan)
tree = cKDTree(source_points)

distances, indices = tree.query(target_points)
matched_rad = rad2_flat[indices]
matched_rad = matched_rad.reshape(ny, nx, nchan)

print("Creating dataset of CrIS on CLAVR-x grid...")
ds["rad_lw_cris"] = xr.DataArray(
    matched_rad,
    dims=("y", "x", "wnum_lw"),
    coords={
        "y": ds["y"],
        "x": ds["x"],
        "wnum_lw": cris_ds["wnum_lw"],
    },
)

today_date_str = datetime.now().strftime("%Y_%m_%d")
ds.to_netcdf(f"data/processed_datasets/coloc_cris-clavrx_{today_date_str}.nc")
