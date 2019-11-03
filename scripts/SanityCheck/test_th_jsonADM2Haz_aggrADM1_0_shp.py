# -*- coding: utf-8 -*-
"""
Last updated June 2018
Updated to Python 3, 24 December 2018

TH_JSON_Pull.py is a script which will use the ThinkHazard! API to pull
ADM2 level hazard values as JSON files from the ThinkHazard! site.
It groups maximum hazard level by ADM1unit and ADM0 unit, and converts these files to CSV
June 2018 updates include ADM1 and ADM0 names into the files, for easier translation into .shp files.

@author: Erik Bethke; updated Stuart Fraser
"""

# -*- coding: utf-8 -*-
from sys import argv
import pandas as pd
# from osgeo import ogr  # commented as it is not currently in use


script, csv_file = argv

# %% Function definitions for Pandas & admin 1 level hazard level evaluation


def haz_adm(row):
    if row['hazard_level'] == 'VLO':
        return 1
    if row['hazard_level'] == 'LOW':
        return 2
    if row['hazard_level'] == 'MED':
        return 3
    if row['hazard_level'] == 'HIG':
        return 4
    return 0


def change_adm(row):
    if row['hazard_level'] == 1:
        return 'VLO'
    if row['hazard_level'] == 2:
        return 'LOW'
    if row['hazard_level'] == 3:
        return 'MED'
    if row['hazard_level'] == 4:
        return 'HIG'


#%% Set up JSON import
input_text = []
input_links = []
input_options = ['ALL', 'CF', 'CY', 'DG', 'EH',
                 'EQ', 'FL', 'LS', 'TS', 'UF', 'VA', 'WF']
baseURL = 'http://www.thinkhazard.org/en/admindiv_hazardsets'
options = {'CF': (baseURL + '/CF.json'),
           'CY': (baseURL + '/CY.json'),
           'DG': (baseURL + '/DG.json'),
           'EH': (baseURL + '/EH.json'),
           'EQ': (baseURL + '/EQ.json'),
           'FL': (baseURL + '/FL.json'),
           'LS': (baseURL + '/LS.json'),
           'TS': (baseURL + '/TS.json'),
           'UF': (baseURL + '/UF.json'),
           'VA': (baseURL + '/VA.json'),
           'WF': (baseURL + '/WF.json')
           }

print('''The following section will ask what hazards to pull information for. Selections should be separated as an entry for each.
      Options include: ALL, CF, CY, DG, EH, EQ, FL, LS, TS, UF, VA, WF''')
while 1:
    input_file = input("Hazards to pull? (Enter to finish): ")
    if input_file == '':
        break
    elif input_file.upper() == 'ALL':
        input_text.extend(['CF', 'CY', 'DG', 'EH', 'EQ',
                           'FL', 'LS', 'TS', 'UF', 'VA', 'WF'])
        print('Current selection: ', input_text)
    elif input_file.upper() in input_options:
        input_text.append(input_file.upper())
        print('Current selection: ', input_text)
    else:
        print('Selection not valid. Please choose from possible options: ALL, CF, CY, DG, EH, EQ, FL, LS, TS, UF, VA, WF')

for i in input_text:
    if i in options[i]:
        input_links.append(options[i])

print("Parsing the following links:",  input_links, "\n")

# %% ADDED JUNE 2018 SF: Load WB ADM2 boundary data, for lookup of ADMcodes (CO)
lookup_csv = 'THgaul_ADM2_attrib.csv'
lookup = pd.read_csv(lookup_csv, encoding='utf-8', delimiter=';')

