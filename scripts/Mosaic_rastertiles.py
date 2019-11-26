# -*- coding: utf-8 -*-
"""
Created on Tue Jul 23 14:54:51 2019

@author: amadio
"""

import rasterio
from rasterio.merge import merge
from rasterio.plot import show
import glob
import os

# File and folder paths
dirpath = "D:/Amadio/Lidar_VE-RER/VE_140_DTM/"
out_fp = os.path.join(dirpath, "VE140_DTM_Mosaic.tif")

# Make a search criteria to select the DEM files
search_criteria = "D*.asc"
q = os.path.join(dirpath, search_criteria)
print(q)
# glob function can be used to list files from a directory with specific criteria
dem_fps = glob.glob(q)
# Files that were found:
dem_fps
# List for the source files
src_files_to_mosaic = []
# Iterate over raster files and add them to source -list in 'read mode'
for fp in dem_fps:
    src = rasterio.open(fp)
    src_files_to_mosaic.append(src)
src_files_to_mosaic
# Merge function returns a single mosaic array and the transformation info
mosaic, out_trans = merge(src_files_to_mosaic)

# Copy the metadata
out_meta = src.meta.copy()
# Update the metadata
out_meta.update({"driver": "GTiff",
                 "height": mosaic.shape[1],
                 "width": mosaic.shape[2],
                 "transform": out_trans,
                 "Compress": "Deflate"
                 }
                )
# Write the mosaic raster to disk
with rasterio.open(out_fp, "w", **out_meta) as dest:
    dest.write(mosaic)