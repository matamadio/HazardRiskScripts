print "Bathtub is starting..."

# Importing libraries
print "  Importing libraries"
import os,sys
import gdal,gdalconst
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from scipy import ndimage
from skimage import measure
import math
import time
import os
import gc
import shutil
from osgeo import gdal,ogr,osr



# Identifying the regions based on region growing method
print "  Identifying the regions based on region growing method"
def regionGroup(img_array, min_size, no_data):
    s = ndimage.generate_binary_structure(2,2)
    img_array[img_array == no_data] = 0
    label_objects, nb_labels = ndimage.label(img_array, structure=s)
    sizes = np.bincount(label_objects.ravel())
    mask_sizes = sizes > min_size
    mask_sizes[0] = 0
    image_cleaned = mask_sizes[label_objects]
    label_objects, nb_labels = ndimage.label(image_cleaned)
    # nb_labels is the total number of objects. 0 represents background object.
    return label_objects, nb_labels

def GDAL2Numpy(pathname, band=1):
    """
    GDAL2Numpy
    """
    if os.path.isfile(pathname):
        dataset = gdal.Open(pathname, gdalconst.GA_ReadOnly)
        band = dataset.GetRasterBand(band)
        cols = dataset.RasterXSize
        rows = dataset.RasterYSize
        geotransform = dataset.GetGeoTransform()
        projection = dataset.GetProjection()
        nodata = band.GetNoDataValue()
        bandtype = gdal.GetDataTypeName(band.DataType)
        wdata = band.ReadAsArray(0, 0, cols, rows)
        # translate nodata as Nan
        if not wdata is None:
            if bandtype in ('Float32', 'Float64', 'CFloat32', 'CFloat64'):
                if not nodata is None:
                    wdata[wdata == nodata] = np.nan
            elif bandtype in ('Byte', 'Int16', 'Int32', 'UInt16', 'UInt32', 'CInt16', 'CInt32'):
                wdata = wdata.astype("Float32", copy=False)
                wdata[wdata == nodata] = np.nan
        band = None
        dataset = None
        return (wdata, geotransform, projection)
    print("file %s not exists!" % (pathname))
    return (None, None, None)

def Numpy2GTiff(arr, geotransform, projection, filename, nodata=-9999):
    """
    Numpy2GTiff
    """
    if isinstance(arr, np.ndarray):
        rows, cols = arr.shape
        if rows > 0 and cols > 0:
            dtype = str(arr.dtype)
            if dtype in ["uint8"]:
                fmt = gdal.GDT_Byte
            elif dtype in ["uint16"]:
                fmt = gdal.GDT_UInt16
            elif dtype in ["uint32"]:
                fmt = gdal.GDT_UInt32
            elif dtype in ["float32"]:
                fmt = gdal.GDT_Float32
            elif dtype in ["float64"]:
                fmt = gdal.GDT_Float64
            else:
                fmt = gdal.GDT_Float64

            driver = gdal.GetDriverByName("GTiff")
            dataset = driver.Create(filename, cols, rows, 1, fmt)
            if (geotransform != None):
                dataset.SetGeoTransform(geotransform)
            if (projection != None):
                dataset.SetProjection(projection)
            dataset.GetRasterBand(1).SetNoDataValue(nodata)
            dataset.GetRasterBand(1).WriteArray(arr)
            # ?dataset.GetRasterBand(1).ComputeStatistics(0)
            dataset = None
            return filename
    return None


def display_image(img, title="", legend ="", max_plot = False):
    if max_plot == True:
        maxPlotWindow()
    im = plt.imshow(img)
    plt.suptitle(title, fontsize = 24, fontweight='bold', color = "black")
    if legend != "":
        values = np.unique(img.ravel())[1:]
        colors = [im.cmap(im.norm(value)) for value in values]
        # create a patch (proxy artist) for every color
        patches = [mpatches.Patch(color=colors[i], label=legend + " {l}".format(l=int(values[i]))) for i in range(len(values))]
        # put those patched as legend-handles into the legend
        plt.legend(handles=patches, bbox_to_anchor=(1.05, 1), loc=2, borderaxespad=0.)
    plt.show()
    return True


# Declaring the arrays for the loop processing
DEMtiffs = ['Sicilia_cm_1.1.tif', 'Sicilia_cm_1.1.tif', 'Sicilia_cm_1.1.tif', 'Sicilia_cm_1.1.tif']
H2Olevel = [466.0, 533.0, 583.0, 659.0]
OUTtiffs = ['Sicilia_RCP26-1yrRP_1.1.tif', 'Sicilia_RCP85-1yrRP_1.1.tif', 'Sicilia_RCP26-100yrRP_1.1.tif', 'Sicilia_RCP85-100yrRP_1.1.tif']

for i in range(0,4):
    
    # Progress message
    print "  Processing DEM raster ", i+1, " out of 4"

    # Loading the DEM raster
    print "    Loading the DEM raster"
    dem, gt, prj = GDAL2Numpy(DEMtiffs[i]) 

    # Defining the water level in cm
    water_level = H2Olevel[i]

    # Mapping the study area
    print "    Mapping the study area"
    min_size=20
    resolution = gt[1]
    no_data=-9999
    dem = np.where(np.isnan(dem),0,dem)
    dem = np.where(dem==0,water_level,dem) # Setting the water level

    # Mapping the flood extension
    print "    Mapping the flood extension"
    flood_dem = np.where(dem<=water_level,water_level,0)             # Flooding everywhere below threshold
    flood_dem, nb_labels = regionGroup(flood_dem, min_size, no_data) # regionGroup
    flood_dem = np.where(flood_dem==1,water_level,0)                 # Getting the first group connected to the sea
        
    # Mapping the water height
    print "    Mapping the water height"
    water_height=np.where(flood_dem>0.0,(flood_dem-dem),0.0)
    Numpy2GTiff(water_height,gt,prj,OUTtiffs[i]) #'WH.tif')
    del dem, flood_dem, water_height; gc.collect()

# Final results
print "Done!"
