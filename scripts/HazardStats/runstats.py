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
parser.add_argument('--in_dir', type=str,
                    help='An absolute path to the input directory')
parser.add_argument('--prefix', type=str,
                    default='',
                    help='Prefix to add to output filename: [prefix]_sanity_check_[datetime of run]')

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
    in_dir = args.in_dir
    haz_rasters = glob(in_dir + "/*.tif")
    shp_files = glob(in_dir + "/*.shp")

    in_dir
    # shpflename.stat.xlsx

    output_fn = "{}/{}.{}.xlsx".format(in_dir, 
                                       shp_files[0].replace(in_dir, "").replace(".shp", ""),
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