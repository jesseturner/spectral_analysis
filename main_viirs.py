from VIIRS_utils import viirs_utils as v_utils
import os

viirs_dir = "/local/home/jturner/FLC_data/VIIRS_data/"
viirs_file = "GMTCO-SVM12-SVM15_j01_d20250312_t0320440_e0326240_b37892_c20250912032031776593_oebc_ops.h5"
file_path = os.path.join(viirs_dir, viirs_file)

v_utils.print_viirs_file_metadata(file_path)
v_utils.print_viirs_file_attrs(file_path)

da = v_utils.open_viirs_file(file_path)
print(da)
da = v_utils.replace_viirs_fill_values(da)
print(da)

v_utils.plot_viirs_data(da)