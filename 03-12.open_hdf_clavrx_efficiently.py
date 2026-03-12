from pyhdf.SD import SD, SDC
import numpy as np

print("Clavrx files are in HDF4 format...")
filepath_list = ['/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_npp_d20260306_t0422348_e0423589_b74382.level2.hdf', 
                 '/mnt/overcastnas1/LEO_clavrx/JPSS_global/2026065/clavrx_npp_d20260306_t0424002_e0425243_b74382.level2.hdf']

all_dnb_data = []
all_cloud_mask_data = []

for filepath in filepath_list:
    file = SD(filepath, SDC.READ)

    dnb_data = file.select('refl_lunar_dnb_nom')
    cloud_mask_data = file.select('cloud_mask')

    print(f"\nFile: {filepath}")
    print(dnb_data.info())
    print(cloud_mask_data.info())

    # Read data into NumPy arrays
    dnb_array = dnb_data[:]
    cloud_mask_array = cloud_mask_data[:]

    # Store arrays in the lists
    all_dnb_data.append(dnb_array)
    all_cloud_mask_data.append(cloud_mask_array)

    # Close the file
    file.end()

# Example: stack all DNB data into one 3D array if shapes are consistent
all_dnb_stack = np.stack(all_dnb_data)
print(f"\nStacked DNB data shape: {all_dnb_stack.shape}")
print("Might need to concatenate these files, investigate further...")

# file = SD(filepath, SDC.READ)

# dnb_data = file.select('refl_lunar_dnb_nom')
# cloud_mask_data = file.select('cloud_mask')

# print(dnb_data.info())

# # Read data into a NumPy array
# data = dnb_data[:]
# print(data.shape)
