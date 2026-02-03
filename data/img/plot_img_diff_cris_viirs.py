import xarray as xr

ds = xr.open_dataset("data/img/SNDR.J1.CRIS.20250312T0642.m06.g068.IMG.std.v2_5.W.250312191129.nc")
print(ds)
print(ds.attrs)
print(ds['viirs_emis_band'])

subset = "All pixels"
bt_m15 = ds.viirs_bt.sel(viirs_emis_band='M15 (10.8μm)', viirs_subset=subset)
bt_m13 = ds.viirs_bt.sel(viirs_emis_band='M13 (4.05μm)', viirs_subset=subset)

btd_viirs = (bt_m15 - bt_m13).mean(dim="fov")
print(btd_viirs)

print(ds.viirs_cris_band.values)
cris_bt_m15 = ds.cris_bt.sel(viirs_cris_band="M15 (10.8μm)")
cris_bt_m13 = ds.cris_bt.sel(viirs_cris_band="M13 (4.05μm)")

btd_cris = (cris_bt_m15 - cris_bt_m13).mean(dim="fov")
lat2d = ds.lat.mean(dim="fov")
lon2d = ds.lon.mean(dim="fov")

import matplotlib.pyplot as plt
import cartopy.crs as ccrs

btd_diff = btd_viirs - btd_cris

projection=ccrs.PlateCarree(central_longitude=0)
fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

c = ax.pcolormesh(
    lon2d,
    lat2d,
    btd_diff,
    transform=ccrs.PlateCarree(),
    cmap='RdBu_r',
    shading='auto'
)

clb = plt.colorbar(c, shrink=0.6, pad=0.02, ax=ax)
clb.ax.tick_params(labelsize=15)
clb.set_label('(K)', fontsize=15)

# ax.set_extent([extent[0], extent[1], extent[2], extent[3]], crs=ccrs.PlateCarree())
ax.coastlines(resolution='50m', color='black', linewidth=2)

ax.set_title("BTD Difference: VIIRS - CrIS", fontsize=20, pad=10)

plt.show()
