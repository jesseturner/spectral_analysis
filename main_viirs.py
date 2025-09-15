from viirs_utils import viirs_utils as v_utils
import os

viirs_dir = "/local/home/jturner/FLC_data/VIIRS_data/"
viirs_file = "GMTCO-SVM12-SVM15_j01_d20250312_t0315027_e0320427_b37892_c20250912033551563103_oebc_ops.h5"
file_path = os.path.join(viirs_dir, viirs_file)

v_utils.print_viirs_file_metadata(file_path)