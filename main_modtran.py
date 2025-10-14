from MODTRAN_utils import modtran_utils as m_utils

#--- Create JSON from SST and GFS
# gfs_filepath = "/home/jturner/FLC_data/model_data/gfs_20250312_06z"
# sst_filepath = "/home/jturner/FLC_data/model_data/sst_20250312"
# title = "GFS and SST vertical profile (2025-03-12)"
# desc = "2025031206_40_67-75"
# json_path = f"MODTRAN_json/{desc}.json"

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat=40, lon=-67.75)
# m_utils.plot_skew_t_from_profile(df, title, fig_dir="MODTRAN_json", fig_name=desc)
# m_utils.create_modtran_json_from_df(df, json_path)

#=== FLC case
json_path = "MODTRAN_json/2025031206_40_67-75.json"
title_name = '2025-03-12 (40, -67.75)'
ylim = (271, 280)
fig_name = "2025031206_flc"

#=== Null case
# json_path = "MODTRAN_json/2025031206_35-75_69-25_med_res.json"
# title_name = '2025-03-12 (35.75, -69.25)'
# ylim = (282, 291)
# fig_name = "2025031206_null"

#--- Run modtran with JSON settings
m_utils.run_modtran(json_path)

df1 = m_utils.open_tp7_file("flc_custom1.tp7")
df2 = m_utils.open_7sc_file("flc_custom1.7sc") #--- Necessary for adjusting resolution

#--- Plot BTD spectra
# m_utils.plot_btd_freq_range(df2, title_name=title_name, 
#     fig_dir='MODTRAN_plot', fig_name=fig_name,
#     freq_range1=[1e4/11.6, 1e4/9.9], freq_range2=[1e4/3.9, 1e4/3.5], ylim=ylim)

#--- Get BTD value from SRF
band = "M12"
if band == "M15":   
    central_wl = 10.763e-6
if band == "M12":
    central_wl = 3.7e-6
srf_file = f"VIIRS_spectral_response_functions/NPP_VIIRS_NG_RSR_{band}_filtered_Oct2011f_BA.dat"
m_utils.get_Tb_from_srf(df2, srf_file, central_wl=central_wl)

#--- Getting atmospheric profiles for cases
# gfs_filepath = "/home/jturner/FLC_data/model_data/gfs_20250312_06z"
# sst_filepath = "/home/jturner/FLC_data/model_data/sst_20250312"
# lat, lon = 40.75, -67.75

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat, lon)
# print(df)

# m_utils.plot_skew_t_from_profile(df, title="GFS and SST vertical profile (2025-03-12)", fig_dir="/home/jturner/spectral_analysis", fig_name="gfs_vertical_profile_20250312")

