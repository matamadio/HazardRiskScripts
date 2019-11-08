## Requires GDAL installed on your system. On windows OS, install OSGEOw from https://trac.osgeo.org/osgeo4w/
## Place this file in the same folder of your rasters
## Change the CRS (coordinate reference system) specified EPSG, the first is "from" the second is "to"
## If you don't know the CRS code, use QGIS to read this info from rasters metadata
## Set your output folder
## From osgeo shell (or any GDAL-enabled shell), navigate to your folder and write "run"


@echo off
for %%f in (*.tif) do gdalwarp -s_srs EPSG:3857 -t_srs EPSG:32632 %%f C:\your\output\folder\%%f