HAZARDSTATS README
==================

warmly needed by M. Amadio, kindly scripted by T. Iwanaga

Script to run zonal statistics over rasters on batch, using parallel (multi-core) processing and threshold filtering using standard deviations or percentile clip.

USAGE
-----

1. Prepare input

- Put 1 shapefile to use for zonal extraction and 1 or more raster in a dedicated folder.
- Be sure the shapefile and the rasters have the same CRS.

2. Run script

There are two ways to use the script:

- Run qa_runstats.py and answer the prompt questions. 
  The tool will select autmatically the one shp and all rasters found in the folder. 
  The ouput xlsx is generated in the data folder.
  
  
- Use runstats.py for direct commandline execution, e.g.

      python runstats.py --field OBJECTID --stats median min max --pre SD 2 --ignore "-9999 9999 0 15.4" --ncores 3 --indir C:\temp

  - field: the attribute in the shapefile to identify zones. All features with the same field code will be counted together.

  - stats: the statistics to be calculated. Allows any stats supported by the numpy package.

  - pre: the type of pre-processing filter to apply before statistics. Two options included:
       - SD: Standard deviations from the mean. Specify a value >0 (e.g. SD 2 will filter out all values more than 2 SD from the mean)
       - PC: Percentile distribution threshold. Specify a value between 0 and 100 (e.g. PC 80 will filter out all values above the 80 percentile)
   - ignore: values to be excluded from stats calcualtion. Provided as a list of values in quotes: "-9999 0 1.3"
    
  - ncores: the number of core to use. For best performances use total cores numbers - 1 (e.g. if you have a 8-cores, use 7).
  
  - indir: directory where input files are located (shp and tifs).