# %% Create CSV(s) to write to, write row headers, write JSONS
for i in input_links:
    csv_num = i.split("/")[-1]
    csv_num = csv_num.split(".")[0]
    csv_name = csv_num + "_" + csv_file
    print("Parsing ", csv_name)
    df1 = pd.read_json(i)

    # ADDED JUNE 2018 -
    # rename column headers in exported file, to those of WB ADM files.
    df1.columns = ["ADM2_CODE", "hazard_level",
                   "hazardset", "ADM0_NAME", "ADM1_NAME", "ADM2_NAME"]
    # merge hazard level files, with WB ADM file to include ADM1_CO, ADM0_CO (not incl in TH export)
    df = pd.merge(lookup, df1, on='ADM2_CODE')
    # drop unnecessary merged columns and rename (unwanted suffix applied in merge)
    df = df.drop(columns=["STATUS", "DISP_AREA", "hazardset",
                          "ADM0_NAME_y", "ADM1_NAME_y", "ADM2_NAME_y"])
    df.columns = ["ADM2_CODE", "ADM2_NAME", "ADM1_CODE",
                  "ADM1_NAME", "ADM0_CODE", "ADM0_NAME", "hazard_level"]

    # save to csv
    df.to_csv(csv_name, encoding='utf-8', index=False)
    print(("CSV {} complete.\n".format(csv_name)))
    print(df)

    # *** Admin 1 aggregation output
    # converts value using lookup
    df['haz_val'] = df.apply(lambda row: haz_adm(row), axis=1)

    # group by adm1 code and export to csv
    df_lvl1 = df.groupby(['ADM1_CODE', 'ADM1_NAME', 'ADM0_CODE', 'ADM0_NAME'])[
        'haz_val'].max()
    pandas_name = 'ADMIN1_' + csv_name + '.csv'
    df_lvl1.to_csv(pandas_name, encoding='utf-8', header=None)

    df_fix1 = pd.read_csv(pandas_name, header=None, encoding='utf-8')
    df_fix1.columns = ['ADM1_CODE', 'ADM1_NAME',
                       'ADM0_CODE', 'ADM0_NAME', 'hazard_level']
    df_fix1['hazard_level'] = df_fix1.apply(
        lambda row: change_adm(row), axis=1)
    # df_fix1.columns = ['ADM1_CODE', 'ADM0_CODE', 'hazard_level']
    df_fix1.to_csv(pandas_name, encoding='utf-8', index=False)
    print('Admin 1 unit hazard levels for ', csv_name, " created.")

    # *** Admin 0 aggregation output
    df_lvl0 = df.groupby(['ADM0_CODE', 'ADM0_NAME'])['haz_val'].max()
    pandas_name = 'ADMIN0_' + csv_name + '.csv'
    df_lvl0.to_csv(pandas_name, encoding='utf-8')

    df_fix0 = pd.read_csv(pandas_name, header=None, encoding='utf-8')
    df_fix0.columns = ['ADM0_CODE', 'ADM0_NAME', 'hazard_level']
    df_fix0['hazard_level'] = df_fix0.apply(
        lambda row: change_adm(row), axis=1)
    df_fix0.to_csv(pandas_name, encoding='utf-8', index=False)
    print('Admin 0 unit hazard levels for ', csv_name, " created.\n")

    #  *** JOIN ADM0 CSV to shapefile
    # joinshpPth =
    # joinshpADM0 = os.join(joinshpPth+)
    # joincsv0 = 'ADMIN0_' + csv_name
    # joinshpADM1 = os.join(joinshpPth+'g2015_2014_1_upd270117.shp')
    # joincsv1 = 'ADMIN1_' + csv_name
    # LATEST UPDATE: removed variables FROM SQL

    # COMMENTED BELOW OUT
    # ogr2ogr -sql
    # 'SELECT inshp.*, joincsv.* FROM inshp LEFT JOIN \'ADMIN0_CY_test_good.csv\'.joincsv ON  inshp.ADM0_CODE = joincsv.ADM0_CODE'
    # outputADM0.shp / Users / stufraser / OneDrive / GIS DataBase / AdminBoundaries / FAO_GAUL / GAULinThinkHazard / g2015_2014_012_THupdated / upd270117 / g2015_2014_0_upd270117.shp

    # ogr2ogr -sql "select joinshpADM1.*, joincsv1.hazard_level from joinshpADM1 left join joincsv1 on joincsv1.ADM1_CODE = joinshpADM1.ADM1_CODE" outputADM1.shp joinshpADM1
