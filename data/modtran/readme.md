- MODTRAN is set up on jpss-cloud6 machine
- Utils available to create input JSON file from GFS and OISST data
- Utils available to run MODTRAN from the command line

- Sample JSON files can be created from modtran6/bin/linux/mod6gui
    - Create with custom setting then save as JSON file in MODTRAN6/


JSON file notes:
- SPECTRAL
  - V1-V2: spectral range
  - DV: spectral resolution, should be about half of FWHM
  - LBMNAM: spectral resolution, limited by selection of BMNAME (0.625 requires 0.1 BMNAME)
  - BMNAME: Spectral model resolution selection, p1 is 0.1.
- AEROSOLS
  - ICLD: type of cloud, like CLOUD_STRATUS
  - VIS: in km, CALT: Cloud base in km

