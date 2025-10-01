from MODTRAN_utils import modtran_utils as m_utils

json_path = "MODTRAN_json/2025031206_40-75_67-75_high_res.json"

m_utils.run_modtran(json_path)

df1 = m_utils.open_tp7_file("flc_custom1.tp7")
print(df1)

m_utils.plot_btd_freq_range(df1, df_name='2025-03-12 (40.75, -67.75)', 
    fig_dir='MODTRAN_plot', fig_name='2025031206_40-75_67-75_high_res',
    freq_range1=[833, 952], freq_range2=[2430, 2555])

#--- Running FLC case
# gfs_filepath = "/home/jturner/FLC_data/model_data/gfs_20250312_06z"
# sst_filepath = "/home/jturner/FLC_data/model_data/sst_20250312"
# lat, lon = 40.75, -67.75

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat, lon)
# print(df)

# m_utils.plot_skew_t_from_profile(df, title="GFS and SST vertical profile (2025-03-12)", fig_dir="/home/jturner/spectral_analysis", fig_name="gfs_vertical_profile_20250312")

