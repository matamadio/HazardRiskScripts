"""

HAZARD STATISTICS script
by M. Amadio (mattia.amadio@gmail.com)
Python coding by T. Iwanaga (iwanaga.takuya@anu.edu.au)

Script to run zonal statistics on batch rasters.

USAGE
- Have 1 shapefile to use for zonal extraction and 1 or more raster in a data folder.
- THE SHAPEFILE AND THE RASTERS MUST ALL BE THE SAME PROJECTED (meters) CRS.
- Run qa_runstats.py and answer the prompt questions. The tool will select autmatically the one shp and all rasters found in the folder. The ouput xlsx is generated in the data folder.
- Use runstats.py for commandline execution (parallel processing)

"""

import os
import pathlib
from glob import glob
from datetime import datetime
import itertools as itools

import numpy as np
import pandas as pd
import geopandas as gpd
from openpyxl import load_workbook

import rasterio
from rasterstats import zonal_stats

try:
    # Optional package for progress bar
    from tqdm import tqdm
except ImportError:
    pass


def matching_crs(rst, shp_data):
    """Check that raster and shpfile have matching CRS.

    Parameters
    ==========
    * rst : file pointer, pointer to raster file
    * shp_data : geopandas, shape data

    Returns
    =======
    * Tuple[bool, str] : (True/False indicating CRS match, 
                          and str for failure)
    """
    # Both vector and raster files have to have matching CRS
    shp_crs = shp_data.crs['init']
    rst_crs = rst.crs.to_string()

    if "=" in rst_crs:
        rst_crs = rst_crs.split("=")[1]

    crs_no_match = shp_crs.lower() != rst_crs.lower()
    if crs_no_match:
        # CRS does not match
        issue = "Issues:"
        issue += " Shapefile and raster have differing CRS."
        issue += " shpfile: {}, raster: {}".format(shp_crs, rst_crs)
        
        return (False, issue)
    # End if

    return (True, '')
# End matching_crs()


def extract_stats(shp_files, rst_files, field,
                  stats_of_interest, output_fn):
    """Extract statistics from rasters using shapefiles.

    Parameters
    ==========
    * shp_file : list[str], paths to shapefiles
    * rst_files : list[str], paths to raster files (in .tif format)
    * field : str, field to run calculations for ("ADM0")
    * stats_of_interest : str, listing statistical functions of interest
                          `zonal_stats()` compatible
    * output_fn : str, path and filename of output file

    Returns
    ==========
    * None

    Outputs
    ==========
    * Excel File : `sanity_check_[datetime of run].xlsx`
    """
    all_combinations = itools.product(*[shp_files, rst_files])

    try:
        _loop = tqdm(all_combinations)
    except NameError:
        _loop = all_combinations
    for shp, rst in _loop:
        # Gets raster file name
        sheet_name = os.path.basename(rst)
        shp_name = os.path.basename(shp)

        try:
            # Set msg for progress bar if available
            _loop.set_description("{} {} {}".format(shp_name, sheet_name, field))
        except AttributeError:
            pass

        shp_data = gpd.read_file(shp)
        shp_data['area'] = shp_data.geometry.area
        shp_data = shp_data.sort_values('area')

        if field not in shp_data.columns:
            print("Error: could not find {} in shapefile".format(field))
            print("       Must be one of {}".format(shp_data.columns))
            continue

        with rasterio.open(rst) as src:
            crs_matches, issue = matching_crs(src, shp_data)
            if not crs_matches:
                with pd.ExcelWriter(output_fn, engine='openpyxl')\
                        as writer:
                    df = pd.DataFrame()
                    df.to_excel(writer, sheet_name, startrow=2)
                    del df

                    cmt = "Could not process {} with {}, incorrect CRS."\
                            .format(sheet_name, shp_name)
                    worksheet = writer.sheets[sheet_name]
                    worksheet.cell(row=1, column=1).value = cmt
                    worksheet.cell(row=2, column=1).value = issue
                # End with
                continue
            # End if

            nodata = src.nodatavals
            transform = src.transform
            rst_data = src.read(1)
            rst_data = np.ma.masked_array(rst_data, mask=(rst_data == nodata))
        # End with

        d_shp = shp_data.dissolve(by=field)
        result = zonal_stats(d_shp, rst_data,
                             affine=transform,
                             stats=stats_of_interest,
                             nodata=nodata,
                             geojson_out=True)
        geostats = gpd.GeoDataFrame.from_features(result)
        df = pd.DataFrame(geostats)

        # Filter out rows with empty data
        df = df[(df.loc[:, stats_of_interest] > 0.0).any(axis=1)]

        # Reset index name so it correctly appears when writing out to file
        df.index.name = field

        # Write out dataframe to excel file
        try:
            book = load_workbook(output_fn)
        except FileNotFoundError:
            book = None

        # Write out data to excel file
        with pd.ExcelWriter(output_fn, engine='openpyxl') as writer:
            if book:
                writer.book = book

            df.to_excel(writer, sheet_name, startrow=2)
            comment = "# Extracted from {} using {}"\
                      .format(sheet_name,
                              shp_name)
            worksheet = writer.sheets[sheet_name]
            worksheet.cell(row=1, column=1).value = comment
        # End with
    # End combination loop
# End extract_stats()
