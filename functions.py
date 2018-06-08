# -*- coding: utf-8 -*-
"""
Created on Sun May 28 21:14:48 2017

@author: Travis
"""

#import copy
import dash
from dash.dependencies import Input, Output, State, Event
import dash_core_components as dcc
import dash_html_components as html
import dash_table_experiments as dt
import gc
import json
from flask import Flask
from flask_cors import CORS
from flask_cache import Cache
import numpy as np
import numpy.ma as ma
import pandas as pd
import plotly
from tqdm import *
import xarray as xr
#from flask_caching import Cache
#import gdal
#import datetime
#from datetime import timedelta
#from itertools import chain
#import matplotlib
#import matplotlib.pyplot as plt, mpld3
#import matplotlib.image as mpimg
#import matplotlib.gridspec as gridspec
#from matplotlib.ticker import FuncFormatter
#from matplotlib import style
#from mpl_toolkits.axes_grid1 import make_axes_locatable
#from matplotlib.patches import Patch
#from osgeo import ogr, osr
#import plotly.plotly as py
#import plotly.tools as tls
#from plotly import tools
#from plotly.graph_objs import *
#import plotly.graph_objs as go
#import rasterio
#import boto3
#import urllib
#import botocore

#def PrintException():
#    exc_type, exc_obj, tb = sys.exc_info()
#    f = tb.tb_frame
#    lineno = tb.tb_lineno
#    filename = f.f_code.co_filename
#    linecache.checkcache(filename)
#    line = linecache.getline(filename, lineno, f.f_globals)
#    print('EXCEPTION IN ({}, LINE {} "{}"): {}'.format(filename, lineno, line.strip(), exc_obj))
#
#gdal.UseExceptions()
#print("GDAL version:" + str(int(gdal.VersionInfo('VERSION_NUM'))))


###########################################################################
##################### Quick Histograms ####################################
###########################################################################    
def indexHist(array,guarantee = 1,mostfreq = 'n',binumber = 1000, limmax = 0, sl = 0):
    '''
    array = single array or list of arrays
    '''
    
    # Check if it is a list with names, a list without names, a single array with a name, 
        # or a single array without a name.
    if str(type(array)) == "<class 'list'>":
        if type(array[0][0]) == str and len(array[0])==2:
            name = array[0][0][:-7] + ' Value Distribution'
            array = [ray[1] for ray in array]
            na = array[0][0,0]    
            for ray in array:
                ray[ray == na] = np.nan
        elif type(array[0]) == str:
            name = array[0] + ' Value Distribution'
            array = array[1]
            na = array[0,0]    
            array[array == na] = np.nan
        else:
            na = array[0][0,0]
            name = "Value Distribution"
            for ray in array:
                ray[ray == na] = np.nan
    else:
        na = array[0,0]
        name = "Value Distribution"
        array[array == na] = np.nan
    
    # Mask the array for the histogram (Makes this easier)
    arrays = np.ma.masked_invalid(array)
    
    # Get min and maximum values
    amin = np.min(arrays)
    printmax = np.max(arrays)
    if limmax > 0:
        amax = limmax
    else:
        amax = np.max(arrays)
        
    # Get the bin width, and the frequency of values within, set some
    # graphical parameters and then plot!
    fig = plt.figure(figsize=(8, 8))
    hists,bins = np.histogram(arrays,range = [amin,amax],bins = binumber,normed = False)
    if mostfreq != 'n':
        mostfreq =  float(bins[np.where(hists == np.max(hists))])
        targetbin = mostfreq
        targethist = np.max(hists)
        firstprint = 'Most Frequent Value: '+ str(round(mostfreq,2))    
    # Get bin of optional second line
    if sl != 0:     
        differences = [abs(bins[i] - sl) for i in range(len(bins))]
        slindex = np.where(differences == np.nanmin(differences))
        secondline = bins[slindex]
        slheight = hists[slindex]
        secondtitle = '\nRMA Strike level: ' + str(guarantee) + ', Alt Strike Level: ' + str(round(sl,4))
    else:
        secondtitle = ''
    if mostfreq != 'n':
        if mostfreq == 0:
            secondcheck = np.copy(hists)
            seconds = secondcheck.flatten()
            seconds.sort() 
            second = float(bins[np.where(hists == seconds[-2])])
            targetbin = second
            targethist= seconds[-2]
            secondprint = '\n       Second most Frequent: '+str(round(second,2))
        else:
            secondprint = '' 
    width = .65 * (bins[1] - bins[0])
    center = (bins[:-1] + bins[1:]) / 2
    plt.bar(center, hists, align='center', width=width)
    title=(name+":\nMinimum: "+str(round(amin,2))+"\nMaximum: "+str(round(printmax,2))+secondtitle)
    plt.title(title,loc = 'center')    
    if mostfreq != 'n':
        plt.axvline(targetbin, color='black', linestyle='solid', linewidth=4)
        plt.axvline(targetbin, color='r', linestyle='solid', linewidth=1.5)
    drange = np.nanmax(arrays) - np.nanmin(arrays)

    if sl != 0:
        plt.axvline(secondline, color='black', linestyle='solid', linewidth=4)
        plt.axvline(secondline, color='y', linestyle='solid', linewidth=1.5)
