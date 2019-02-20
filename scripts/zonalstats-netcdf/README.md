git_repos-netCDF

# Zonal stats on Netcdf - Readme and instructions
by Takuya Iwanaga and Mattia Amadio.

This code allows to run zonal statistics accounting all the bands of the netcdf.
In the example, we use italian regions to extract the average of temperature from climatic data. The code is tested on anaconda and atom environment.

## REQUIREMENTS AND RUN:
Requires the installation of numpy, pandas and rasterio libraries.

> conda install -c conda-forge rasterio pandas numpy

- Edit run_operation.py to specify workspace and source files.
- Edit netcdf_interaction.py to change "NOME_REG" with the field of zonal areas.
- Run the analysis.
