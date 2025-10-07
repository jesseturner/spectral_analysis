from VIIRS_utils import viirs_utils as v_utils
import os

viirs_dir = "/local/home/jturner/FLC_data/VIIRS_data/"
viirs_file = "GMTCO-SVM12-SVM15_j01_d20250312_t0639527_e0645327_b37894_c20250912024232561810_oebc_ops.h5"
file_path = os.path.join(viirs_dir, viirs_file)

# v_utils.print_viirs_file_metadata(file_path)
# v_utils.print_viirs_file_attrs(file_path, dataset="Data_Products/VIIRS-M12-SDR/VIIRS-M12-SDR_Gran_0")

# da_m12 = v_utils.open_viirs_brightness_temp(file_path, "M12")
# da_m15 = v_utils.open_viirs_brightness_temp(file_path, "M15")

# da_btd = da_m15 - da_m12
# print(da_btd)

# description = f"{viirs_file.split("_")[1]} {viirs_file.split("_")[2]} {viirs_file.split("_")[3]}"
# save_name = f"btd_{description.replace(" ", "_")}"
# plot_title = f"VIIRS M15 - M12 (10.76 μm - 3.7 μm) BTD \n {description}"
# v_utils.plot_viirs_data(da_btd, "VIIRS_plot", save_name, plot_title, extent=[-73, -57, 33, 46])

srf_file = "VIIRS_spectral_response_functions/NPP_VIIRS_NG_RSR_I4_filtered_Oct2011f_BA.dat"
v_utils.plot_viirs_srf(srf_file)