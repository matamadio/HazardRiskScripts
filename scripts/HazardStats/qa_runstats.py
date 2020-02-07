"""A question and answer approach to using HazardStats"""
import pathlib
from glob import glob
import geopandas as gpd
import os, sys

from runstats import main


if __name__ == '__main__':
    indir = input("Input directory to use? ")
    shp_file = glob(indir+"/*.shp")
    num_shp = len(shp_file)
    if num_shp > 1:
        print("Found more than 1 shapefile! Aborting!")
        print(shp_file)
        sys.exit()
    elif num_shp == 0:
        sys.exit("No shapefile found!")
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

    filtering = input("What filtering to apply? One of 'PC' or 'SD' (leave blank if none) ") or None
    if filtering:
        if filtering not in ['PC', 'SD']:
            print("Unknown filtering! Has to be 'PC' or 'SD', got: {}".format(filtering))
            sys.exit()
        filter_val = input("What threshold/range value? ")
        try:
            filtering = (filtering, float(filter_val))
        except ValueError:
            print("Unexpected values, tried to parse: {} {}".format(filtering, filter_val))
            print("Make sure these are correct.")
            print("Examples of valid entries: PC 80 or SD 2")
            sys.exit()
    
    ignore = input("Any values to ignore? (space separated, leave blank if none) ") or None
    if ignore:
        ignore = ignore.split()
        ignore = [float(v) for v in ignore]

    ncores = input("How many cores to use? (default: 1) ")
    if ncores == '':
        ncores = 1
    else:
        ncores = int(ncores)

    rst_fns = glob(indir+"/*.tif")
    print("Extracting {} for {}, in {} using {} cores\n".format(stats, 
                                                field, 
                                                shp_file,
                                                ncores))
    if filtering:
        print("Before calculating stats, the following filter will be applied: {}".format(filtering))

    print("and doing the above for the following rasters:")
    print(rst_fns, '\n')
    confirm = input("Is this correct? (Y/N) ")
    if "n" in confirm.lower():
        print("Aborting!")
        sys.exit()

    stat_pp = "_".join(stats)
    if filtering:
        stat_pp += "_" + "_".join(map(str, filtering))

    output_fn = "{}/{}.{}.xlsx".format(indir, 
                                       shp_file.replace(indir, "").replace(".shp", ""),
                                       stat_pp)

    opts = {
        'rst_fns': rst_fns,
        'shp_fns': [shp_file],
        'field': field,
        'stats': stats,
        'ncores': ncores,
        'ignore': ignore,
        'preprocess': filtering
    }
    main(output_fn, **opts)
