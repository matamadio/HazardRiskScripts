import os
import csv
import pandas as pd
import xlrd
#from geopy.geocoders import Nominatim
#from geopy.exc import GeocoderTimedOut
#import pandas as pd
#from geolocation.google_maps import GoogleMaps
from pygeocoder import Geocoder
from pygeolib import GeocoderError

#DEFINE PATH
filePath = "C:/Users/Lovly/Dropbox/tmp/Rifiuti/"

#LOAD DATA
workbook = xlrd.open_workbook(filePath+'medical.xlsx')
worksheet = workbook.sheet_by_name('Unmatch')

failed = {
    'row_num': [],
    'address' : []
}

output = {}
total = []

output = {}
# CREATE HEADINGS
headings = ['streetcn','lat','lon','name']
for col in headings:
    output[col] = []

#GET COORDINATES
num_rows = worksheet.nrows - 1
curr_row = 0

myFilePath = os.path.join(filePath, 'output_medic.csv')
    
while curr_row < num_rows:
    curr_row += 1
    row = worksheet.row(curr_row)
    curr_cell = 0
    cell_type = worksheet.cell_type(curr_row, curr_cell)
    cell_value = worksheet.cell_value(curr_row, curr_cell)
    print worksheet.cell_value(curr_row, 0)
    if cell_value != '':
        # address = cell_value.encode("utf8")
        address = cell_value
        try:
            location = Geocoder.geocode(address)
            if location != None:
                output['streetcn'].append(cell_value.encode("utf8"))
                output['lat'].append(location.coordinates[0])
                output['lon'].append(location.coordinates[1])
                output['name'].append(worksheet.cell_value(curr_row, 1).encode("utf8"))
                print cell_value, location.coordinates[0], location.coordinates[1], worksheet.cell_value(curr_row, 1)

        except GeocoderError:
            print "The address '{}' could not be geocoded (row number: {})".format(address, curr_row)
            failed['address'].append(address)
            failed['row_num'].append(curr_row)

# index = False removes row numbers
pd.DataFrame(output).to_csv(myFilePath, index=False, encoding='utf-8')
pd.DataFrame(failed).to_csv(filePath+"failed.csv", index=False, encoding='utf-8')

## WRITE OUTPUT TO A CSV FILE
#myFilePath = os.path.join(filePath, 'output_mattia.csv')
#myCSVFile = open(myFilePath, 'wb')
#writer = csv.DictWriter(myCSVFile, fieldnames=headings, extrasaction='ignore', dialect='excel', quoting=csv.QUOTE_NONNUMERIC)
#writer.writeheader() 
#for row in total:
#    writer.writerow(row)
# myCSVFile.close()

# WRITE OUTPUT TO AN EXCEL FILE
#df = pd.DataFrame(total, columns=headings)        
#df.to_excel("TOTAL_OUTPUT.xls" , "data")

#WRITE FAILED OUTPUT TO CSV FILE

#    a = csv.writer(fp, delimiter=',')
#    data = totalfail
#    a.writerows(data)