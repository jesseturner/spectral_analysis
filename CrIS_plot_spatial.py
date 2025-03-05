import cartopy.crs as ccrs
import cartopy.feature as cfeature
import matplotlib.pyplot as plt
import xarray as xr
import numpy as np
import matplotlib.patches as patches

cris_dir = "CrIS_data/"
file_name = "SNDR.J1.CRIS.20240722T0930.m06.g096.L1B.std.v03_08.G.240722160620.nc"

ds = xr.open_dataset(cris_dir+file_name)

#--- Subset to wavenumber of 900 cm-1 (~ 11um)
#------- Selecting the first field of view (chosen arbitrarily, I don't know what this means)
ds_wn_900 = ds.sel(wnum_lw=900, fov=0)

#--- Boulder CO
# latitude_north = 40.062
# latitude_south = 39.98
# longitude_west = -105.31
# longitude_east = -105.2

#--- Colorado
latitude_north = 41.0
latitude_south = 37.0
longitude_west = -109.05
longitude_east = -102.04

print("rad LW:", np.shape(ds_wn_900['rad_lw'].values))
print("nedn LW:", np.shape(ds_wn_900['nedn_lw'].values))

#--- Plot the radiance
projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})
levels = np.linspace(np.min(ds_wn_900['rad_lw'].values), np.max(ds_wn_900['rad_lw'].values), 30)

c = ax.pcolormesh(ds_wn_900['lon'], ds_wn_900['lat'], ds_wn_900['rad_lw'], cmap='Greys', shading='auto')
#c=ax.contourf(ds_wn_900['lon'], ds_wn_900['lat'], ds_wn_900['rad_lw'], cmap='Greys', extend='both', levels=levels)

clb = plt.colorbar(c, shrink=0.4, pad=0.02, ax=ax)
clb.ax.tick_params(labelsize=15)
clb.set_label('Radiance (mW/m²/sr/cm⁻¹)', fontsize=15)

#--- Set the geographical limits of the figure
ax.set_extent([longitude_west, longitude_east, latitude_south, latitude_north], crs=ccrs.PlateCarree())

#--- Coastlines
ax.coastlines(resolution='50m', color='gray', linewidth=1)

#--- Counties
counties = cfeature.NaturalEarthFeature(
    category='cultural',
    name='admin_2_counties',
    scale='10m',
    facecolor='none')
#ax.add_feature(counties, edgecolor='gray', linewidth=1)

#--- States
ax.add_feature(cfeature.STATES, edgecolor='gray', linewidth=1, zorder=6)


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
gl = ax.gridlines(draw_labels=True, linewidth=1, color='gray', linestyle='--', zorder=5)
gl.top_labels = False
gl.right_labels = False
ax.xaxis.set_major_formatter(plt.FuncFormatter(lambda x, pos: f'{x:.1f}°E' if x >= 0 else f'{-x:.1f}°W'))
ax.yaxis.set_major_formatter(plt.FuncFormatter(lambda y, pos: f'{y:.1f}°N' if y >= 0 else f'{-y:.1f}°S'))

#--- Title
ax.set_title("Boulder, CO at 900 cm$^{-1}$ (~11 μm)", fontsize=20, pad=10)

fig.savefig("CrIS_figures/spatial_20240722", dpi=200, bbox_inches='tight')
plt.close()