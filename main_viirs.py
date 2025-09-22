from VIIRS_utils import viirs_utils as v_utils
import os

viirs_dir = "/local/home/jturner/FLC_data/VIIRS_data/"
viirs_file = "GMTCO-SVM12-SVM15_j02_d20250312_t0554219_e0600007_b12101_c20250912030557371905_oebc_ops.h5"
file_path = os.path.join(viirs_dir, viirs_file)

# v_utils.print_viirs_file_metadata(file_path)
# v_utils.print_viirs_file_attrs(file_path)

da_m12 = v_utils.open_viirs_brightness_temp(file_path, "M12")
da_m15 = v_utils.open_viirs_brightness_temp(file_path, "M15")

da_btd = da_m15 - da_m12
print(da_btd)

save_name = f"btd_{viirs_file.split("_")[1]}_{viirs_file.split("_")[2]}_{viirs_file.split("_")[3]}"
plot_title = "VIIRS M15 - M12 (10.76 μm - 3.7 μm) BTD"
v_utils.plot_viirs_data(da_btd, "VIIRS_plot", save_name, plot_title)