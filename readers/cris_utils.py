import earthaccess, os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
import cartopy.crs as ccrs
import cartopy.feature as cfeature
import pandas as pd

def download_cris_data(date_start, date_end, lon_west, lat_south, lon_east, lat_north, cris_dir="CrIS_data"):
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
        bounding_box=(lon_west, lat_south, lon_east, lat_north)
    )
    os.makedirs(f"{cris_dir}", exist_ok=True)
    files = earthaccess.download(results, cris_dir)
    return

def open_cris_data(filepath):
    ds = xr.open_dataset(filepath)
    return ds

def isolate_target_point(ds, target_lat, target_lon):
    abs_diff = np.abs(ds['lat'] - target_lat) + np.abs(ds['lon'] - target_lon)
    atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
    ds_target = ds.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

    actual_lat = f"{ds_target['lat'].values:.2f}"
    actual_lon = f"{ds_target['lon'].values:.2f}"
    print(f"Using lat/lon of {actual_lat}, {actual_lon}, fov of {fov_idx}")
    return ds_target, actual_lat, actual_lon

def planck_radiance(wnum, T):
    
    C1 = 1.191042722E-12		
    C2 = 1.4387752			# units are [K cm]
    C1 = C1 * 1e7			# units are now [mW/m2/ster/cm-4]
    rad = C1 * wnum * wnum * wnum / (np.exp(C2 * wnum / T)-1)
    
    return rad

def radiance_to_brightness_temp(radiance, wnum):
    B = radiance / (1000 * 100)  # mW/(m²·sr·cm^-1) to W/(m²·sr·m^-1)
    
    # Constants
    c = 2.99792458e8       # speed of light in m/s
    h = 6.62607015e-34     # Planck's constant in J·s
    k = 1.380649e-23       # Boltzmann constant in J/K
    
    nu_bar = wnum * 100  # now in m⁻¹

    numerator = h * c * nu_bar
    denominator = k * np.log((2 * h * c**2 * nu_bar**3) / B + 1)
    
    T_B = numerator / denominator    
    return T_B

def get_brightness_temperature(ds, spectra_sel):
    """
    :param ds: From open_cris_data() or isolate_target_point()
    :param spectra_sel: "lw", "mw", or "sw"
    """
    wnum = ds[f'wnum_{spectra_sel}'].values
    
    TB = radiance_to_brightness_temp(ds[f'rad_{spectra_sel}'], wnum)

    df = pd.DataFrame({
        "Wavenumber (cm-1)": wnum, 
        "Wavelength (um)": 10_000 / wnum, 
        "Brightness Temperature (K)": TB
    })

    return df

