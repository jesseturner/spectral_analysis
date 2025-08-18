from spectral_utils import modtran_utils as m_utils

df1 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/false_low_clouds.tp7")

df2 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/low_clouds.tp7")

df3 = m_utils.open_tp7_file("/home/jturner/MODTRAN6/no_low_clouds.tp7")

m_utils.plot_bt_dual(df1=df1, df2=df2, df1_name="moist air", df2_name="true low clouds",
    fig_dir="MODTRAN_plot", fig_name="scene_comparison_1")

m_utils.plot_bt_dual(df1=df1, df2=df3, df1_name="moist air", df2_name="no low clouds",
    fig_dir="MODTRAN_plot", fig_name="scene_comparison_2")

m_utils.plot_bt_dual_freq_range(df1, df2=df2, df1_name="moist air", df2_name="true low clouds", 
    fig_dir='MODTRAN_plot', fig_name='scene_comparison_1_abi_band_07',
    freq_range=[833, 952])

m_utils.plot_bt_dual_freq_range(df1, df2=df2, df1_name="moist air", df2_name="true low clouds", 
    fig_dir='MODTRAN_plot', fig_name='scene_comparison_1_abi_band_14',
    freq_range=[2430, 2555])

m_utils.plot_btd_freq_range(df1, df_name='moist air', 
    fig_dir='MODTRAN_plot', fig_name='btd_moist_air',
    freq_range1=[833, 952], freq_range2=[2430, 2555])

m_utils.plot_btd_freq_range(df2, df_name='true low cloud', 
    fig_dir='MODTRAN_plot', fig_name='btd_true_low_cloud',
    freq_range1=[833, 952], freq_range2=[2430, 2555])


print(df1)

