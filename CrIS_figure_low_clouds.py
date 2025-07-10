import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os
from datetime import datetime

#--- Path to CrIS data and figure save directory
cris_dir = "CrIS_data/"
file_name_flc = "SNDR.J1.CRIS.20250612T0618.m06.g064.L1B.std.v03_08.G.250612135622.nc"
file_name_low_cld = "SNDR.SNPP.CRIS.20250707T0624.m06.g065.L1B.std.v03_28.G.250707135332.nc"
file_name_high_cld = "SNDR.J1.CRIS.20250703T0624.m06.g065.L1B.std.v03_08.G.250703135751.nc"

#--- Target location within the CrIS swath
target_lat = 41.3
target_lon = -67.25

save_path = "CrIS_figures/"
location_name = "Gulf of Maine"
save_name = location_name.lower().replace(" ", "_")

#--- get brightness temperature from file
def getCrisData(file_name):

    datetime_str = file_name.split('.')[3]
    dt = datetime.strptime(datetime_str, "%Y%m%dT%H%M")

    #--- Opening CrIS file
    ds = xr.open_dataset(cris_dir+file_name)
    os.makedirs(os.path.dirname(save_path), exist_ok=True)

    #--- Isolating the targeted point
    abs_diff = np.abs(ds['lat'] - target_lat) + np.abs(ds['lon'] - target_lon).values
    atrack_idx, xtrack_idx, fov_idx = np.unravel_index(abs_diff.argmin(), abs_diff.shape)
    ds_target = ds.isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx)

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


    #------ Get brightness temperature from CrIS radiance data
    TB_lw = radiance_to_brightness_temp(radiance_lw, wnum_lw)
    TB_mw = radiance_to_brightness_temp(radiance_mw, wnum_mw)
    TB_sw = radiance_to_brightness_temp(radiance_sw, wnum_sw)

    return wl_lw, wl_mw, wl_sw, TB_lw, TB_mw, TB_sw, dt

#--- Run the function to get the data
wl_lw, wl_mw, wl_sw, flc_TB_lw, flc_TB_mw, flc_TB_sw, flc_dt = getCrisData(file_name_flc)
wl_lw, wl_mw, wl_sw, cld_TB_lw, cld_TB_mw, cld_TB_sw, cld_dt = getCrisData(file_name_low_cld)
wl_lw, wl_mw, wl_sw, hc_TB_lw, hc_TB_mw, hc_TB_sw, hc_dt = getCrisData(file_name_high_cld)

#------ Plot brightness temperature by wavelength
fig = plt.figure(figsize=(10, 5))
plt.plot(wl_lw, flc_TB_lw, label=f"False Low Cloud ({flc_dt.strftime('%Y-%m-%d')})", color="black", linewidth=0.5)
plt.plot(wl_mw, flc_TB_mw, color="black", linewidth=0.5)
plt.plot(wl_sw, flc_TB_sw, color="black", linewidth=0.5)
plt.plot(wl_lw, cld_TB_lw, label=f"Low Clouds ({cld_dt.strftime('%Y-%m-%d')})", color="blue", linewidth=0.5)
plt.plot(wl_mw, cld_TB_mw, color="blue", linewidth=0.5)
plt.plot(wl_sw, cld_TB_sw, color="blue", linewidth=0.5)
plt.plot(wl_lw, hc_TB_lw, label=f"High Clouds ({hc_dt.strftime('%Y-%m-%d')})", color="lightblue", linewidth=0.5)
plt.plot(wl_mw, hc_TB_mw, color="lightblue", linewidth=0.5)
plt.plot(wl_sw, hc_TB_sw, color="lightblue", linewidth=0.5)
plt.xlim(4, 15)
plt.ylim(200, 300)

fig.legend()

plt.xlabel("Wavelength (μm)")
plt.ylabel("Brightness Temperature (K)")
plt.title(f"Brightness Temperature Spectrum from CrIS ({location_name})")
plt.grid(color='#d3d3d3')

fig.savefig(f"{save_path}/{save_name}_spectra_bt_example_wl", dpi=200, bbox_inches='tight')
plt.close()