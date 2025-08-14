from spectral_utils import spectral_utils as s_utils

df1 = s_utils.open_tp7_file("/home/jturner/MODTRAN6/false_low_clouds.tp7")

df2 = s_utils.open_tp7_file("/home/jturner/MODTRAN6/low_clouds.tp7")

df3 = s_utils.open_tp7_file("/home/jturner/MODTRAN6/no_low_clouds.tp7")

s_utils.plot_brightness_temperature(df1=df1, df2=df2, fig_dir="MODTRAN_plot", fig_name="scene_comparison_1",
    df1_name="false low clouds", df2_name="true low clouds")

s_utils.plot_brightness_temperature(df1=df1, df2=df3, fig_dir="MODTRAN_plot", fig_name="scene_comparison_2",
    df1_name="false low clouds", df2_name="no low clouds")

print(df1)