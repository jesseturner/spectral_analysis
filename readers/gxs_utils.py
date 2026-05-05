import xarray as xr

def open_gxs_data(filepath):
    '''
    Dimensions: 
        number_channels: 2402,
        num_scan_line: 615, (y)
        num_fov_per_scan_line: 1201, (x)
        number_layers: 137 (only for profile retrievals)
    '''
    ds = xr.open_dataset(filepath)
    return ds

def convert_freq_to_index(channel_freq_list):

    #--- Issues with getting the actual number_channels coordinate, estimating instead
    channel_index_list = []

    for freq_cm in channel_freq_list:
        index = int(round(233.66 * (10000 / freq_cm - 4.44)))
        channel_index_list.append(index)
        
    return channel_index_list