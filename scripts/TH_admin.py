# TH admin layer fixer
# Basically adds rows (features) and columns (attributes)
# from patch files to original WB shapefile 
# Then it renames some ADM units with better known spelling to improve search

# Import libraries
import os
import numpy as np
import pandas as pd
import geopandas as gpd
from datetime import datetime

# set working dir
os.chdir('X:/Work/WB/Thinkhazard/Geodata/admin/test/')
# Load shp files and table
wb = gpd.read_file('g2015_2014_0.shp').drop(['EXP0_YEAR', 'STR0_YEAR', 'Shape_Le_1'], 1)
thp = gpd.read_file('TH_patch.shp')
tha = gpd.read_file('TH_fields.dbf').drop('geometry', 1)
# Remove france
for index, row in wb.iterrows():
    if row['ADM0_NAME'] == 'France':
        wb.drop(index, inplace=True)
# Merge shp files
ADM0 = gpd.GeoDataFrame(pd.concat([wb, thp], ignore_index=True))
#Add TH attributes from table
ADM0 = ADM0.merge(tha, on='ADM0_CODE', how='left')
# Ref system
ADM0.crs= {'init': 'epsg:4326'}
#Export shp
ADM0.to_file("ADM0_TH.shp", driver="ESRI Shapefile")

# Apply corrections to ADM1 and ADM2 names
ADM1 = gpd.read_file('g2015_2014_1.shp').drop(['EXP1_YEAR', 'STR1_YEAR', 'Shape_Le_1'], 1)
ADM1[['UpdtField', 'OrigVal', 'Updated', 'FRE', 'ESP', 'LOCAL']] = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], index=ADM1.index)
ADM2 = gpd.read_file('g2015_2014_2.shp').drop(['EXP2_YEAR', 'STR2_YEAR', 'Shape_Le_1'], 1)
ADM2[['UpdtField', 'OrigVal', 'Updated', 'FRE', 'ESP', 'LOCAL']] = pd.DataFrame([[np.nan, np.nan, np.nan, np.nan, np.nan, np.nan]], index=ADM2.index)

corrections = {'Tookyoo': 'Tokyo', 'Tiba': 'Chiba', 'U.K. of Great Britain and Northern Ireland': 'United Kingdom', 'Norfolkshire': 'Norfolk'}
tgt_col = 'ADM1_NAME'
curr_date = datetime.today().strftime('%Y-%m-%d')
for k, v in corrections.items():
    ADM1.loc[ADM1.ADM1_NAME == k, ['UpdtField', 'OrigVal', 'Updated', tgt_col]] = [tgt_col, k, curr_date, v]
    ADM2.loc[ADM2.ADM1_NAME == k, ['UpdtField', 'OrigVal', 'Updated', tgt_col]] = [tgt_col, k, curr_date, v]    
    ADM2.loc[ADM2.ADM2_NAME == k, ['UpdtField', 'OrigVal', 'Updated', tgt_col]] = [tgt_col, k, curr_date, v]

# Ref system
ADM1.crs= {'init': 'epsg:4326'}
ADM2.crs= {'init': 'epsg:4326'}

#Export shp
ADM1.to_file("ADM1_TH.shp", driver="ESRI Shapefile")
ADM2.to_file("ADM2_TH.shp", driver="ESRI Shapefile")