#--- Libraries used
#------ Use spectral_analysis.yml in repo to create a compatible conda environment, if desired
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
import sys

#--- Path to CrIS data and figure save directory
#------ CrIS data can be downloaded using CrIS_data.py in repo
cris_dir = "CrIS_data/"
file_name = "SNDR.J1.CRIS.20240722T1912.m06.g193.L1B.std.v03_08.G.240723022056.nc"
save_path = "CrIS_figures_fresh/"

#--- Target location within the CrIS swath
#------ Boulder CO
target_lat = 40.02
target_lon = -105.3

#===========================No inputs below here===========================

#--- Checking if data is available
cris_path = cris_dir + file_name
if not os.path.isfile(cris_path):
    print(f"Error: File not found.")
    sys.exit(1)

#--- Opening CrIS file
ds = xr.open_dataset(cris_dir+file_name)
os.makedirs(os.path.dirname(save_path), exist_ok=True)

#--- Isolating the targeted point
abs_diff = np.abs(ds['lat'] - target_lat) + np.abs(ds['lon'] - target_lon).values
atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
ds_target = ds.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

print(f"Using lat/lon of {ds_target["lat"].values:.2f}, {ds_target["lon"].values:.2f}, fov of {fov_idx}")

#--- Wavenumbers for each CrIS range
wnum_lw = ds_target["wnum_lw"].values  # Longwave IR
wnum_mw = ds_target["wnum_mw"].values  # Midwave IR
wnum_sw = ds_target["wnum_sw"].values  # Shortwave IR

#------ Radiance in mW/(m² sr cm⁻¹)
radiance_lw = ds_target["rad_lw"]
radiance_mw = ds_target["rad_mw"]
radiance_sw = ds_target["rad_sw"]

#------ Convert wavenumber (cm⁻¹) to wavelength (um)
wl_lw = 10000/wnum_lw
wl_mw = 10000/wnum_mw
wl_sw = 10000/wnum_sw

#------ Create a comparison radiance for a reasonable surface temperature (using T = 290 K)
def planck_radiance(wnum, T):
    
    C1 = 1.191042722E-12		
    C2 = 1.4387752			# units are [K cm]
    C1 = C1 * 1e7			# units are now [mW/m2/ster/cm-4]
    rad = C1 * wnum * wnum * wnum / (np.exp(C2 * wnum / T)-1)
    
    return rad

#------ Plot the randiance spectra
fig = plt.figure(figsize=(10, 5))

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
plt.title("Infrared Spectrum from CrIS (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"/spectra_rad_example", dpi=200, bbox_inches='tight')
plt.close()

#------ Get brightness temperature
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

#------ Get brightness temperature from CrIS radiance data
TB_lw = radiance_to_brightness_temp(radiance_lw, wnum_lw)
TB_mw = radiance_to_brightness_temp(radiance_mw, wnum_mw)
TB_sw = radiance_to_brightness_temp(radiance_sw, wnum_sw)

#------ Plot brightness temperature by wavenumber
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, TB_lw, label="Longwave IR", color="black", linewidth=0.5)
plt.plot(wnum_mw, TB_mw, label="Midwave IR", color="black", linewidth=0.5)
plt.plot(wnum_sw, TB_sw, label="Shortwave IR", color="black", linewidth=0.5)

plt.xlabel("Wavenumber (cm-1)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"spectra_bt_example_wn", dpi=200, bbox_inches='tight')
plt.close()


#------ Plot brightness temperature by wavelength
fig = plt.figure(figsize=(10, 5))
plt.plot(wl_lw, TB_lw, label="Longwave IR", color="black", linewidth=0.5)
plt.plot(wl_mw, TB_mw, label="Midwave IR", color="black", linewidth=0.5)
plt.plot(wl_sw, TB_sw, label="Shortwave IR", color="black", linewidth=0.5)
plt.xlim(4, 15)
plt.ylim(150, 400)

plt.xlabel("Wavelength (μm)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"spectra_bt_example_wl", dpi=200, bbox_inches='tight')
plt.close()