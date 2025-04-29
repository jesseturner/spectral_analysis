import earthaccess
import boto3

#--- Earthaccess docs: https://earthaccess.readthedocs.io/en/latest/quick-start/
auth = earthaccess.login()



#--- Search for the granule by DOI
#------ Suomi NPP Normal Spectral Resolution 10.5067/OZZPDWENP2NC
#------ Suomi NPP Full Spectral Resolution 10.5067/ZCRSHBM5HB23
#------ NOAA-20 / JPSS-1 Full Spectral Resolution 10.5067/LVEKYTNSRNKP
results = earthaccess.search_data(
    doi='10.5067/LVEKYTNSRNKP',
    temporal=("2024-08-18", "2024-08-18"), 
    bounding_box=(-105.31, 39.98, -105.2, 40.062)
)

files = earthaccess.download(results, "CrIS_data")