#        plt.annotate('Optional Threshold: \n' + str(round(sl,2)), xy=(sl-.001*drange, slheight), xytext=(min(bins)+.1*drange, slheight-.01*max(hists)),arrowprops=dict(facecolor='black', shrink=0.05))


###############################################################################
########################## AWS Retrieval ######################################
###############################################################################
# For singular Numpy File - Might have to write this for a compressed numpy 
def getNPY(path):
    key=[i.key for i in bucket.objects.filter(Prefix = path)][0] # Probably an easier way
    obj = resource.Object("pasture-rangeland-forage", key)
    try:
        with io.BytesIO(obj.get()["Body"].read()) as f:
            # rewind the file
            f.seek(0)
            array = np.load(f)
            array = array.f.arr_0    
    except botocore.exceptions.ClientError as e:
        error = e
        if error.response['Error']['Code'] == "404":
            array = "The object does not exist."
        else:
            raise
    return array

# For 3D Numpy files
def getNPYs(numpypath,csvpath):
    # Get arrays
    key=[i.key for i in bucket.objects.filter(Prefix = numpypath)][0] # Probably an easier way
    obj = resource.Object("pasture-rangeland-forage", key)
    try:
        with io.BytesIO(obj.get()["Body"].read()) as file:
            # rewind the file
            file.seek(0)
            array = np.load(file)
            arrays = array.f.arr_0    
    except botocore.exceptions.ClientError as error:
        print(error)

    # get dates
    key=[i.key for i in bucket.objects.filter(Prefix = csvpath)][0] # Probably an easier way
    obj = resource.Object("pasture-rangeland-forage", key)
    try:
        with io.BytesIO(obj.get()["Body"].read()) as df:        
            datedf = pd.read_csv(df)
    except botocore.exceptions.ClientError as error:
        print(error)
        
    arrays = [[datedf['dates'][i],arrays[i]] for i in range(len(arrays))]
    return arrays




###############################################################################
##################### Convert single raster to array ##########################
###############################################################################
def readRaster(rasterpath,band,navalue = -9999):
    """
    rasterpath = path to folder containing a series of rasters
    navalue = a number (float) for nan values if we forgot 
                to translate the file with one originally
    
    This converts a raster into a numpy array along with spatial features needed to write
            any results to a raster file. The return order is:
                
      array (numpy), spatial geometry (gdal object), coordinate reference system (gdal object)
    
    """
    raster = gdal.Open(rasterpath)
    geometry = raster.GetGeoTransform()
    arrayref = raster.GetProjection()
    array = np.array(raster.GetRasterBand(band).ReadAsArray())
    del raster
    array = array.astype(float)
    if np.nanmin(array) < navalue:
        navalue = np.nanmin(array)
    array[array==navalue] = np.nan
    return(array,geometry,arrayref)

