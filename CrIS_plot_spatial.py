import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import matplotlib.patches as patches

cris_dir = "CrIS_data/"
file_name = "SNDR.J1.CRIS.20240722T1912.m06.g193.L1B.std.v03_08.G.240723022056.nc"
wnum_sel = 900 #cm-1 (~ 11um)

ds = xr.open_dataset(cris_dir+file_name)

#--- Subset to wavenumber of 900 cm-1 (~ 11um)
#------- Selecting the first field of view, which I believe is the one used for the spectra
ds_wn_900 = ds.sel(wnum_lw=wnum_sel, fov=1)

#--- Colorado
latitude_north = 41.0
latitude_south = 37.0
longitude_west = -109.05
longitude_east = -102.04

print("shape of LW radiation data:", np.shape(ds_wn_900['rad_lw'].values))

#--- Calculate the brightness temperature

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

b_temp_900 = radiance_to_brightness_temp(ds_wn_900['rad_lw'].values, wnum_sel)

#--- Plot the brightness temperature
projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

c = ax.pcolormesh(ds_wn_900['lon'], ds_wn_900['lat'], b_temp_900, cmap='Greys', shading='auto')

clb = plt.colorbar(c, shrink=0.4, pad=0.02, ax=ax)
clb.ax.tick_params(labelsize=15)
clb.set_label('(K)', fontsize=15)

ax.set_extent([longitude_west, longitude_east, latitude_south, latitude_north], crs=ccrs.PlateCarree())
ax.coastlines(resolution='50m', color='gray', linewidth=1)
counties = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_2_counties',
    scale='10m',
    facecolor='none')
ax.add_feature(counties, edgecolor='white', linewidth=1)
ax.add_feature(cfeature.STATES, edgecolor='white', linewidth=1, zorder=6)


#--- Boulder CO bounding box
boulder_bounds = {
    "latitude_north": 40.062,
    "latitude_south": 39.98,
    "longitude_west": -105.31,
    "longitude_east": -105.2
}
rect = patches.Rectangle(
    (boulder_bounds["longitude_west"], boulder_bounds["latitude_south"]),  # Bottom-left corner
    boulder_bounds["longitude_east"] - boulder_bounds["longitude_west"],  # Width
    boulder_bounds["latitude_north"] - boulder_bounds["latitude_south"],  # Height
    linewidth=2, edgecolor='red', facecolor='none', zorder=10
)
ax.add_patch(rect)
ax.text(
    (boulder_bounds["longitude_west"] + boulder_bounds["longitude_east"]) / 2,  # Center longitude
    boulder_bounds["latitude_north"] + 0.1,  # Slightly above the box
    "Boulder, CO",
    fontsize=12, color='red', fontweight='bold',
    horizontalalignment='center', transform=ccrs.PlateCarree()
)

#--- Lat and Lon lines
#gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', linestyle='--', zorder=5)
#gl.top_labels = False
#gl.right_labels = False
#ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'{x:.1f}°E' if x >= 0 else f'{-x:.1f}°W'))
#ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, pos: f'{y:.1f}°N' if y >= 0 else f'{-y:.1f}°S'))

#--- Title
ax.set_title("CrIS Brightness Temperature (900 cm$^{-1}$, ~11 μm) \n (2024-07-22 ~19:17 UTC)", fontsize=20, pad=10)

fig.savefig("CrIS_figures/spatial_20240722", dpi=200, bbox_inches='tight')
plt.close()