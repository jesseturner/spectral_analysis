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
# c_utils.plot_btd_freq_range(df,
#     fig_dir='CrIS_plot', fig_name=f'btd_{save_name}', fig_title=plot_title,
#     freq_range1=[833, 952], freq_range2=[2430, 2555], ylim=ylim)


#=== Temp: for running following lines
band_lw = 10.90
band_str = str(band_lw).replace(".", "")

#--- Create fake SRF
band_lw_start = int(band_lw*1000)-1
band_lw_mid = int(band_lw*1000)
band_lw_end = int(band_lw*1000)+1
srf_file = f"spectral_response_functions/VIIRS_NG_RSR_{band_str}.dat"

c_utils.create_fake_srf(name=f"line_{band_str}", 
    full_range=(band_lw_start, band_lw_end), 
    response_range=(band_lw_mid, band_lw_mid),
    save_path=srf_file)

#--- Get BTD value from SRF
# c_utils.get_Tb_from_srf(df, srf_file)

#--- Plot brightness temperature with VIIRS SRFs
xlim = (9, 12)
ylim = (274, 281)
freq_range =[10000/xlim[1], 10000/xlim[0]]
# srf_file0 = f"spectral_response_functions/line_{band_str}.dat"
# srf_file1 = "spectral_response_functions/NPP_VIIRS_NG_RSR_M15_filtered_Oct2011f_BA.dat"
#srf_file2 = "spectral_response_functions/GOES-R_ABI_SRF_ch14.dat"
srf_file_list = [srf_file]
srf_name_list = [f"{band_lw} μm"]
color_list = ["#4A8FE7"]

c_utils.plot_freq_range_srf(df, srf_file_list, srf_name_list, color_list,
    fig_dir='CrIS_plot', fig_name=f'band{band_str}_{save_name}', fig_title=plot_title,
    freq_range=freq_range, ylim=ylim, xlim=xlim)

#--- Plot CrIS spatially
ds = c_utils.open_cris_data(file_path)
ds_t_11, ds_11 = c_utils.get_cris_spatial_brightness_temp(ds, wl_sel=band_lw)
ds_t_3_9, ds_3_9 = c_utils.get_cris_spatial_brightness_temp(ds, wl_sel=3.95)
ds_btd = ds_t_11 - ds_t_3_9

c_utils.plot_cris_spatial(ds_btd, ds_3_9['lat'], ds_3_9['lon'], extent=[-73, -57, 33, 46], 
    fig_dir="CrIS_plot", fig_name=f"spatial_{band_str}_{save_name}", 
    fig_title=f"CrIS Brightness Temperature ({band_lw} - 3.95 μm) \n j01 d20250312 t0642", 
    is_btd=True)
