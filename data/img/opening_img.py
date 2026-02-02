import xarray as xr

ds = xr.open_dataset("data/img/SNDR.J1.CRIS.20250312T0636.m06.g067.IMG_COL.std.v2_5.W.250312191128.nc")
print(ds)
print(ds.attrs)