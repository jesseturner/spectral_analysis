from VIIRS_utils import viirs_utils as v_utils
import os

dnb_dir = "/local/home/jturner/FLC_data/DNB_data/" 
dnb_file = "GDNBO-SVDNB_j01_d20250312_t0639527_e0645327_b37894_c20250912025655090196_oebc_ops.h5"
file_path = os.path.join(dnb_dir, dnb_file)

v_utils.print_viirs_file_metadata(file_path)
v_utils.print_viirs_file_attrs(file_path, dataset="Data_Products/VIIRS-DNB-GEO/VIIRS-DNB-GEO_Gran_0")

da = v_utils.open_dnb_radiance(file_path)
print(da)

save_name = f"dnb_{dnb_file.split("_")[1]}_{dnb_file.split("_")[2]}_{dnb_file.split("_")[3]}"
plot_title = "VIIRS Day/Night Band"

#--- This currently seems to have fill values or scaling, or both
v_utils.plot_dnb_radiance(da, "VIIRS_plot", save_name, plot_title)
