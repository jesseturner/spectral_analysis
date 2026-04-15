#--- Opening CLAVR-x files with pyhdf, plotting with imshow

from pyhdf.SD import SD, SDC
import numpy as np
import matplotlib.pyplot as plt
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
    
    print_hdf_file_info(example_file=filepath_list[0], dataset='cloud_mask')
    print_hdf_file_info(example_file=filepath_list[0], dataset='refl_lunar_dnb_nom')

    #--- Add logic only get nighttime data with moonlight
    filepath_list = filepath_list[30:42]
    all_cloud_mask_data = opening_clavrx(filepath_list, dataset='cloud_mask')
    all_dnb_data = opening_clavrx(filepath_list, dataset='refl_lunar_dnb_nom')

    all_cm_combined = np.concatenate(all_cloud_mask_data, axis=0)
    all_dnb_combined = np.concatenate(all_dnb_data, axis=0)
    print(f"Unique values: {np.unique(all_cm_combined)}")
    print(f"Unique values: {np.unique(all_dnb_combined)}")

    plot_clavrx_cloud_mask(all_cm_combined)
    plot_clavrx_dnb(all_dnb_combined)

    return

#---------------

def print_hdf_file_info(example_file, dataset):
    '''
    :param example_file:
    :param dataset: 'cloud_mask', 'refl_lunar_dnb_nom'
    '''
    file = SD(example_file, SDC.READ)
    print(f"--- {dataset} dataset info ---")
    sample = file.select(dataset)
    print(f"Name: {sample.info()[0]}")
    print(f"Dimensions: {sample.info()[1]}")
    print(f"Dataset shape: {sample.info()[2]}")
    print(f"Data type code: {sample.info()[3]}")
    print(f"Attributes: {sample.info()[4]}")

    return

def opening_clavrx(filepath_list, dataset):
    '''
    :param filepath_list: ['/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_j01_d20260306_t0401141_e0402386_b42986.level2.hdf', ...]
    :param dataset: 'cloud_mask', 'refl_lunar_dnb_nom'
    '''
    print("Opening and stacking files in list...")
    data_array = []
    for filepath in tqdm(filepath_list, desc="Reading HDF files"):
        file = SD(filepath, SDC.READ)

        dataset_data = file.select(dataset)
        dataset_array = dataset_data[:]
        data_array.append(dataset_array)

        file.end()

    return data_array

def plot_clavrx_cloud_mask(data_array):
    fig, ax = plt.subplots(1, figsize=(12,12))
    img = ax.imshow(data_array, cmap='gray', vmin=0, vmax=3)
    ax.set_title("CLAVR-x Cloud Mask")
    plt.axis('off')
    plt.savefig(f"plots/imshow_cloud_mask.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return 

def plot_clavrx_dnb(data_array):
    fig, ax = plt.subplots(1, figsize=(12,12))
    img = ax.imshow(data_array, cmap='gray', vmin=-32000, vmax=24000)
    ax.set_title("CLAVR-x Day/Night Band Radiance")
    plt.axis('off')
    plt.savefig(f"plots/imshow_dnb.png",
                dpi=200, bbox_inches='tight')
    plt.close()

    return 

#---------------

if __name__ == "__main__":
    main()