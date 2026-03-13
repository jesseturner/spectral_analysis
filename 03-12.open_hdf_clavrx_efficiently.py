from pyhdf.SD import SD, SDC
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.colors import ListedColormap
from matplotlib.colors import BoundaryNorm
import cartopy.crs as ccrs
from datetime import datetime
import os
import glob
from tqdm import tqdm

def main():

    clavrx_dir = "/mnt/overcastnas1/LEO_clavrx/JPSS_global/"
    clavrx_date_str = "2026030604"  # YYYYMMDDHH
    clavrx_dt = datetime.strptime(clavrx_date_str, "%Y%m%d%H")
    clavrx_julian_str = clavrx_dt.strftime("%Y%j")
    hour_str = clavrx_dt.strftime("%H")
    clavrx_pattern = os.path.join(clavrx_dir, f"{clavrx_julian_str}/*t{hour_str}*.hdf")
    filepath_list = glob.glob(clavrx_pattern)
    filepath_list.sort()

    print("Clavrx files are in HDF4 format, using pyhdf...")
    print(f"{len(filepath_list)} files found for {clavrx_date_str[0:4]}-{clavrx_date_str[4:6]}-{clavrx_date_str[6:8]} hour {clavrx_date_str[8:10]}")
    #filepath_list = ['/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_npp_d20260306_t0422348_e0423589_b74382.level2.hdf', 
    #                '/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_npp_d20260306_t0424002_e0425243_b74382.level2.hdf']

    file = SD(filepath_list[0], SDC.READ)
    print("--- DNB dataset info ---")
    dnb_sample = file.select('refl_lunar_dnb_nom')
    print(f"Name: {dnb_sample.info()[0]}")
    print(f"Dimensions: {dnb_sample.info()[1]}")
    print(f"Dataset shape: {dnb_sample.info()[2]}")
    print(f"Data type code: {dnb_sample.info()[3]}")
    print(f"Attributes: {dnb_sample.info()[4]}")

    print("--- Cloud mask dataset info ---")
    cloud_mask_sample = file.select('cloud_mask')
    print(f"Name: {cloud_mask_sample.info()[0]}")
    print(f"Dimensions: {cloud_mask_sample.info()[1]}")
    print(f"Dataset shape: {cloud_mask_sample.info()[2]}")
    print(f"Data type code: {cloud_mask_sample.info()[3]}")
    print(f"Attributes: {cloud_mask_sample.info()[4]}")

    print("Opening and stacking files in list...")
    all_dnb_data = []
    all_cloud_mask_data = []
    filepath_list = filepath_list[:12]
    for filepath in tqdm(filepath_list, desc="Reading HDF files"):
        file = SD(filepath, SDC.READ)

        dnb_data = file.select('refl_lunar_dnb_nom')
        cloud_mask_data = file.select('cloud_mask')

        # Read data into NumPy arrays
        dnb_array = dnb_data[:]
        cloud_mask_array = cloud_mask_data[:]
        all_dnb_data.append(dnb_array)
        all_cloud_mask_data.append(cloud_mask_array)

        file.end()

    all_cm_combined = np.concatenate(all_cloud_mask_data, axis=0)
    print(f"Concatenated cloud mask data shape: {all_cm_combined.shape}")
    print(f"Unique values: {np.unique(all_cm_combined)}")

    fig, ax = plt.subplots(1, figsize=(12,12))
    ax.imshow(all_cm_combined, cmap='gray', vmin=0, vmax=3)
    ax.set_title("Concatenated granules")
    plt.savefig(f"plots/hdf_demo_cloud_mask_concat.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return

#---------------

if __name__ == "__main__":
    main()