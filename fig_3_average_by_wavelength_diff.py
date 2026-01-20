# Plot the average of the spectra across the CrIS domain 
# and the by-wavelength difference between the average spectra for FLC and TLC. 

from modules_cris import cris_utils as c_utils
import matplotlib.pyplot as plt
import numpy as np
from fig_1_cris_modtran_overlay import file_path
from fig_2_training_set import FLC_points, TLC_points

c_utils.set_plots_dark()

fig_name = "fig3_source_CrIS_average"
plot_title = "IR Spectra to Distinguish Low Clouds in CrIS"

def get_category_stats(ds_func, points):
    """
    Given a list of lat/lon points, return the wavelengths, average Tb, and variance of Tb.
    """
    all_Tb = []
    ds = ds_func(file_path)

    for lat, lon in points:
        
        ds_target = c_utils.isolate_target_point(ds, target_lat=lat, target_lon=lon)
        df_cris = c_utils.get_brightness_temperature(ds_target)
        wl = df_cris["Wavelength (um)"]
        Tb = df_cris["Brightness Temperature (K)"].values
        all_Tb.append(Tb)

    ds.close()
    all_Tb = np.array(all_Tb)
    Tb_mean = np.mean(all_Tb, axis=0)
    Tb_min = np.min(all_Tb, axis=0)
    Tb_max = np.max(all_Tb, axis=0)
    Tb_var = np.var(all_Tb, axis=0)

    return wl, Tb_mean, Tb_min, Tb_max, Tb_var

# Compute stats for each category
wl_FLC, Tb_mean_FLC, Tb_min_FLC, Tb_max_FLC, Tb_var_FLC = get_category_stats(c_utils.open_cris_data, FLC_points)
wl_TLC, Tb_mean_TLC, Tb_min_TLC, Tb_max_TLC, Tb_var_TLC = get_category_stats(c_utils.open_cris_data, TLC_points)

# Plotting
plt.figure(figsize=(10,5))
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
plt.close()

#--- Plotting the difference in averages
fig, ax = plt.subplots(figsize=(10, 5))

wl = wl_FLC
Tb_diff = Tb_mean_TLC - Tb_mean_FLC

plt.axhline(y=0, color="blue", linestyle="-", linewidth=1, zorder=0)

#--- Only CrIS regions
mask = (
    ((wl >= 3.92) & (wl <= 4.64)) |
    ((wl >= 5.71) & (wl <= 8.26)) |
    ((wl >= 9.13) & (wl <= 15.4))
)
y_plot = np.where(mask, Tb_diff, np.nan)

ax.plot(wl, y_plot, 
        color="white", 
        linewidth=0.5, 
        label=f"True Low Cloud - False Low Cloud", 
        zorder=3)
ax.set_xlim((3,16))
ax.set_ylim((-10,10))

ax.set_xlabel("Wavelength (μm)")
ax.set_ylabel("Brightness Temperature Difference (K)")
ax.set_title(f"Average {plot_title}")
ax.legend()

plt.savefig(f"plots/{fig_name}_diff.png", dpi=200, bbox_inches='tight')
plt.close()

