# Plotting the training and testing lat-lon points on the ABI image. 

import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import numpy as np

#--- Grab GOES utils from outside path
import sys
sys.path.append("../GOES_Analysis")
from GOES_utils import goes_utils as g_utils

#--- Testing set
# FLC_points = [
#     (43.5, -66.0), 
#     (43.0, -67.0), 
#     (43.0, -66.5), 
#     (43.0, -66.0), 
#     (42.5, -67.5), 
#     (42.5, -67.0), 
#     (42.5, -66.5), 
#     (42.0, -68.0), 
#     (42.0, -67.5), 
#     (41.5, -68.5), 
#     (41.5, -68.0), 
#     (41.5, -65.0), 
#     (41.0, -69.0), 
#     (41.0, -68.5), 
#     (41.0, -65.5), 
#     (41.0, -65.0), 
#     (40.5, -69.5), 
#     (40.5, -69.0), 
#     (40.5, -68.5), 
#     (40.0, -70.0), 
#     (40.0, -69.5), 
#     (40.0, -69.0), 
#     (40.0, -68.5),
#     (39.5, -70.5), 
#     (39.5, -70.0),  
#     (39.5, -69.5), 
#     (39.5, -69.0), 
#     (39.5, -68.5), 
#     (39.5, -68.0),
#     (39.0, -71.0), 
#     (39.0, -70.5), 
#     (39.0, -70.0),  
#     (39.0, -69.5), 
#     (39.0, -69.0), 
#     (39.0, -68.5), 
#     (39.0, -68.0), 
#     (39.0, -67.5), 

# ]
# TLC_points = [
#     (44.5, -65.5), 
#     (44.5, -65.0), 
#     (44.5, -64.5),
#     (44.5, -64.0),
#     (44.5, -63.5),
#     (44.5, -63.0),
#     (44.5, -62.5),
#     (44.5, -62.0),
#     (44.0, -65.5), 
#     (44.0, -65.0), 
#     (44.0, -64.5), 
#     (44.0, -64.0),
#     (44.0, -63.5), 
#     (44.0, -63.0),  
#     (44.0, -62.5), 
#     (43.5, -65.5), 
#     (43.5, -65.0), 
#     (43.5, -64.5), 
#     (43.5, -64.0), 
#     (43.5, -63.5), 
#     (43.5, -63.0), 
#     (43.0, -65.5), 
#     (43.0, -65.0), 
#     (43.0, -64.5), 
#     (43.0, -64.0), 
#     (43.0, -63.5), 
#     (43.0, -63.0), 
#     (42.5, -65.5), 
#     (42.5, -65.0), 
#     (42.5, -64.5), 
#     (42.5, -64.0), 
#     (42.0, -66.0), 
#     (42.0, -65.5), 
#     (42.0, -65.0), 
#     (41.5, -67.0), 
#     (41.5, -66.5), 
#     (41.5, -66.0), 
#     (41.5, -65.5), 
#     ]

#--- Split training points into lon/lat
 

year = 2024
month = 7
day = 12
hour = 6
ten_minutes = 0
band1, wl1 = '13', 10.3
band2, wl2 = '07', 3.9
# sat = 'goes19' # Current GOES-E
sat = 'goes16' # Previous GOES-E
extent=[-73, -57, 33, 46]
g_utils.set_plots_dark() # all following plots will use dark setting

#--- Open GOES ABI data
ds1 = g_utils.get_goes_data(band1, sat, year, month, day, hour, ten_minutes)
ds1 = g_utils.get_region_by_lat_lon(ds1, extent)

ds2 = g_utils.get_goes_data(band2, sat, year, month, day, hour, ten_minutes)
ds2 = g_utils.get_region_by_lat_lon(ds2, extent)

fig_name = f"{sat}_{band1}-{band2}_{year}{month:02}{day:02}_{hour:02}{ten_minutes}0"
plot_title = f"ABI B{band1} - B{band2} ({wl1} µm - {wl2} µm) BTD \n {sat} d{year}{month:02}{day:02} t{hour:02}{ten_minutes}0"

wl1 = round(ds1.band_wavelength.values[0],1)
Tb1 = (ds1.planck_fk2/(np.log((ds1.planck_fk1/ds1.Rad)+1)) - ds1.planck_bc1)/ds1.planck_bc2
wl2 = round(ds2.band_wavelength.values[0],1)
Tb2 = (ds2.planck_fk2/(np.log((ds2.planck_fk1/ds2.Rad)+1)) - ds2.planck_bc1)/ds2.planck_bc2
btd = Tb1 - Tb2

projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

custom_cmap_name = "blueblack"
cmap, norm = g_utils.custom_cmap_selection(custom_cmap_name)
pcm = plt.pcolormesh(btd.lon, btd.lat, btd, cmap=cmap, norm=norm, shading="nearest")

# ax.scatter(
#     FLC_lons, FLC_lats,
#     s=60,
#     c='cyan',
#     marker='o',
#     edgecolors='white',
#     linewidths=0.7,
#     transform=ccrs.PlateCarree(),
#     label='False Low Cloud'
# )

# ax.scatter(
#     TLC_lons, TLC_lats,
#     s=60,
#     c='magenta',
#     marker='^',
#     edgecolors='white',
#     linewidths=0.7,
#     transform=ccrs.PlateCarree(),
#     label='True Low Cloud'
# )

clb = plt.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
clb.ax.tick_params(labelsize=15)
clb.set_label('(K)', fontsize=15)

# ax.legend(
#     loc='lower left',
#     fontsize=12,
#     frameon=True,
#     facecolor='black',
#     edgecolor='white'
# )

if extent: ax.set_extent(extent, crs=ccrs.PlateCarree())
ax.set_title(plot_title, fontsize=20, pad=10)
ax.coastlines(resolution='50m', color='white', linewidth=2)

plt.savefig(f"plots/fig2_testing_set.png", dpi=200, bbox_inches='tight')
plt.close()