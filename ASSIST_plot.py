import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

assist_dir = "ASSIST_data/"
file_name = "20240722_191700.nc"
save_path = "ASSIST_figures/"

ds = xr.open_dataset(assist_dir+file_name)
os.makedirs(os.path.dirname(save_path), exist_ok=True)

#--- Pull out the radiance and wavenumber values
radiance_sw = ds.radiance_ch1
radiance_lw = ds.radiance_ch2
wnum_sw = ds.wnum_ch1
wnum_lw = ds.wnum_ch2

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
    print(T_B)
    
    return T_B

#------ Create a comparison radiance for a reasonable surface temperature (using T = 290 K)
def planck_radiance(wnum, T):
    
    C1 = 1.191042722E-12		
    C2 = 1.4387752			# units are [K cm]
    C1 = C1 * 1e7			# units are now [mW/m2/ster/cm-4]
    rad = C1 * wnum * wnum * wnum / (np.exp(C2 * wnum / T)-1)
    
    return rad

#------ Plot the spectra
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, radiance_lw, label="Longwave IR", color="black", linewidth=0.5)
plt.plot(wnum_sw, radiance_sw, label="Shortwave IR", color="black", linewidth=0.5)

plt.plot(wnum_lw, planck_radiance(wnum_lw, 290), color="blue", linewidth=1)
plt.plot(wnum_sw, planck_radiance(wnum_sw, 290), color="blue", linewidth=1)
plt.xlim(500, 2500)
plt.ylim(-5, 160)

label_x = 1500
label_y = np.interp(label_x, wnum_lw, planck_radiance(wnum_lw, 290))
plt.text(label_x, label_y, "290 K Blackbody", color="blue", fontsize=10, va='bottom', rotation=-25)

plt.xlabel("Wavenumber (cm⁻¹)")
plt.ylabel("Radiance (mW/m²/sr/cm⁻¹)")
plt.title("Infrared Spectrum from ASSIST (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"/spectra_ground_rad", dpi=200, bbox_inches='tight')
plt.close()

#------ Get brightness temperature from CrIS radiance data
TB_lw = radiance_to_brightness_temp(radiance_lw, wnum_lw)
TB_sw = radiance_to_brightness_temp(radiance_sw, wnum_sw)

#------ Plot brightness temperature by wavenumber
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, TB_lw, label="Longwave IR", color="black", linewidth=0.5)
plt.plot(wnum_sw, TB_sw, label="Shortwave IR", color="black", linewidth=0.5)
plt.xlim(500, 2500)

plt.xlabel("Wavenumber (cm-1)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from ASSIST (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"spectra_ground_bt_wn", dpi=200, bbox_inches='tight')
plt.close()

#------ Convert wavenumber (cm⁻¹) to wavelength (um)
wl_lw = 10000/wnum_lw
wl_sw = 10000/wnum_sw

#------ Plot brightness temperature by wavelength
fig = plt.figure(figsize=(10, 5))
plt.plot(wl_lw, TB_lw, label="Longwave IR", color="black", linewidth=0.5)
plt.plot(wl_sw, TB_sw, label="Shortwave IR", color="black", linewidth=0.5)
plt.xlim(4, 15)
plt.ylim(150, 400)

plt.xlabel("Wavelength (μm)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from ASSIST (Boulder CO) \n 2024-07-22 19:17 UTC")
plt.grid(color='#d3d3d3')

fig.savefig(save_path+"spectra_ground_bt_wl", dpi=200, bbox_inches='tight')
plt.close()