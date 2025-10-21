from VIIRS_utils import viirs_utils as v_utils
import os

#--- Plot the VIIRS BTD

viirs_dir = "/local/home/jturner/FLC_data/VIIRS_data/"
viirs_file = "GMTCO-SVM12-SVM13-SVM15_j01_d20250312_t0639527_e0645327_b37894_c20251017052332443046_oebc_ops.h5"
file_path = os.path.join(viirs_dir, viirs_file)

v_utils.print_viirs_file_metadata(file_path)
v_utils.print_viirs_file_attrs(file_path, dataset="Data_Products/VIIRS-M13-SDR/VIIRS-M13-SDR_Gran_0")

da_sw = v_utils.open_viirs_brightness_temp(file_path, "M13")
da_lw = v_utils.open_viirs_brightness_temp(file_path, "M15")

da_btd = da_lw - da_sw

description = f"{viirs_file.split("_")[1]} {viirs_file.split("_")[2]} {viirs_file.split("_")[3]}"
save_name = f"btd_{description.replace(" ", "_")}"
plot_title = f"VIIRS M15 - M13 (10.76 μm - 4.05 μm) BTD \n {description}"
v_utils.plot_viirs_data(da_btd, "VIIRS_plot", save_name, plot_title, extent=[-73, -57, 33, 46], pin_coords=(40, -67.75))


#--- Plot the VIIRS Day/Night Band

# dnb_file = "GDNBO-SVDNB_j01_d20250312_t0639527_e0645327_b37894_c20250912025655090196_oebc_ops.h5"
# dnb_file_path = os.path.join("/local/home/jturner/FLC_data/DNB_data", dnb_file)

# description = f"{dnb_file.split("_")[1]} {dnb_file.split("_")[2]} {dnb_file.split("_")[3]}"
# save_name = f"dnb_{description.replace(" ", "_")}"
# plot_title = f"VIIRS Day/Night Band \n {description}"

# da = v_utils.open_dnb_radiance(dnb_file_path)

# v_utils.plot_dnb_radiance(da, "VIIRS_plot", save_name, plot_title, extent=[-73, -57, 33, 46], pin_coords=(40, -67.75))


#--- Plot the VIIRS spectral response functions

# srf_file = "VIIRS_spectral_response_functions/NPP_VIIRS_NG_RSR_M12_FAKE.dat"
# v_utils.plot_viirs_srf(srf_file)