###############################################################################
##################### Convert single raster to array ##########################
###############################################################################
def readRasterAWS(awspath,navalue = -9999):
    """
    rasterpath = path to folder containing a series of rasters
    navalue = a number (float) for nan values if we forgot 
                to translate the file with one originally
    
    This converts a raster into a numpy array along with spatial features needed to write
            any results to a raster file. The return order is:
                
      array (numpy), spatial geometry (gdal object), coordinate reference system (gdal object)
    
    """
    with rasterio.open(awspath) as src:
        array = src.read(1,window = ((0,120),(0,300)))
        geometry = src.get_transform()
        arrayref = src.get_crs()
    array = array.astype(float)
    if np.nanmin(array) < navalue:
        navalue = np.nanmin(array)
    array[array==navalue] = np.nan
    return array
###############################################################################
######################## Convert multiple rasters #############################
####################### into numpy arrays #####################################
###############################################################################
def readRasters(rasterpath,navalue = -9999):
    """
    rasterpath = path to folder containing a series of rasters
    navalue = a number (float) for nan values if we forgot 
                to translate the file with one originally
    
    This converts monthly rasters into numpy arrays and them as a list in another
            list. The other parts are the spatial features needed to write
            any results to a raster file. The list order is:
                
      [[name_date (string),arraylist (numpy)], spatial geometry (gdal object), coordinate reference system (gdal object)]
    
    The file naming convention required is: "INDEXNAME_YYYYMM.tif"

    """
    print("Converting raster to numpy array...")
    alist=[]
    if '/' in rasterpath:
        files = ["s3://pasture-rangeland-forage/" + i.key for i in bucket.objects.filter(Prefix = rasterpath)]
        rootlen = len(files[0])    
        names = [files[i][rootlen:] for i in range(len(files))] 
    else:
        files = glob.glob(rasterpath+"*tif")
        names = os.listdir(rasterpath)
    with rasterio.open(files[0]) as src:  
        geometry = src.get_transform()
        arrayref = src.get_crs()
    for i in tqdm(range(0,len(files))): 
        with rasterio.open(files[i]) as src:
            array = src.read(1,window = ((0,120),(0,300)))
        array = array.astype(float)
        array[array==navalue] = np.nan
        name = str.upper(names[i][:-4]) # the file name excluding its extention (may need to be changed if the extension length is not 3)
        alist.append([name,array]) # It's confusing but we need some way of holding these dates. 
    return(alist,geometry,arrayref)
    
###############################################################################
######################## Convert multiple rasters #############################
####################### into numpy arrays silently ############################
###############################################################################
def readRasters2(rasterpath,navalue = -9999):
    """
    rasterpath = path to folder containing a series of rasters
    navalue = a number (float) for nan values if we forgot 
                to translate the file with one originally
    
    This converts monthly rasters into numpy arrays and them as a list in another
            list. The other parts are the spatial features needed to write
            any results to a raster file. The list order is:
                
      [[name_date (string),arraylist (numpy)], spatial geometry (gdal object), coordinate reference system (gdal object)]
    
    The file naming convention required is: "INDEXNAME_YYYYMM.tif"

    """
    alist=[]
    if rasterpath[-1:] != '\\':
        rasterpath = rasterpath+'\\'
    files = glob.glob(rasterpath+'*.tif')
    names = [files[i][len(rasterpath):] for i in range(len(files))]
    sample = gdal.Open(files[0])
    geometry = sample.GetGeoTransform()
    arrayref = sample.GetProjection()
    del sample
    start = time.clock()
    for i in tqdm(range(len(files))): 
        rast = gdal.Open(files[i])
        array = np.array(rast.GetRasterBand(1).ReadAsArray())
        del rast
        array = array.astype(float)
        array[array==navalue] = np.nan
        name = str.upper(names[i][:-4]) #the file name excluding its extention (may need to be changed if the extension length is not 3)
        alist.append([name,array]) # It's confusing but we need some way of holding these dates. 
    end = time.clock() - start       
    return(alist,geometry,arrayref)

