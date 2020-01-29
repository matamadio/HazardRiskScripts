HazardRisk
==========

The scripts folder includes the tools developed for thinkhazard.
- Sanity check: scripts for extracting data from TH and perform zonal statistics on rasters
- HazardStats: script for batch zonal statistics, percentile and standard deviation threshold option, uses multi-core processing
- Corpsec: extraction of data for key urban areas for Corporate security
- zonalstats-netcdf: perform zonal statistics through .nc files
- TH_admin.py: TH admin layer fixer, adds rows (features) and columns (attributes) from patch files to original WB shapefile. Then it renames some ADM units with better known spelling to improve search

Intended to run on a Windows environment. Others are not guaranteed to work.

Dependencies
-------------------
tqdm
numpy
pandas
geopandas
rasterio
rasterstats
scipy
skimage
openpyxl

