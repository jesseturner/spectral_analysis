from modules_gxs_sim import gxs_utils as gxs

gxs_filepath = "data/gxs_sim/Tb_gxs2402bae_g26_d20190922_t211500_e211500.nc"

ds = gxs.open_gxs_data(gxs_filepath)
print(ds)

for i in range(0, 2401, 120):
    gxs.plot_Tb_CLD(ds, channel_index=i, plot_title="GXS Cloudy Tb (Sim data)", 
                    plot_dir="plots", plot_name="example_gxs")