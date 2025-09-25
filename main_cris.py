from cris_utils import cris_utils as c_utils

#c_utils.download_cris_data(date_start="2025-06-25", date_end="2025-06-25", lon_west=-105.31, lat_south=39.98, lon_east=-105.2, lat_north=40.062)

ds = c_utils.open_cris_data("CrIS_data/SNDR.J1.CRIS.20250625T0854.m06.g090.L1B.std.v03_08.G.250625154750.nc")

ds = c_utils.isolate_target_point(ds, target_lat=42.27, target_lon=-66.25)

c_utils.plot_radiance_spectra(ds, fig_dir="CrIS_plot", fig_name="CrIS_rad")

c_utils.plot_brightness_temperature(ds, fig_dir="CrIS_plot", fig_name="CrIS_Tb")

print(ds)