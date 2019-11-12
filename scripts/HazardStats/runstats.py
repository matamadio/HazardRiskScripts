import argparse
import pathlib
from datetime import datetime
from glob import glob

from hazardstat import extract_stats

example_text = '''usage example:

 python runstats.py --show C:/temp/shpfile.shp
 python runstats.py --field OBJECTID --stats min max --in_dir C:\temp
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
    haz_rasters = glob(indir + "/*.tif")
    shp_files = glob(indir + "/*.shp")

    output_fn = "{}/{}.{}.xlsx".format(indir, 
                                       shp_files[0].replace(indir, "").replace(".shp", ""),
                                       "_".join(stats_to_calc))

    # openpyxl has trouble with relative paths
    # convert to absolute path to avoid this issue
    abs_output = pathlib.Path(output_fn)
    abs_output = abs_output.resolve()
    print("Outputting data to", abs_output)

    assert len(shp_files) > 0, "No shapefiles found!"
    assert len(haz_rasters) > 0, "No rasters found!"

    extract_stats(shp_files, haz_rasters, field_to_check,
                  stats_to_calc, abs_output)