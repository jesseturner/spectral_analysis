from modules_gxs_sim import gxs_utils as gxs

gxs_filepath = "data/gxs_sim/Tb_gxs2402bae_g26_d20190922_t211500_e211500.nc"

ds = gxs.open_gxs_data(gxs_filepath)
# print(ds)

#--- Save image for each wavenumber
# channel_index_list = range(0, 2401, 120)
# print(channel_index_list)

# for i in channel_index_list:
#     gxs.plot_Tb_CLD(ds, channel_index=i, plot_title="GXS Cloudy Tb (Sim data)", 
#                    plot_dir="plots", plot_name="example_gxs")

#--- Create 3D stack image
#gxs.plot_Tb_3d(ds, channel_index_list, plot_dir="plots", plot_name="ex_stack")

#--- Create 3D stack image for ABI
# channel_wl_abi = [0.47, 0.64, 0.86, 1.37, 1.6, 2.2, 3.9, 6.2, 6.9, 7.3, 8.4, 9.6, 10.3, 11.2, 12.3, 13.3]
# channel_freq_abi = [10_000 / x for x in channel_wl_abi]
# print(channel_freq_abi)

# channel_index_list = gxs.convert_freq_to_index(channel_freq_abi)
# print(channel_index_list)
# gxs.plot_block(ds, channel_index_list, custom_cmap_name="blue", plot_dir="plots", plot_name="stack_abi")

#--- Create 3D stack image for full GXS
channel_index_list = range(100, 2201, 100)
gxs.plot_block(ds, channel_index_list, custom_cmap_name="blue", plot_dir="plots", plot_name="stack_gxs")

#--- Coarsen spatial resolution to approximate CrIS
# channel_index_list = range(100, 2201, 10)
# ds = ds[['Tb_CLR']]
# ds_clean = ds.where(ds != -19998)
# ds_coarse = ds_clean.coarsen(
#     num_scan_line=40,
#     num_fov_per_scan_line=40,
#     boundary="trim"
# ).mean(skipna=True)
# ds_coarse = ds_coarse.compute()
# gxs.plot_block(ds_coarse, channel_index_list, custom_cmap_name="blue", plot_dir="plots", plot_name="stack_cris_sim")