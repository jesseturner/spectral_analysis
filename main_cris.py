from CrIS_utils import cris_utils as c_utils
import os

# c_utils.download_cris_data(date_start="2025-03-12", date_end="2025-03-12", lon_west=-73, lat_south=33, lon_east=-57, lat_north=46)

cris_dir = "CrIS_data/"
cris_file = "SNDR.J1.CRIS.20250312T0642.m06.g068.L1B.std.v03_08.G.250312132403.nc"
file_path = os.path.join(cris_dir, cris_file)

ds = c_utils.open_cris_data(file_path)

ds = c_utils.isolate_target_point(ds, target_lat=35.75, target_lon=-69.25)
print(ds)

df = c_utils.get_brightness_temperature(ds)
print(df)

save_name = f"{cris_file.split(".")[1]}_{cris_file.split(".")[3]}"
plot_title = f"CrIS 2025-03-12 (35.69, -69.21) \n j01 d20250312 t0642"

c_utils.plot_brightness_temperature(df, fig_dir="CrIS_plot", fig_name=save_name, fig_title=plot_title)

c_utils.plot_btd_freq_range(df,
    fig_dir='CrIS_plot', fig_name=f'btd_{save_name}', fig_title=plot_title,
    freq_range1=[833, 952], freq_range2=[2430, 2555])

