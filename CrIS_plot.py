import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import os

cris_dir = "CrIS_data/"
file_name = "SNDR.J1.CRIS.20240722T0930.m06.g096.L1B.std.v03_08.G.240722160620.nc"
#file_name = "SNDR.J1.CRIS.20240722T1912.m06.g193.L1B.std.v03_08.G.240723022056.nc"
save_path = "CrIS_figures/"

ds = xr.open_dataset(cris_dir+file_name)
os.makedirs(os.path.dirname(save_path), exist_ok=True)



#--- Plot satellite track
lat = ds["lat"].values  # (atrack, xtrack, fov)
lon = ds["lon"].values  # (atrack, xtrack, fov)
# Reduce dimensions (e.g., take the central FOV for a simpler plot)
central_fov = lat.shape[2] // 2  # Middle FOV index
lat = lat[:, :, central_fov]  # Shape (atrack, xtrack)
lon = lon[:, :, central_fov]
# Create the figure and map projection
fig, ax = plt.subplots(figsize=(10, 5), subplot_kw={"projection": ccrs.PlateCarree()})
# Add coastlines and features
ax.add_feature(cfeature.COASTLINE, linewidth=0.8)
ax.add_feature(cfeature.BORDERS, linewidth=0.5, linestyle="dotted")
ax.add_feature(cfeature.LAND, facecolor="lightgray")
ax.gridlines(draw_labels=True, linestyle="--")
#ax.set_extent([np.min(lon)-50, np.max(lon)+50, np.min(lat)-10, np.max(lat)+10], crs=ccrs.PlateCarree())
ax.set_extent([-180, 180, -90, 90], crs=ccrs.PlateCarree())

# Plot the satellite track
ax.scatter(lon, lat, s=1, color="red", transform=ccrs.PlateCarree(), label="Satellite Track")
# Add a title and legend
ax.set_title("Satellite Track from CrIS Instrument")
ax.legend()

fig.savefig(save_path+"satellite_track", dpi=200, bbox_inches='tight')
plt.close()



#--- Plot first spectra in dataset
# Select the first observation (atrack=0, xtrack=0, fov=0)
atrack_idx, xtrack_idx, fov_idx = 20, 20, 5

# Extract wavenumbers and corresponding radiance values
wnum_lw = ds["wnum_lw"].values  # Longwave IR
wnum_mw = ds["wnum_mw"].values  # Midwave IR
wnum_sw = ds["wnum_sw"].values  # Shortwave IR

radiance_lw = ds["rad_lw"].isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx).values  # Longwave radiance
radiance_mw = ds["rad_mw"].isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx).values  # Midwave radiance
radiance_sw = ds["rad_sw"].isel(atrack=atrack_idx, xtrack=xtrack_idx, fov=fov_idx).values  # Shortwave radiance

print(ds["rad_lw"])

# Convert wavenumber to wavelength
wl_lw = 10000/wnum_lw # cm-1 to um
wl_mw = 10000/wnum_mw
wl_sw = 10000/wnum_sw

# Plot the spectra
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, radiance_lw, label="Longwave IR", color="red")
plt.plot(wnum_mw, radiance_mw, label="Midwave IR", color="blue")
plt.plot(wnum_sw, radiance_sw, label="Shortwave IR", color="green")

# Formatting the plot
plt.xlabel("Wavenumber (cm⁻¹)")
plt.ylabel("Radiance (mW/m²/sr/cm⁻¹)")
plt.title("Infrared Spectrum from CrIS (First Observation)")
plt.legend()
plt.grid()

fig.savefig(save_path+"/spectra_example", dpi=200, bbox_inches='tight')
plt.close()



# def radiance_to_brightness_temp(radiance, wavenumber):

#     # Convert units
#     wl = 1 / wavenumber / 1e2 # cm-1 to m
#     B = radiance / (1000/100) # mW/(m2 sr cm-1) to W/(m2 sr m)


#     # Constants
#     # h = 6.62607015e-34  # Planck's constant (J·s)
#     # c = 3e8  # Speed of light (m/s)
#     # k_B = 1.380649e-23  # Boltzmann constant (J/K)

#     c = 299792458 #m/s
#     h = 6.6260755e-34 #Js
#     k = 1.380658e-23 #J/K

#     c1 = 2*h*c*c  #W m2
#     c2 = h*c/k    #K m

#     # Apply inverse Planck's law
#     T_B = c2 / ( wl * np.log( c1/( (wl**5) * B ) + 1 ) )
#     #T_B = (h * c) / (k_B * wl) / np.log((2 * h * c**2) / (wl**5 * I) + 1)
    
#     return T_B

def radiance_to_brightness_temp(radiance, wavenumber):

    # Convert units
    wl = (10000 / wavenumber) * 1e-6 # cm-1 to m
    B = radiance/1000 # mW/(m2 sr cm-1) to W/(m2 sr m)

    # Constants
    c = 2.99792458e8       # m/s
    h = 6.62607015e-34     # J*s
    k = 1.380649e-23       # J/K

    # Planck constants
    c1 = 2 * h * c**2      # W·m²·sr⁻¹
    c2 = h * c / k         # K·m

    # Apply inverse Planck's law
    T_B = c2 / (wl * np.log(c1 / (wl**5 * B) + 1))
    
    return T_B

# Apply the conversion to each radiance spectrum
TB_lw = radiance_to_brightness_temp(radiance_lw, wnum_lw)  # Longwave IR
TB_mw = radiance_to_brightness_temp(radiance_mw, wnum_mw)  # Midwave IR
TB_sw = radiance_to_brightness_temp(radiance_sw, wnum_sw)  # Shortwave IR

print(TB_lw)


# Plot the brightness temperature spectra
fig = plt.figure(figsize=(10, 5))
# plt.plot(wl_lw, TB_lw, label="Longwave IR", color="red")
# plt.plot(wl_mw, TB_mw, label="Midwave IR", color="blue")
# plt.plot(wl_sw, TB_sw, label="Shortwave IR", color="green")
plt.plot(wnum_lw, TB_lw, label="Longwave IR", color="red")
plt.plot(wnum_mw, TB_mw, label="Midwave IR", color="blue")
plt.plot(wnum_sw, TB_sw, label="Shortwave IR", color="green")

# Formatting the plot
#plt.xlabel("Wavelength (μm)")
plt.xlabel("Wavenumber (cm-1)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (First Observation)")
plt.legend()
plt.grid()

fig.savefig(save_path+"spectra_bt_example", dpi=200, bbox_inches='tight')
plt.close()