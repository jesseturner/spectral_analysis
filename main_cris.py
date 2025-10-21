from CrIS_utils import cris_utils as c_utils
import os

#--- Download CrIS data
# c_utils.download_cris_data(date_start="2025-03-12", date_end="2025-03-12", lon_west=-73, lat_south=33, lon_east=-57, lat_north=46)

cris_dir = "CrIS_data/"
cris_file = "SNDR.J1.CRIS.20250312T0642.m06.g068.L1B.std.v03_08.G.250312132403.nc"
file_path = os.path.join(cris_dir, cris_file)

#=== FLC case
target_lat = 40
target_lon = -67.75
ylim = (271, 280)

#=== Null case
# target_lat = 35.75
# target_lon = -69.25
# ylim = (282, 291)

#--- Get brightness temperature spectra for point
ds = c_utils.open_cris_data(file_path)
ds = c_utils.isolate_target_point(ds, target_lat=target_lat, target_lon=target_lon)
print(ds)

df = c_utils.get_brightness_temperature(ds)
print(df)

#--- Plot brightness temperature
lat = f"{ds['lat'].values:.2f}"
lon = f"{ds['lon'].values:.2f}"
save_name = f"{cris_file.split(".")[1]}_{cris_file.split(".")[3]}_{ds['lat'].values:.0f}_{ds['lon'].values:.0f}"
plot_title = f"CrIS 2025-03-12 ({lat}, {lon}) \n j01 d20250312 t0642"

# c_utils.plot_brightness_temperature(df, fig_dir="CrIS_plot", fig_name=save_name, fig_title=plot_title)
c_utils.plot_btd_freq_range(df,
    fig_dir='CrIS_plot', fig_name=f'btd_{save_name}', fig_title=plot_title,
    freq_range1=[833, 952], freq_range2=[2430, 2555], ylim=ylim)

#--- Get BTD value from SRF
c_utils.create_fake_srf(name="M12_FAKE", full_range=(3200, 4250), response_range=(3900, 4000))
band = "M12_FAKE"
srf_file = f"VIIRS_spectral_response_functions/NPP_VIIRS_NG_RSR_{band}.dat"
c_utils.get_Tb_from_srf(df, srf_file)