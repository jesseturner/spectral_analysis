import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np

cris_dir = "CrIS_data/"
file_name = "SNDR.J1.CRIS.20240721T2354.m06.g240.L1B.std.v03_08.G.240722081402.nc"

ds = xr.open_dataset(cris_dir+file_name)
print(ds)



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

fig.savefig("CrIS_figures/satellite_track", dpi=200, bbox_inches='tight')
plt.close()



#--- Plot first spectra in dataset
# Select the first observation (atrack=0, xtrack=0, fov=0)
atrack_idx, xtrack_idx, fov_idx = 0, 0, 0

# Extract wavenumbers and corresponding radiance values
wnum_lw = ds["wnum_lw"].values  # Longwave IR
wnum_mw = ds["wnum_mw"].values  # Midwave IR
wnum_sw = ds["wnum_sw"].values  # Shortwave IR

radiance_lw = ds["nedn_lw"].isel(fov=fov_idx).values  # Longwave radiance
radiance_mw = ds["nedn_mw"].isel(fov=fov_idx).values  # Midwave radiance
radiance_sw = ds["nedn_sw"].isel(fov=fov_idx).values  # Shortwave radiance

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

fig.savefig("CrIS_figures/spectra_example", dpi=200, bbox_inches='tight')
plt.close()


#--- Plot the brightness temperature
# Constants
h = 6.62607015e-34  # Planck's constant (J·s)
c = 3e8  # Speed of light (m/s)
k_B = 1.380649e-23  # Boltzmann constant (J/K)

# Convert radiance to brightness temperature (for each wavenumber)
def radiance_to_brightness_temp(radiance, wavenumber):
# Convert wavenumber from cm^-1 to Hz
    nu = wavenumber * 1e2 * c  # cm^-1 to Hz

    L = radiance * (1e-3 / 3e10)
    
# Apply inverse Planck's law
    TB = (h * nu / k_B) * ((np.log(((2 * h * nu**3) / (c**2 * L)) + 1))**(-1))
    return TB

# Apply the conversion to each radiance spectrum
TB_lw = radiance_to_brightness_temp(radiance_lw, wnum_lw)  # Longwave IR
TB_mw = radiance_to_brightness_temp(radiance_mw, wnum_mw)  # Midwave IR
TB_sw = radiance_to_brightness_temp(radiance_sw, wnum_sw)  # Shortwave IR

print(TB_lw)

# Plot the brightness temperature spectra
fig = plt.figure(figsize=(10, 5))
plt.plot(wnum_lw, TB_lw, label="Longwave IR", color="red")
plt.plot(wnum_mw, TB_mw, label="Midwave IR", color="blue")
plt.plot(wnum_sw, TB_sw, label="Shortwave IR", color="green")

# Formatting the plot
plt.xlabel("Wavenumber (cm⁻¹)")
plt.ylabel("Brightness Temperature (K)")
plt.title("Brightness Temperature Spectrum from CrIS (First Observation)")
plt.legend()
plt.grid()

fig.savefig("CrIS_figures/spectra_bt_example", dpi=200, bbox_inches='tight')
plt.close()