from modules_modtran import modtran_utils as m_utils

#--- Create JSON from SST and GFS
# gfs_filepath = "data/gfs/gfs_20250312_06z"
# sst_filepath = "data/gfs/model_data/sst_20250312"
# title = "GFS and SST vertical profile (2025-03-12)"
# desc = "2025031206_40_67-75"
# json_path = f"data/modtran/modtran_json/{desc}.json"

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat=40, lon=-67.75)
# m_utils.plot_skew_t_from_profile(df, title, fig_dir="plots", fig_name=desc)
# m_utils.create_modtran_json_from_df(df, json_path)

#=== FLC case
json_path = "data/modtran/modtran_json/2025031206_40_67-75_cloud.json"
title_name = '2025-03-12 (40, -67.75)'
fig_name = "2025031206_flc_cloud"

#=== Null case
# json_path = "data/modtran/modtran_json/2025031206_35-75_69-25_med_res.json"
# title_name = '2025-03-12 (35.75, -69.25)'
# ylim = (282, 291)
# fig_name = "2025031206_null"

#--- Run modtran with JSON settings
m_utils.run_modtran(json_path)

df1 = m_utils.open_tp7_file("flc_custom1.tp7")
df2 = m_utils.open_7sc_file("flc_custom1.7sc") #--- Necessary for adjusting resolution

#--- Plot brightness temperature
m_utils.plot_brightness_temperature(df2, fig_dir="plots", fig_name=f"MODTRAN_Tb_{fig_name}", 
    fig_title=f"MODTRAN {title_name} \n Profile from GFS and OISST",
    xlim=(3, 12), ylim=(180, 300), line_color="white")

#--- Plot BTD spectra
# m_utils.plot_btd_freq_range(df2, title_name=title_name, 
#     fig_dir='plots', fig_name=fig_name,
#     freq_range1=[1e4/11.6, 1e4/9.9], freq_range2=[1e4/3.9, 1e4/3.5], ylim=ylim)

#--- Get BTD value from SRF
# band = "M12"
# srf_file = f"data/spectral_response_functions/NPP_VIIRS_NG_RSR_{band}_filtered_Oct2011f_BA.dat"
# m_utils.get_Tb_from_srf(df2, srf_file)

#--- Getting atmospheric profiles for cases
# gfs_filepath = "data/gfs/model_data/gfs_20250312_06z"
# sst_filepath = "data/gfs/model_data/sst_20250312"
# lat, lon = 40.75, -67.75

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat, lon)
# print(df)

# m_utils.plot_skew_t_from_profile(df, title="GFS and SST vertical profile (2025-03-12)", fig_dir="plots", fig_name="gfs_vertical_profile_20250312")


#--- Plot brightness temperature with VIIRS SRFs
# description = "lw_zoomed"
# xlim = (10, 12)
# ylim = (268, 280)
# freq_range =[10000/xlim[1], 10000/xlim[0]]
# # srf_file0 = "data/spectral_response_functions/line_395.dat"
# srf_file1 = "data/spectral_response_functions/NPP_VIIRS_NG_RSR_M12_filtered_Oct2011f_BA.dat"
# srf_file2 = "data/spectral_response_functions/GOES-R_ABI_SRF_ch7.dat"
# srf_file3 = "data/spectral_response_functions/NPP_VIIRS_NG_RSR_M15_filtered_Oct2011f_BA.dat"
# srf_file4 = "data/spectral_response_functions/GOES-R_ABI_SRF_ch13.dat"
# srf_file_list = [srf_file1, srf_file2, srf_file3, srf_file4]
# srf_name_list = ["VIIRS M12", "ABI B07", "VIIRS M15", "ABI B13"]
# color_list = ["#3A7CA5", "#A53A3A", "#8FC4E6", "#E68F8F"]

# m_utils.plot_freq_range_srf(df2, srf_file_list, srf_name_list, color_list,
#     fig_dir='plots', fig_name=f'band{description}_{fig_name}', fig_title=f"MODTRAN {title_name} \n Profile from GFS and OISST",
#     freq_range=freq_range, ylim=ylim, xlim=xlim)