import argparse
import pathlib
from datetime import datetime
from glob import glob
import itertools as itools

from hazardstat import (extract_stats, write_to_excel)

example_text = '''usage example:

 python runstats.py --show C:/temp/shpfile.shp
 python runstats.py --field OBJECTID --stats min max --ncores 3 --indir C:\temp
'''

parser = argparse.ArgumentParser(description='Sanity check',
                                 epilog=example_text,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
parser.add_argument('--show', type=str,
                    help='Display the available fields from a given shapefile (absolute path)')
parser.add_argument('--field', type=str,
                    help='Specify the field to perform calculations for')
parser.add_argument('--stats', type=str, nargs='+',
                    default=["max", "min", "mean", "range", "sum"],
                    help='Statistics to calculate (default: max min mean range sum)')
parser.add_argument('--indir', type=str,
                    help='Path to the input directory (preferably an absolute path)')
parser.add_argument('--ncores', type=int,
                    default=1,
                    help='Number of cores to use')


def main(output_fn, **opts):
    # openpyxl has trouble with relative paths
    # convert to absolute path to avoid this issue
    abs_output = pathlib.Path(output_fn)
    abs_output = abs_output.resolve()
    print("Outputting data to", abs_output)

    ncores = opts['ncores']
    shp_fns = opts['shp_fns']
    rst_fns = opts['rst_fns']
    field = opts['field']
    stats = opts['stats']

    if ncores > 1:
        import multiprocess as mp
        from hazardstat import apply_extract

        with mp.Manager() as manager:
            # `d` is a DictProxy object shared between all processes
            # can be converted to dict for final write out
            d = manager.dict()
            with manager.Pool(processes=ncores) as pool:
                # Map each shapefile to a single raster
                # Then call apply_extract for each shp->raster combination
                file_combs = itools.product(*[[d], shp_fns, rst_fns, [field], [stats]])
                procs = pool.starmap_async(apply_extract, file_combs)
                procs.get()

            results = dict(d)
    else:
        results = extract_stats(shp_fns, rst_fns, field, stats)

    print("Writing results...")
    write_to_excel(abs_output, results)
    print("Finished")
# End main()

if __name__ == '__main__':
    args = parser.parse_args()

    if args.show:
        import geopandas as gpd
        import sys
        shp = gpd.read_file(args.show)
        print("Available fields:", list(shp.columns))
        sys.exit(0)

    field_to_check = args.field
    stats_to_calc = args.stats

    print("Calculating {} for {}".format(stats_to_calc, field_to_check))

    # Get hazard geotiff and shapefiles for stat zones
    # Shapefile for stats zones
    indir = args.indir
    rst_fns = glob(indir + "/*.tif")
    shp_fns = glob(indir + "/*.shp")

    assert len(shp_fns) > 0, "No shapefiles found!"
    assert len(rst_fns) > 0, "No rasters found!"

    output_fn = "{}/{}.{}.xlsx".format(indir, 
                                       shp_fns[0].replace(indir, "").replace(".shp", ""),
                                       "_".join(stats_to_calc))

    ncores = args.ncores
    opts = {
        'rst_fns': rst_fns,
        'shp_fns': shp_fns,
        'field': field_to_check,
        'stats': stats_to_calc,
        'ncores': ncores,
    }

    main(output_fn, **opts)
