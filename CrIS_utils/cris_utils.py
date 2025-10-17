import earthaccess, os
import xarray as xr
import numpy as np
import matplotlib.pyplot as plt
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

def get_brightness_temperature(ds):
    wnum_lw = ds['wnum_lw'].values
    wnum_mw = ds['wnum_mw'].values
    wnum_sw = ds['wnum_sw'].values

    wnum = np.concatenate((wnum_lw, wnum_mw, wnum_sw))
    wl = 10000 / wnum
    
    TB_lw = radiance_to_brightness_temp(ds['rad_lw'], wnum_lw)
    TB_mw = radiance_to_brightness_temp(ds['rad_mw'], wnum_mw)
    TB_sw = radiance_to_brightness_temp(ds['rad_sw'], wnum_sw)
    TB = np.concatenate((TB_lw, TB_mw, TB_sw))

    data = {
        "Wavenumber (cm-1)": wnum, 
        "Wavelength (um)": wl, 
        "Brightness Temperature (K)": TB
    }

    df = pd.DataFrame(data)

    return df

def plot_brightness_temperature(df, fig_dir="CrIS_plot", fig_name="CrIS_Tb", fig_title="Brightness Temperature Spectrum from CrIS"):


    fig = plt.figure(figsize=(10, 5))
    plt.plot(df["Wavelength (um)"], df["Brightness Temperature (K)"], color="black", linewidth=0.5)
    plt.xlim(4, 15)
    plt.ylim(150, 400)

    plt.xlabel("Wavelength (μm)")
    plt.ylabel("Brightness Temperature (K)")
    plt.title(fig_title)
    plt.grid(color='#d3d3d3')

    _plt_save(fig_dir, fig_name)
    return

def plot_btd_freq_range(df,
    fig_dir='CrIS_plot', fig_name='CrIS_btd_range', fig_title='CrIS Brightness Temperature',
    freq_range1=None, freq_range2=None, ylim=None):
    """
    Visualizing the brightness temperature difference between two different spectra ranges.
    freq_range format: [2430, 2555]
    ylim: tuple like (271, 280)
    """

    fig, ax = plt.subplots(figsize=(10, 5))

    df_range1 = _filter_freq_to_range(df, freq_range1[0], freq_range1[1])
    _plot_continuous(ax, df_range1, color="blue")
    ax.xaxis.label.set_color("blue")
    ax.tick_params(axis="x", colors="blue")

    ax2 = ax.twiny()
    df_range2 = _filter_freq_to_range(df, freq_range2[0], freq_range2[1])
    _plot_continuous(ax2, df_range2, color="red")
    ax2.xaxis.label.set_color("red")
    ax2.tick_params(axis="x", colors="red")
    
    ax.set_title(fig_title)
    ax.set_xlabel("Wavelength (μm)")
    ax.set_ylabel("Temperature (K)")
    if ylim:
        ax.set_ylim(ylim)

    _plt_save(fig_dir, fig_name)
    return

def _filter_freq_to_range(df, freq_start, freq_end):
    filtered_df = df[((df["Wavenumber (cm-1)"] >= freq_start) & (df["Wavenumber (cm-1)"] <= freq_end))]
    return filtered_df

def _plot_continuous(ax, df, color='black'):
    x = df["Wavelength (um)"]
    y = df["Brightness Temperature (K)"]
    ax.plot(x, y, color=color, linewidth=1)
        
    return

def _plt_save(fig_dir, fig_name):
    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

def get_Tb_from_srf(spectra_df, srf_file):
    """
    Use CrIS spectra and SRF to get brightness temperature.
    
    ----------
    spectra_df : from get_brightness_temperature(ds)
    srf_file : downloaded .dat file
    """

    #--- flip direction to match to SRF
    spectra_wl = spectra_df['Wavelength (um)'][::-1]
    spectra_t = spectra_df['Brightness Temperature (K)'][::-1]

    #--- Load SRF, which is in wavelengths and proportions
    srf = np.loadtxt(srf_file)
    srf_wl = np.array(srf[:, 0]/1000) # Convert from nm to µm
    srf_response = np.array(srf[:, 1])

    #--- Interpolate BT onto the SRF wavelength grid
    from scipy.interpolate import interp1d
    interp_rad = interp1d(spectra_wl, spectra_t, kind='linear', bounds_error=False, fill_value=np.nan)
    Tb_array = interp_rad(srf_wl)

    #--- Remove missing data from SRF arrays
    mask = ~np.isnan(Tb_array)
    Tb_array = Tb_array[mask]
    srf_response = srf_response[mask]
    srf_wl = srf_wl[mask]

    #------ Trapezoid method to get Tb multiplied by normalized SRF
    Tb = np.trapz(Tb_array * srf_response, srf_wl) / np.trapz(srf_response, srf_wl) 
    print(f"Brightness temperature: {Tb:.2f} K")

    return