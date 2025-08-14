from spectral_utils import spectral_utils as s_utils

df = s_utils.open_tp7_file("/home/jturner/MODTRAN6/false_low_clouds.tp7")

df = s_utils.plot_brightness_temperature(df, "MODTRAN_plot", "false_low_clouds")
print(df)