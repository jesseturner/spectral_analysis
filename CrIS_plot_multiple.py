import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

cris_dir = "CrIS_data/"
file_name_smoky = "SNDR.J1.CRIS.20240722T1912.m06.g193.L1B.std.v03_08.G.240723022056.nc"
file_name_null = "SNDR.J1.CRIS.20240818T1906.m06.g192.L1B.std.v03_08.G.240819020736.nc"
save_path = "CrIS_figures/"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

#--- Boulder CO
target_lat = 40.02
target_lon = -105.3

ds_smoky = xr.open_dataset(cris_dir+file_name_smoky)
ds_null = xr.open_dataset(cris_dir+file_name_null)

#--- Isolating the Boulder CO point
abs_diff = np.abs(ds_smoky['lat'] - target_lat) + np.abs(ds_smoky['lon'] - target_lon).values
atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
ds_boulder_smoky = ds_smoky.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

abs_diff = np.abs(ds_null['lat'] - target_lat) + np.abs(ds_null['lon'] - target_lon).values
atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
ds_boulder_null = ds_null.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)


#--- Wavenumbers for each CrIS range
#------ Not sure why these are different
wnum_lw = ds_boulder_smoky["wnum_lw"].values  # Longwave IR
wnum_mw = ds_boulder_smoky["wnum_mw"].values  # Midwave IR
wnum_sw = ds_boulder_smoky["wnum_sw"].values  # Shortwave IR

#------ Radiance in mW/(m² sr cm⁻¹)
radiance_lw_smoky = ds_boulder_smoky["rad_lw"]
radiance_mw_smoky = ds_boulder_smoky["rad_mw"]
radiance_sw_smoky = ds_boulder_smoky["rad_sw"]

radiance_lw_null = ds_boulder_null["rad_lw"]
radiance_mw_null = ds_boulder_null["rad_mw"]
radiance_sw_null = ds_boulder_null["rad_sw"]

#------ Convert wavenumber (cm⁻¹) to wavelength (um)
# wl_lw = 10000/wnum_lw
# wl_mw = 10000/wnum_mw
# wl_sw = 10000/wnum_sw

#------ Create a comparison radiance for a reasonable surface temperature (using T = 290 K)
def planck_radiance(wnum, T):
    c = 2.99792458e8       # speed of light in m/s
    h = 6.62607015e-34     # Planck's constant in J*s
    k = 1.380649e-23       # Boltzmann constant in J/K
    wnum_m = wnum * 100    # convert cm⁻¹ to m⁻¹
    wl = 1 / wnum_m        # wavelength in m

    # Planck function
    rad = (2 * h * c**2 / wl**5) / (np.exp(h * c / (wl * k * T)) - 1)

    # Convert to W/(m² sr cm⁻¹) from W/(m² sr m⁻¹)
    rad_per_cm = rad / 100

    # Convert to mW/(m² sr cm⁻¹)
    rad_mW = rad_per_cm / 1000
    return rad_mW


#------ Get brightness temperature
def radiance_to_brightness_temp(radiance, wavenumber):
    # Convert wavenumber (cm^-1) to wavelength (meters)
    wl = (1 / (wavenumber*100))  # cm^-1 to m
    
    # Convert radiance to W/(m²·sr·m)
    B = radiance * 100 * 1000  # mW/(m²·sr·cm^-1) to W/(m²·sr·m)
    
    # Constants
    c = 2.99792458e8       # speed of light in m/s
    h = 6.62607015e-34     # Planck's constant in J·s
    k = 1.380649e-23       # Boltzmann constant in J/K
    
    # Planck constants
    c1 = 2 * h * c**2      # W·m²·sr⁻¹
    c2 = h * c / k         # K·m
    
    # Apply inverse Planck's law to get brightness temperature
    T_B = c2 / (wl * np.log(c1 / (wl**5 * B) + 1))
    
    return T_B

#------ Get brightness temperature from CrIS radiance data
TB_lw_smoky = radiance_to_brightness_temp(radiance_lw_smoky, wnum_lw)
TB_mw_smoky = radiance_to_brightness_temp(radiance_mw_smoky, wnum_mw)
TB_sw_smoky = radiance_to_brightness_temp(radiance_sw_smoky, wnum_sw)

TB_lw_null = radiance_to_brightness_temp(radiance_lw_null, wnum_lw)
TB_mw_null = radiance_to_brightness_temp(radiance_mw_null, wnum_mw)
TB_sw_null = radiance_to_brightness_temp(radiance_sw_null, wnum_sw)


#------ Plot brightness temperature by wavenumber
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, TB_lw_smoky, label="Smoky (2024-07-22)", color="black", linewidth=0.5)
plt.plot(wnum_mw, TB_mw_smoky, color="black", linewidth=0.5)
plt.plot(wnum_sw, TB_sw_smoky, color="black", linewidth=0.5)

plt.plot(wnum_lw, TB_lw_null, label="No smoke (2024-08-18)", color="blue", linewidth=0.5)
plt.plot(wnum_mw, TB_mw_null, color="blue", linewidth=0.5)
plt.plot(wnum_sw, TB_sw_null, color="blue", linewidth=0.5)

plt.xlabel("Wavenumber (cm-1)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')
plt.legend()

fig.savefig(save_path+"spectra_bt_multiple_wn", dpi=200, bbox_inches='tight')
plt.close()

#------ Convert wavenumber (cm⁻¹) to wavelength (um)
wl_lw = 10000/wnum_lw
wl_mw = 10000/wnum_mw
wl_sw = 10000/wnum_sw

#------ Plot brightness temperature by wavelength
fig = plt.figure(figsize=(10, 5))

plt.plot(wl_lw, TB_lw_null, label="No smoke (2024-08-18)", color="#04879C", linewidth=0.5)
plt.plot(wl_mw, TB_mw_null, color="#04879C", linewidth=0.5)
plt.plot(wl_sw, TB_sw_null, color="#04879C", linewidth=0.5)

plt.plot(wl_lw, TB_lw_smoky, label="Smoky (2024-07-22)", color="red", linewidth=0.5)
plt.plot(wl_mw, TB_mw_smoky, color="red", linewidth=0.5)
plt.plot(wl_sw, TB_sw_smoky, color="red", linewidth=0.5)

plt.xlim(4, 15)
plt.ylim(150, 400)

plt.xlabel("Wavenumber (cm-1)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')
plt.legend()

fig.savefig(save_path+"spectra_bt_multiple_wl", dpi=200, bbox_inches='tight')
plt.close()