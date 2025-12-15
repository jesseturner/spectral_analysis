from modules_cris import cris_utils as c_utils
import os

#--- Download CrIS data
# c_utils.download_cris_data(date_start="2025-03-12", date_end="2025-03-12", lon_west=-73, lat_south=33, lon_east=-57, lat_north=46)

cris_dir = "data/cris/"
cris_file = "SNDR.J1.CRIS.20250312T0642.m06.g068.L1B.std.v03_08.G.250312132403.nc"
file_path = os.path.join(cris_dir, cris_file)

#=== FLC case
# target_lat = 40
# target_lon = -67.75
# ylim = (268, 280)

#=== Null case
# target_lat = 36
# target_lon = -72
# ylim = (280, 292)

#=== Custom case
target_lat = 42.46
target_lon = -64.99
ylim = (271, 278)

#--- Get brightness temperature spectra for point
ds = c_utils.open_cris_data(file_path)
ds = c_utils.isolate_target_point(ds, target_lat=target_lat, target_lon=target_lon)

df = c_utils.get_brightness_temperature(ds)

#--- Plot brightness temperature
lat = f"{ds['lat'].values:.2f}"
lon = f"{ds['lon'].values:.2f}"
save_name = f"{cris_file.split(".")[1]}_{cris_file.split(".")[3]}_{ds['lat'].values:.0f}_{ds['lon'].values:.0f}"
plot_title = f"CrIS 2025-03-12 ({lat}, {lon}) \n j01 d20250312 t0642"

c_utils.plot_brightness_temperature(df, fig_dir="plots", fig_name=save_name, 
    fig_title=plot_title, xlim=(10,12), ylim=ylim)
# c_utils.plot_btd_freq_range(df,
#     fig_dir='plots', fig_name=f'btd_{save_name}', fig_title=plot_title,
#     freq_range1=[833, 952], freq_range2=[2430, 2555], ylim=ylim)

#=== Temp: for running following lines
band_sel = [10.302640]
band_name = f"10.30 μm"
save_name = "longwave_custom"

#--- Create fake SRF
srf_file = f"data/spectral_response_functions/VIIRS_NG_RSR_{save_name}.dat"
c_utils.create_fake_srf_lines(name=f"line_{save_name}", 
    lines=band_sel, 
    save_path=srf_file)

#--- Get BTD value from SRF
c_utils.get_Tb_from_srf(df, srf_file)

#--- Plot brightness temperature with VIIRS SRFs
xlim = (3.9, 4.2)
# ylim = (274, 281)
freq_range =[10000/xlim[1], 10000/xlim[0]]
srf_file_list = [srf_file]
color_list = ["#4A8FE7"]

c_utils.plot_freq_range_srf(df, srf_file_list, band_sel, color_list,
    fig_dir='plots', fig_name=f'band_{save_name}', fig_title=plot_title,
    freq_range=freq_range, ylim=ylim, xlim=xlim)

#--- Plot CrIS spatially
ds = c_utils.open_cris_data(file_path)
ds_t_11, ds_11 = c_utils.get_cris_band_Tb(ds, srf_file=srf_file)
ds_t_3_9, ds_3_9 = c_utils.get_cris_band_Tb(ds, 
    srf_file="data/spectral_response_functions/GOES-R_ABI_SRF_ch7.dat")
ds_btd = ds_t_11 - ds_t_3_9

c_utils.plot_cris_spatial(ds_btd, ds_3_9['lat'], ds_3_9['lon'], extent=[-73, -57, 33, 46], 
    fig_dir="plots", fig_name=f"spatial_{save_name}", 
    fig_title=f"CrIS Brightness Temperature ({band_name} - 3.95 μm) \n j01 d20250312 t0642", 
    is_btd=True, pin_coords=(target_lat, target_lon))
