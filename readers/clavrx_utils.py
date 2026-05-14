from pyhdf.SD import SD, SDC
from tqdm import tqdm
import re
import numpy as np
from datetime import datetime

def opening_clavrx(filepath_list, dataset):
    '''
    :param filepath_list: ['/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_j01_d20260306_t0401141_e0402386_b42986.level2.hdf', ...]
    :param dataset: 'cloud_mask', 'refl_lunar_dnb_nom'
    '''
    print(f"Opening and stacking {dataset} data from files in list...")
    data_array = []
    for filepath in tqdm(filepath_list, desc="Reading HDF files"):
        try:
            file = SD(filepath, SDC.READ)

            dataset_data = file.select(dataset)
            dataset_array = dataset_data[:]
            data_array.append(dataset_array)

            file.end()
        except ValueError as e:
            print("Error:", e)
            #--- Add 768 (x length of each dataset)
            pad = np.full((768, 3200), np.nan)
            data_array.append(pad)
        except Exception as e:
            print("Error:", e)
            pad = np.full((768, 3200), np.nan)
            data_array.append(pad)

    data_array_combined = np.concatenate(data_array, axis=0)

    return data_array_combined

def get_datetime(file):
    match = re.search(r"d(\d{8})_t(\d{7})", file)
    date_str, time_str = match.groups()
    dt = datetime.strptime(date_str + time_str[:6], "%Y%m%d%H%M%S")
    return dt