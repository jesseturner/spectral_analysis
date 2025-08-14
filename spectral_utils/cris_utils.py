import earthaccess, os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt

def download_cris_data(date_start, date_end, lon_west, lat_south, lon_east, lat_north, cris_dir="CrIS_data"):
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
    abs_diff = np.abs(ds['lat'] - target_lat) + np.abs(ds['lon'] - target_lon).values
    atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
    ds_target = ds.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

    print(f"Using lat/lon of {ds_target['lat'].values:.2f}, {ds_target['lon'].values:.2f}, fov of {fov_idx}")
    return ds_target

def planck_radiance(wnum, T):
    
    C1 = 1.191042722E-12		
    C2 = 1.4387752			# units are [K cm]
    C1 = C1 * 1e7			# units are now [mW/m2/ster/cm-4]
    rad = C1 * wnum * wnum * wnum / (np.exp(C2 * wnum / T)-1)
    
    return rad

def plot_radiance_spectra(ds, fig_dir="CrIS_plot", fig_name="CrIS_plot"):
    fig = plt.figure(figsize=(10, 5))

    wnum_lw = ds['wnum_lw'].values
    wnum_mw = ds['wnum_mw'].values
    wnum_sw = ds['wnum_sw'].values
    radiance_lw = ds["rad_lw"]
    radiance_mw = ds["rad_mw"]
    radiance_sw = ds["rad_sw"]

    plt.plot(wnum_lw, planck_radiance(wnum_lw, 290), color="blue", linewidth=1, label="290 K Blackbody")
    plt.plot(wnum_mw, planck_radiance(wnum_mw, 290), color="blue", linewidth=1)
    plt.plot(wnum_sw, planck_radiance(wnum_sw, 290), color="blue", linewidth=1)
    plt.xlim(500, 2500)
    plt.ylim(-5, 160)
    plt.legend()

    plt.plot(wnum_lw, radiance_lw, label="Longwave IR", color="black", linewidth=0.5)
    plt.plot(wnum_mw, radiance_mw, label="Midwave IR", color="black", linewidth=0.5)
    plt.plot(wnum_sw, radiance_sw, label="Shortwave IR", color="black", linewidth=0.5)

    plt.xlabel("Wavenumber (cm⁻¹)")
    plt.ylabel("Radiance (mW/m²/sr/cm⁻¹)")
    plt.title(f"Infrared Spectrum from CrIS")
    plt.grid(color='#d3d3d3')

    os.makedirs(f"{fig_dir}", exist_ok=True)
    fig.savefig(f"{fig_dir}/{fig_name}", dpi=200, bbox_inches='tight')
    plt.close()
    return