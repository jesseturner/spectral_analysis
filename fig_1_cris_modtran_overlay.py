from modules_cris import cris_utils as c_utils
from modules_modtran import modtran_utils as m_utils
import os
import matplotlib.pyplot as plt
import numpy as np

cris_dir = "data/cris/"
cris_file = "SNDR.J1.CRIS.20250312T0642.m06.g068.L1B.std.v03_08.G.250312132403.nc"
file_path = os.path.join(cris_dir, cris_file)
c_utils.set_plots_dark()

#====== FLC case ======
# cris_target_lat = 40
# cris_target_lon = -67.75
# modtran_json_path = "data/modtran/modtran_json/2025031206_40_67-75.json"
# fig_name = "fig1_case_FLC"
# plot_title = f"IR Spectra for False Low Cloud"

# ds = c_utils.open_cris_data(file_path)
# ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat, target_lon=cris_target_lon)
# df_cris = c_utils.get_brightness_temperature(ds)
# wl_1, Tb_1 = df_cris["Wavelength (um)"], df_cris["Brightness Temperature (K)"]
# label_1 = "CrIS"
# color_1 = "#1E90FF"

# m_utils.run_modtran(modtran_json_path)
# modtran_df1 = m_utils.open_tp7_file("flc_custom1.tp7")
# modtran_df2 = m_utils.open_7sc_file("flc_custom1.7sc")
# wl_2, Tb_2 = 10000/modtran_df2['FREQ'], modtran_df2['BBODY_T[K]']
# label_2 = "MODTRAN"
# color_2 = "#FF4500"


#====== TLC case ======
# cris_target_lat = 43
# cris_target_lon = -66.22
# modtran_json_path = "data/modtran/modtran_json/2025031206_40_67-75_cloud.json"
# fig_name = "fig1_case_TLC"
# plot_title = f"IR Spectra for True Low Cloud"

# ds = c_utils.open_cris_data(file_path)
# ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat, target_lon=cris_target_lon)
# df_cris = c_utils.get_brightness_temperature(ds)
# wl_1, Tb_1 = df_cris["Wavelength (um)"], df_cris["Brightness Temperature (K)"]
# label_1 = "CrIS"
# color_1 = "#1E90FF"

# m_utils.run_modtran(modtran_json_path)
# modtran_df1 = m_utils.open_tp7_file("flc_custom1.tp7")
# modtran_df2 = m_utils.open_7sc_file("flc_custom1.7sc")
# wl_2, Tb_2 = 10000/modtran_df2['FREQ'], modtran_df2['BBODY_T[K]']
# label_2 = "MODTRAN"
# color_2 = "#FF4500" 


#====== MOD case ======
# modtran_json_path_TLC = "data/modtran/modtran_json/2025031206_40_67-75_cloud.json"
# modtran_json_path_FLC = "data/modtran/modtran_json/2025031206_40_67-75.json"
# fig_name = "fig1_source_MOD"
# plot_title = f"IR Spectra to Distiguish Low Clouds in MODTRAN"

# m_utils.run_modtran(modtran_json_path_TLC)
# modtran_df1_TLC = m_utils.open_tp7_file("flc_custom1.tp7")
# modtran_df2_TLC = m_utils.open_7sc_file("flc_custom1.7sc")
# wl_1, Tb_1 = 10000/modtran_df2_TLC['FREQ'], modtran_df2_TLC['BBODY_T[K]']
# label_1 = "True Low Cloud"
# color_1 = "#00FA9A"

# m_utils.run_modtran(modtran_json_path_FLC)
# modtran_df1_FLC = m_utils.open_tp7_file("flc_custom1.tp7")
# modtran_df2_FLC = m_utils.open_7sc_file("flc_custom1.7sc")
# wl_2, Tb_2 = 10000/modtran_df2_FLC['FREQ'], modtran_df2_FLC['BBODY_T[K]']
# label_2 = "False Low Cloud"
# color_2 = "#1E90FF"

#====== CrIS case ======
# cris_target_lat_FLC = 40
# cris_target_lon_FLC = -67.75
# cris_target_lat_TLC = 43
# cris_target_lon_TLC = -66.22
# fig_name = "fig1_source_CrIS"
# plot_title = f"IR Spectra to Distiguish Low Clouds in CrIS"

# ds = c_utils.open_cris_data(file_path)
# ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat_TLC, target_lon=cris_target_lon_TLC)
# df_cris_TLC = c_utils.get_brightness_temperature(ds)
# wl_1, Tb_1 = df_cris_TLC["Wavelength (um)"], df_cris_TLC["Brightness Temperature (K)"]
# label_1 = "True Low Cloud"
# color_1 = "#00FA9A"

# ds = c_utils.open_cris_data(file_path)
# ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat_FLC, target_lon=cris_target_lon_FLC)
# df_cris_FLC = c_utils.get_brightness_temperature(ds)
# wl_2, Tb_2 = df_cris_FLC["Wavelength (um)"], df_cris_FLC["Brightness Temperature (K)"]
# label_2 = "False Low Cloud"
# color_2 = "#1E90FF"

#====== ====== ======

#--- 1. Plot brightness temperature overlay

# fig, ax = plt.subplots(figsize=(10, 5))
# ax.set_facecolor('black')

# ax.plot(wl_1, Tb_1, 
#         color=color_1, 
#         linewidth=0.5, 
#         label=label_1)
# ax.plot(wl_2, Tb_2, 
#         color=color_2, 
#         linewidth=0.5, 
#         label=label_2)
# ax.set_xlim((3,12))
# ax.set_ylim((180,300))

