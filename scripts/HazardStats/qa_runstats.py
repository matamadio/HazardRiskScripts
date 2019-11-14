"""A question and answer approach to using HazardStats"""
import pathlib
from glob import glob
import geopandas as gpd
import os, sys

from runstats import main


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
    stats_in = input("What statistics to extract? (default: {}) ".format(stats))
    if stats_in != "":
        stats = stats_in.split()

    ncores = input("How many cores to use? (default: 1) ")
    if ncores == '':
        ncores = 1
    else:
        ncores = int(ncores)

    rst_fns = glob(in_dir+"/*.tif")
    print("Extracting {} for {}, in {} using {} cores\n".format(stats, 
                                                field, 
                                                shp_file,
                                                ncores))
    print("and doing the above for the following rasters:")
    print(rst_fns, '\n')
    confirm = input("Is this correct? (Y/N) ")
    if "n" in confirm.lower():
        print("Aborting!")
        sys.exit()

    output_fn = "{}/{}.{}.xlsx".format(in_dir, 
                                       shp_file.replace(in_dir, "").replace(".shp", ""),
                                       "_".join(stats))

    opts = {
        'rst_fns': rst_fns,
        'shp_fns': [shp_file],
        'field': field,
        'stats': stats,
        'ncores': ncores,
    }
    main(output_fn, **opts)
