import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

save_path = "CrIS_ASSIST_figures/"
os.makedirs(os.path.dirname(save_path), exist_ok=True)

#--- Get CrIS data
cris_dir = "CrIS_data/"
cris_file_name = "SNDR.J1.CRIS.20240722T1912.m06.g193.L1B.std.v03_08.G.240723022056.nc"
cris_ds = xr.open_dataset(cris_dir+cris_file_name)

#--- Boulder CO
target_lat = 40.02
target_lon = -105.3

#--- Isolating the Boulder CO point
abs_diff = np.abs(cris_ds['lat'] - target_lat) + np.abs(cris_ds['lon'] - target_lon).values
atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
cris_ds_boulder = cris_ds.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

#------ Radiance in mW/(m² sr cm⁻¹)
cris_radiance_lw = cris_ds_boulder["rad_lw"]
cris_radiance_mw = cris_ds_boulder["rad_mw"]
cris_radiance_sw = cris_ds_boulder["rad_sw"]

#--- Wavenumbers for each CrIS range
cris_wnum_lw = cris_ds_boulder["wnum_lw"].values  # Longwave IR
cris_wnum_mw = cris_ds_boulder["wnum_mw"].values  # Midwave IR
cris_wnum_sw = cris_ds_boulder["wnum_sw"].values  # Shortwave IR

def planck_radiance(wnum, T):
    
    C1 = 1.191042722E-12		
    C2 = 1.4387752			# units are [K cm]
    C1 = C1 * 1e7			# units are now [mW/m2/ster/cm-4]
    rad = C1 * wnum * wnum * wnum / (np.exp(C2 * wnum / T)-1)
    
    return rad

#--- Get ASSIST data
assist_dir = "ASSIST_data/"
assist_file_name = "20240722_191700.nc"
assist_ds = xr.open_dataset(assist_dir+assist_file_name)

#--- Pull out the radiance and wavenumber values
assist_radiance_sw = assist_ds.radiance_ch1
assist_radiance_lw = assist_ds.radiance_ch2
assist_wnum_sw = assist_ds.wnum_ch1
assist_wnum_lw = assist_ds.wnum_ch2

#------ Plot the spectras together (radiance)
fig = plt.figure(figsize=(10, 5))

plt.xlim(500, 2500)
plt.ylim(-5, 160)

plt.plot(assist_wnum_lw, planck_radiance(assist_wnum_lw, 300), color="blue", linewidth=1)
plt.plot(assist_wnum_sw, planck_radiance(assist_wnum_sw, 300), color="blue", linewidth=1)

label_x = 1500
label_y = np.interp(label_x, assist_wnum_lw, planck_radiance(assist_wnum_lw, 300))
plt.text(label_x, label_y, "300 K Blackbody", color="blue", fontsize=10, va='bottom', rotation=-25)

plt.plot(assist_wnum_lw, assist_radiance_lw, label="ASSIST", color="black", linewidth=0.5)
plt.plot(assist_wnum_sw, assist_radiance_sw, color="black", linewidth=0.5)

plt.plot(cris_wnum_lw, cris_radiance_lw, label="CrIS", color="red", linewidth=0.5)
plt.plot(cris_wnum_mw, cris_radiance_mw, color="red", linewidth=0.5)
plt.plot(cris_wnum_sw, cris_radiance_sw, color="red", linewidth=0.5)

plt.legend()

plt.xlabel("Wavenumber (cm⁻¹)")
plt.ylabel("Radiance (mW/m²/sr/cm⁻¹)")
plt.title("Infrared Spectrum (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"/spectra_rad", dpi=200, bbox_inches='tight')
plt.close()


#------ Plot the spectras together (brightness temperature)

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
    print(T_B)
    
    return T_B

#------ Get brightness temperature from CrIS radiance data
cris_TB_lw = radiance_to_brightness_temp(cris_radiance_lw, cris_wnum_lw)
cris_TB_mw = radiance_to_brightness_temp(cris_radiance_mw, cris_wnum_mw)
cris_TB_sw = radiance_to_brightness_temp(cris_radiance_sw, cris_wnum_sw)
assist_TB_lw = radiance_to_brightness_temp(assist_radiance_lw, assist_wnum_lw)
assist_TB_sw = radiance_to_brightness_temp(assist_radiance_sw, assist_wnum_sw)

#------ Convert wavenumber (cm⁻¹) to wavelength (um)
cris_wl_lw = 10000/cris_wnum_lw
cris_wl_mw = 10000/cris_wnum_mw
cris_wl_sw = 10000/cris_wnum_sw
assist_wl_lw = 10000/assist_wnum_lw
assist_wl_sw = 10000/assist_wnum_sw

fig = plt.figure(figsize=(10, 5))

plt.xlim(4, 15)
plt.ylim(150, 400)

plt.plot(assist_wl_lw, assist_TB_lw, label="ASSIST", color="black", linewidth=0.5)
plt.plot(assist_wl_sw, assist_TB_sw, color="black", linewidth=0.5)

plt.plot(cris_wl_lw, cris_TB_lw, label="CrIS", color="red", linewidth=0.5)
plt.plot(cris_wl_mw, cris_TB_mw, color="red", linewidth=0.5)
plt.plot(cris_wl_sw, cris_TB_sw, color="red", linewidth=0.5)

# plt.plot(assist_wnum_lw, assist_TB_lw, label="ASSIST", color="black", linewidth=0.5)
# plt.plot(assist_wnum_sw, assist_TB_sw, color="black", linewidth=0.5)

# plt.plot(cris_wnum_lw, cris_TB_lw, label="CrIS", color="red", linewidth=0.5)
# plt.plot(cris_wnum_mw, cris_TB_mw, color="red", linewidth=0.5)
# plt.plot(cris_wnum_sw, cris_TB_sw, color="red", linewidth=0.5)

plt.legend()

plt.xlabel("Wavelength (μm)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Infrared Spectrum (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"/spectra_bt", dpi=200, bbox_inches='tight')
plt.close()