# ax.set_xlabel("Wavelength (μm)")
# ax.set_ylabel("Brightness Temperature (K)")
# ax.set_title(plot_title)
# ax.legend()

# plt.savefig(f"plots/{fig_name}.png", dpi=200, bbox_inches='tight')
# plt.close()

#--- 2. plot brightness temperature difference

# fig, ax = plt.subplots(figsize=(10, 5))
# ax.set_facecolor('black')

# wl = wl_1
# Tb_diff = Tb_2 - Tb_1

# ax.plot(wl, Tb_diff, 
#         color="white", 
#         linewidth=0.5, 
#         label=f"{label_1} - {label_2}")
# ax.set_xlim((3,12))
# ax.set_ylim((-10,10))

# ax.set_xlabel("Wavelength (μm)")
# ax.set_ylabel("Brightness Temperature Difference (K)")
# ax.set_title(plot_title)
# ax.legend()

# plt.savefig(f"plots/{fig_name}_diff.png", dpi=200, bbox_inches='tight')
# plt.close()

#--- 3. Getting random assortment of atmospheres (FLC and TLC)
#------ Incomplete
# gfs_filepath = "data/gfs/gfs_20250312_06z"
# sst_filepath = "data/gfs/model_data/sst_20250312"
# title = "GFS and SST vertical profile (2025-03-12)"
# desc = "2025031206_40_67-75"
# json_path = f"data/modtran/modtran_json/{desc}.json"

# df = m_utils.profile_from_gfs_and_sst(gfs_filepath, sst_filepath, lat=40, lon=-67.75)
# m_utils.plot_skew_t_from_profile(df, title, fig_dir="plots", fig_name=desc)
# m_utils.create_modtran_json_from_df(df, json_path)

#--- 4. Getting average spectra from CrIS
FLC_points = [(40, -67.75), (40.5, -67.80), (40.6,-67.18), (40.47, -66.63), (40.93, -66.79), (40.5, -68.4), (40, -68.8), (40, -69), (40, -69.4), (39.6, -70), (39.3, 70.6), (39.3, 71)]
TLC_points = [(41.99, -67.78), (42.56, 66.77), (42.53, -66.21), (43.02, -66.22), (42.98, -65.63), (42.84, -65.19), (42.91, -64.77), (42.57, -64.79), (42.50, -65.21)]

fig_name = "fig1_source_CrIS_average"
plot_title = "IR Spectra to Distinguish Low Clouds in CrIS"

def get_category_stats(ds_func, points):
    """
    Given a list of lat/lon points, return the wavelengths, average Tb, and variance of Tb.
    """
    all_Tb = []

    for lat, lon in points:
        ds = ds_func(file_path)
        ds = c_utils.isolate_target_point(ds, target_lat=lat, target_lon=lon)
        df_cris = c_utils.get_brightness_temperature(ds)
        wl = df_cris["Wavelength (um)"]
        Tb = df_cris["Brightness Temperature (K)"].values
        all_Tb.append(Tb)

    all_Tb = np.array(all_Tb)
    Tb_mean = np.mean(all_Tb, axis=0)
    Tb_min = np.min(all_Tb, axis=0)
    Tb_max = np.max(all_Tb, axis=0)

    return wl, Tb_mean, Tb_min, Tb_max

# Compute stats for each category
wl_FLC, Tb_mean_FLC, Tb_min_FLC, Tb_max_FLC = get_category_stats(c_utils.open_cris_data, FLC_points)
wl_TLC, Tb_mean_TLC, Tb_min_TLC, Tb_max_TLC = get_category_stats(c_utils.open_cris_data, TLC_points)

# Plotting
plt.figure(figsize=(10,6))
plt.plot(wl_FLC, Tb_mean_FLC, label="False Low Cloud (Mean)", color="#1E90FF")
plt.fill_between(wl_FLC, Tb_min_FLC, Tb_max_FLC, color="#1E90FF", alpha=0.3)

plt.plot(wl_TLC, Tb_mean_TLC, label="True Low Cloud (Mean)", color="#00FA9A")
plt.fill_between(wl_TLC, Tb_min_TLC, Tb_max_TLC, color="#00FA9A", alpha=0.3)

plt.xlabel("Wavelength (um)")
plt.ylabel("Brightness Temperature (K)")
plt.xlim((3,12))
plt.ylim((180,300))
plt.title(plot_title)
plt.legend()
plt.tight_layout()
plt.savefig(f"plots/{fig_name}", dpi=200)

fig, ax = plt.subplots(figsize=(10, 5))
plt.close()

fig, ax = plt.subplots(figsize=(10, 5))

wl = wl_FLC
Tb_diff = Tb_mean_TLC - Tb_mean_FLC

plt.axhline(y=0, color="blue", linestyle="-", linewidth=1, zorder=0)
ax.plot(wl, Tb_diff, 
        color="white", 
        linewidth=0.5, 
        label=f"True Low Cloud - False Low Cloud", 
        zorder=3)
ax.set_xlim((3,12))
ax.set_ylim((-10,10))

ax.set_xlabel("Wavelength (μm)")
ax.set_ylabel("Brightness Temperature Difference (K)")
ax.set_title(f"Average {plot_title}")
ax.legend()

plt.savefig(f"plots/{fig_name}_diff.png", dpi=200, bbox_inches='tight')
plt.close()