import os
import xarray as xr
import h5py

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

def open_viirs_file():
    ds = xr.open_dataset(file_path, engine="netcdf4")
    print(ds)
    return