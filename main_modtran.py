from spectral_utils import modtran_utils as m_utils

df1 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/false_low_clouds.tp7")

df2 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/low_clouds.tp7")

df3 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/no_low_clouds.tp7")

#range1=[833, 952], range2=[2430, 2555]

m_utils.plot_bt_dual(df1=df1, df2=df2, df1_name="false low clouds", df2_name="true low clouds",
    fig_dir="MODTRAN_plot", fig_name="scene_comparison_1")

m_utils.plot_bt_dual(df1=df1, df2=df3, df1_name="false low clouds", df2_name="no low clouds",
    fig_dir="MODTRAN_plot", fig_name="scene_comparison_2")

print(df1)

