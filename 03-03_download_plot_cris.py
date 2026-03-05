import xarray as xr
import h5py
import earthaccess
import os
import matplotlib.pyplot as plt
import cartopy.crs as ccrs

def main():
    # aws_sdr_path = "data/cris/SCRIF_j01_d20260303_t1648349_e1649047_b42951_c20260303172817999000_oebc_ops.h5"
    # aws_geo_path = "data/cris/GCRSO_j01_d20260303_t1648349_e1649047_b42951_c20260303172818357000_oebc_ops.h5"
    # open_aws_cris(aws_sdr_path, aws_geo_path)

    ea_cris_files = download_cris_data("2026-03-05", "2026-03-06", cris_dir="data/cris/from_earthaccess")

    # cris_path = "data/cris/from_earthaccess/SNDR.J1.CRIS.20260302T0012.m06.g003.L1B.std.v03_08.G.260302072655.nc"
    # ds = xr.open_dataset(cris_path)
    # ds_sel = ds.sel(atrack=slice(0, 18), xtrack=slice(0, 18), fov=0, wnum_lw=648.75)
    # print(ds_sel['lat'])
    # print(ds_sel['rad_lw'])

    # plot_cris_spatial(ds_sel['rad_lw'], ds_sel['lat'], ds_sel['lon'], fig_dir="plots", fig_name="cris_rad", fig_title="CrIS radiance")

    return

#---------------

def download_cris_data(date_start, date_end, lon_west=None, lat_south=None, lon_east=None, lat_north=None, cris_dir="CrIS_data"):
    """
    date_start and date_end format: "2025-06-25"
    coordinate format: -105.31
    """
    #--- Earthaccess docs: https://earthaccess.readthedocs.io/en/latest/quick-start/
    auth = earthaccess.login()

    print("Currently only searches NOAA-20")

    #--- Search for the granule by DOI
    #------ Suomi NPP Normal Spectral Resolution 10.5067/OZZPDWENP2NC
    #------ Suomi NPP Full Spectral Resolution 10.5067/ZCRSHBM5HB23
    #------ NOAA-20 / JPSS-1 Full Spectral Resolution 10.5067/LVEKYTNSRNKP
    #------ NOAA-21 / JPSS-2 Full Spectral Resolution 
    results = earthaccess.search_data(
        doi='10.5067/LVEKYTNSRNKP',
        temporal=(date_start, date_end), 
        # bounding_box=(lon_west, lat_south, lon_east, lat_north)
    )
    os.makedirs(f"{cris_dir}", exist_ok=True)
    files = earthaccess.download(results, cris_dir)
    print(f"{len(files)} downloaded.")
    return files

def plot_cris_spatial(ds_sel, ds_lat, ds_lon, fig_dir, fig_name, fig_title):
    """
    Spatial plot of CrIS brightness temperature for a certain band. Band can either be CrIS narrow band, or a simulated broad band from a SRF. 

    ds_sel : from get_cris_band_Tb(), BTD simply uses ds_sel1 - ds_sel2
    extent : [west, east, south, north]
    pin_coords : (lat, lon)
    """

    projection=ccrs.PlateCarree(central_longitude=0)
    fig,ax=plt.subplots(1, figsize=(12,12),subplot_kw={'projection': projection})

    c = ax.pcolormesh(ds_lon, ds_lat, ds_sel, cmap='Greys', shading='auto')

    clb = plt.colorbar(c, shrink=0.6, pad=0.02, ax=ax)
    clb.ax.tick_params(labelsize=15)
    clb.set_label('(K)', fontsize=15)

    ax.coastlines(resolution='50m', color='white', linewidth=2)
    # ax.add_feature(cfeature.STATES, edgecolor='black', linewidth=1, zorder=6)

    ax.set_title(fig_title, fontsize=20, pad=10)

    os.makedirs(f"{fig_dir}", exist_ok=True)
    plt.savefig(f"{fig_dir}/{fig_name}.png", dpi=200, bbox_inches='tight')
    plt.close()

    return

def open_aws_cris(sdr_path, geo_path):

    with h5py.File(sdr_path, "r") as f:
        rad = f["All_Data/CrIS-FS-SDR_All/ES_RealLW"][:]

    with h5py.File(geo_path, "r") as f:
        lat = f["All_Data/CrIS-SDR-GEO_All/Latitude"][:]
        lon = f["All_Data/CrIS-SDR-GEO_All/Longitude"][:]
        sat_zen = f["All_Data/CrIS-SDR-GEO_All/SatelliteZenithAngle"][:]
        sol_zen = f["All_Data/CrIS-SDR-GEO_All/SolarZenithAngle"][:]
        time = f["All_Data/CrIS-SDR-GEO_All/MidTime"][:]

    ds = xr.Dataset(
        {
            "radiance": (["for", "scan", "fov", "channel"], rad)
        },
        coords={
            "latitude": (["for", "scan", "fov"], lat),
            "longitude": (["for", "scan", "fov"], lon),
            "satellite_zenith": (["for", "scan", "fov"], sat_zen),
            "solar_zenith": (["for", "scan", "fov"], sol_zen),
        }
    )

    print(ds)
    return

#---------------

if __name__ == "__main__":
    main()