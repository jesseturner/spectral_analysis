import xarray as xr
import matplotlib.pyplot as plt
import os
import numpy as np
import matplotlib.colors as mcolors

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

def _plt_save(fig_dir, fig_name):
    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()
    return

def plot_Tb_CLD(ds, channel_index, plot_title, plot_dir, plot_name):
    '''
    Plotting Cloudy Brightness Temperature. 
    
    :param channel_index: between 0 and 2402
    :param freq: between 2252.26 and 680.09 cm-1
    :param ds: from open_gxs_data()
    '''

    freq = ds['freq'][channel_index].values.item()
    print(f"Channel index {channel_index}: Frequency of {round(freq,2)} cm-1 ({round(10_000/freq, 2)} um)")

    img = ds['Tb_CLR'][channel_index, :, :]
    img = img.where(img != -19998) #--- Missing values to NaNs

    x = img['num_fov_per_scan_line'].values
    y = img['num_scan_line'].values
    z = img.values

    fig, ax = plt.subplots(figsize=(10, 6))

    pcm = ax.pcolormesh(
        x, y, z,
        cmap='Greys',
        shading='nearest'
    )

    clb = fig.colorbar(pcm, shrink=0.6, pad=0.02, ax=ax)
    clb.set_label('Brightness Temperature (K)', fontsize=15)
    clb.ax.tick_params(labelsize=15)
    ax.invert_yaxis()

    ax.set_xlabel('FOV per scan line', fontsize=15)
    ax.set_ylabel('Scan line', fontsize=15)
    ax.set_title(f'{plot_title}\n {round(freq,2)} cm$^{-1}$ ({round(10_000/freq, 2)} µm)')

    _plt_save(plot_dir, f'{plot_name}_{round(freq)}')
    return


def plot_block(ds, channel_list, custom_cmap_name, plot_dir, plot_name):

    # Filter to frequencies
    img_3d = ds['Tb_CLR'].sel(number_channels=channel_list)

    # Remove NaN values
    img_3d = img_3d.where(img_3d != -19998)

    # Crop to a square
    ny = img_3d.sizes['num_scan_line']
    nx = img_3d.sizes['num_fov_per_scan_line']
    side = min(nx, ny)
    x0 = (nx - side) // 2
    y0 = (ny - side) // 2

    img_3d = img_3d.isel(
        num_fov_per_scan_line=slice(x0, x0 + side),
        num_scan_line=slice(y0, y0 + side)
    )

    # Get the coordinates
    x = img_3d['num_fov_per_scan_line'].values
    y = img_3d['num_scan_line'].values

    X, Y = np.meshgrid(x, y)
    
    fig = plt.figure(figsize=(8, 6), facecolor='black')
    ax = fig.add_subplot(111, projection='3d', facecolor='black')

    # Optional: make background clean
    ax.xaxis.pane.fill = False
    ax.yaxis.pane.fill = False
    ax.zaxis.pane.fill = False
    ax.grid(False)

    # Consistent color scaling
    finite_vals = img_3d.values[np.isfinite(img_3d.values)]
    vmin = finite_vals.min() # Adjustment to get colors to line up nicely
    vmax = finite_vals.max()
    cmap, norm = custom_cmap_selection(custom_cmap_name)

    # Plot stacked slices
    for img, ch in zip(img_3d, channel_list):
        img_np = img.values

        ax.contourf(
            X, Y, img_np,
            levels=20,
            zdir='z',
            offset=ch,
            cmap=cmap,
            vmin=vmin,
            vmax=vmax
        )

    # Axes labeling & limits
    ax.set_xlabel('FOV per scan line')
    ax.set_ylabel('Scan line')
    ax.set_zlabel('ABI Channel', color="black")
    
    ax.invert_yaxis()
    ax.set_zlim(np.min(channel_list), np.max(channel_list))

    # Viewing angle
    ax.view_init(elev=25, azim=-60)

    _plt_save(plot_dir, plot_name)

    return

def convert_freq_to_index(channel_freq_list):

    #--- Issues with getting the actual number_channels coordinate, estimating instead
    channel_index_list = []

    for freq_cm in channel_freq_list:
        index = int(round(233.66 * (10000 / freq_cm - 4.44)))
        channel_index_list.append(index)
        
    return channel_index_list

def custom_cmap_selection(custom_cmap_name):
    
    if custom_cmap_name == "green":
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom_cmap",
            [(0, "#06BA63"), (0.5, "black"), (1, "white")]
        )
        norm = mcolors.TwoSlopeNorm(vmin=-6, vcenter=0, vmax=1.5)

    if custom_cmap_name == "blue":
        cmap = mcolors.LinearSegmentedColormap.from_list(
            "custom_cmap",
            [(0, "#A9A9A9"), (0.5, "white"), (1, "#1167b1")]
        )
        norm = mcolors.TwoSlopeNorm(vmin=-3, vcenter=0, vmax=3)
    
    return cmap, norm