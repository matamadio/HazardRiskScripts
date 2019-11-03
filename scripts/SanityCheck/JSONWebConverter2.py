# -*- coding: utf-8 -*-
"""
Created on Fri Aug 25 14:31:15 2017

@author: Erik Bethke
"""

# -*- coding: utf-8 -*-
from sys import argv
import csv
import json
import urllib.request
import http.client

http.client.HTTPConnection._http_vsn = 10
http.client.HTTPConnection_http_vsn_str = 'HTTP/1.0'

script, csv_file = argv

#%% Set up JSON import
input_links = []

while 1:
    input_file = input("Enter your JSON URL to parse (Enter to stop): ")
    if input_file == '':
        break
    input_links.append(input_file)
'''
## For Manual Entry of input links.
input_links = ['http://www.thinkhazard.org/en/admindiv_hazardsets/EQ.json']
'''
print("Parsing the following links:",  input_links)

#%% Create CSV(s) to write to, write row headers, write JSONS
numCSV = input("All files parsed to individual CSVs (Enter 1), or to one CSV (Enter 2)? ")

if numCSV == "1":
    for i in input_links:
        csv_num = i.split("/")[-1]
        csv_num = csv_num.split(".")[0]
        csv_name = csv_num +  "_" + csv_file
        print("Parsing ", csv_name)
        out_csv = csv.writer(open(csv_name, 'w', encoding = 'utf-8'), delimiter = ',', lineterminator = '\n')
        out_csv.writerow(['code', 'name', 'hazardset', 'hazard_level', 'level_1', 'level_2'])
        # Write JSONs to CSV
        jsonlink = urllib.request.urlopen(i)
        infile_parsed = json.loads(jsonlink.read())
        for x in infile_parsed:
            out_csv.writerow([x["code"], x["name"], x["hazardset"], x["hazard_level"], x["level_1"], x["level_2"]])
    print("CSV %s complete." % csv_name)
elif numCSV == "2":
    out_csv = csv.writer(open(csv_file, 'w', encoding = 'utf-8'), delimiter = ',', lineterminator = '\n')
    out_csv.writerow(['code', 'name', 'hazardset', 'hazard_level', 'level_1', 'level_2'])
    print("Headers built.")

    # Write JSONs to CSV
    listval = 0
    for i in input_links:
        print("Parsing ", input_links[listval])
        jsonlink = urllib.request.urlopen(i)
        infile_parsed = json.loads(jsonlink.read())
        for x in infile_parsed:
            out_csv.writerow([x["code"], x["name"], x["hazardset"], x["hazard_level"], x["level_1"], x["level_2"]])
        listval += 1
    print("CSV complete.")
