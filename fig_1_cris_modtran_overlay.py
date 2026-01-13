from modules_cris import cris_utils as c_utils
from modules_modtran import modtran_utils as m_utils
import os
import matplotlib.pyplot as plt

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
cris_target_lat_FLC = 40
cris_target_lon_FLC = -67.75
cris_target_lat_TLC = 43
cris_target_lon_TLC = -66.22
fig_name = "fig1_source_CrIS"
plot_title = f"IR Spectra to Distiguish Low Clouds in CrIS"

ds = c_utils.open_cris_data(file_path)
ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat_TLC, target_lon=cris_target_lon_TLC)
df_cris_TLC = c_utils.get_brightness_temperature(ds)
wl_1, Tb_1 = df_cris_TLC["Wavelength (um)"], df_cris_TLC["Brightness Temperature (K)"]
label_1 = "True Low Cloud"
color_1 = "#00FA9A"

ds = c_utils.open_cris_data(file_path)
ds = c_utils.isolate_target_point(ds, target_lat=cris_target_lat_FLC, target_lon=cris_target_lon_FLC)
df_cris_FLC = c_utils.get_brightness_temperature(ds)
wl_2, Tb_2 = df_cris_FLC["Wavelength (um)"], df_cris_FLC["Brightness Temperature (K)"]
label_2 = "False Low Cloud"
color_2 = "#1E90FF"

#====== ====== ======

#--- Plot brightness temperature overlay

fig, ax = plt.subplots(figsize=(10, 5))
ax.set_facecolor('black')

ax.plot(wl_1, Tb_1, 
        color=color_1, 
        linewidth=0.5, 
        label=label_1)
ax.plot(wl_2, Tb_2, 
        color=color_2, 
        linewidth=0.5, 
        label=label_2)
ax.set_xlim((3,12))
ax.set_ylim((180,300))

ax.set_xlabel("Wavelength (μm)")
ax.set_ylabel("Brightness Temperature (K)")
ax.set_title(plot_title)
ax.legend()

plt.savefig(f"plots/{fig_name}.png", dpi=200, bbox_inches='tight')
plt.close()

#--- plot brightness temperature difference

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