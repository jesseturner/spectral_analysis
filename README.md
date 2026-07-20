### Spectral Analysis

Tools for comparing the infrared spectra of low clouds and clear sky

Set up on `jturner@jpss-cloud6:/home/jturner/spectral_analysis`
* has MODTRAN installed
* use conda env `spectral_analysis`

This repo has a lot of exploratory analysis
* `notebook_cris.ipynb` has the most developed work, with CrIS LW IR spectral divided by CLAVR-x (VIIRS) cloud type categories
* `create_coloc_cris-clavrx.py` creates the colocated CrIS and CLAVR-x (VIIRS) dataset used in `notebook_cris.ipynb`

Data sources: 
* JPSS instruments VIIRS, CrIS, and Day-Night Band
* GFS model
* Simulated GeoXO sounder (GXS)
* Radiosonde measurements
* CLAVR-x cloud algorithm data (on VIIRS)
