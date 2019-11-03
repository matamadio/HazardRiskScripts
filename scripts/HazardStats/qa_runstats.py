"""
A question and answer approach to using schecker.py
"""

import argparse
import pathlib
from datetime import datetime
from glob import glob
import geopandas as gpd
import os, sys

from hazardstat import extract_stats


if __name__ == '__main__':
    in_dir = input("Input directory to use? ")
    shp_file = glob(in_dir+"/*.shp")
    if len(shp_file) > 1:
        print("Found more than 1 shapefile! Aborting!")
        print(shp_file)
        sys.exit()
    shp_file = shp_file[0]
    shp_data = gpd.read_file(shp_file)

    print("The shapefile has the following fields:")
    print(list(shp_data.columns), "\n")

    field = input("Which field to process? ")
    if field not in shp_data.columns:
        print("Could not find specified field! Aborting...")
        sys.exit()

    stats = ["max", "min", "mean", "range", "sum"]
    stats_in = input("What statistics to calculate? (default: {}) ".format(stats))
    if stats_in != "":
        stats = stats_in.split()

    rst_files = glob(in_dir+"/*.tif")
    
    print("Calculating {} for {}, in {}".format(stats, 
                                                field, 
                                                shp_file))
    print("and doing the above for the following rasters:")
    print(rst_files)
    confirm = input("Is this correct? (Y/N) ")
    if "n" in confirm.lower():
        print("Aborting!")
        sys.exit()

    output_fn = "{}/{}.{}.xlsx".format(in_dir, 
                                       shp_file.replace(in_dir, "").replace(".shp", ""),
                                       "_".join(stats))

    # openpyxl has trouble with relative paths
    # convert to absolute path to avoid this issue
    abs_output = pathlib.Path(output_fn)
    abs_output = abs_output.resolve()
    print("Outputting data to", abs_output)

    extract_stats([shp_file], rst_files, field,
                  stats, abs_output)