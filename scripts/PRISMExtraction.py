# -*- coding: utf-8 -*-
"""
Created on Wed Nov 22 08:48:09 2017

    This is to extract rasters from these huge PRISM datasets. It's tricky to 
        me because they are organized by month, each with 123 years worth of
        data for that month.


@author: Travis
"""
import os
os.chdir('C:/Users/User/Github/PRF-ALTIND')
from functions import *

###############################################################################
############## New  Numpization Function  #####################################
###############################################################################
# This is needed for multiband rasters
# Each one of the 12 tifs contain 123 bands. Each band represents a year at the associated month
# So Index_1_PRISM contains 123 years worth of data for just january
# These are going to be rather large arrays, pay attention to the memory

################################### New Function #############################
def tifCollect(rasterpath, year, indexname, mask):
    """
    raster path = path to folder with list of raster files
    year = year from each raster to extract after
    indexname = string of name of index in question
    
    Remember this only works for PRISM drought indices atm, and 
        for now its only tested with the PDSI.
    """
    if rasterpath[:-2] != '\\':
        rasterpath = rasterpath + '\\'
    files = glob.glob(rasterpath+'*.tif')
    sample = gdal.Open(files[0])
    geom = sample.GetGeoTransform()
    proj = sample.GetProjection()
    indexlist = [] 
    
    def daystoDate(raster, band, startyear):
        days = raster.GetRasterBand(band).GetMetadata().get('NETCDF_DIM_day')
        date = datetime.datetime(startyear,1,1,0,0) + datetime.timedelta(int(days) - 1)
        return date.strftime("%Y%m")

    # Below will get the names. We could do the same thing with the raster, however...memory problems
    for path in tqdm(files):
        print(path)
        raster = gdal.Open(path)
        yearly = [[indexname+"_"+daystoDate(raster,band,1900),np.array(raster.GetRasterBand(band).ReadAsArray())*mask] for band in range(1,raster.RasterCount+1) if int(daystoDate(raster,band,1900)[:-2]) >= year]
        indexlist.append(yearly)
    indexlist = [index for sublist in indexlist for index in sublist] 
    indexlist.sort()
    return([indexlist,geom,proj])


################################# Call  ############################################################  
# Watch out for memory --  And don't try to open the list in variable explorer!! 
maskpath = 'd:\\data\\droughtindices\\masks\\nad83\\mask4.tif'
mask,geo,proj = readRaster(maskpath,1,-9999.) 
indexname = 'SPI-1'
year = 1948
rasterpath = 'd:\\data\\droughtindices\\spi\\nad83\\full\\quarteres\\1month'
[indexlist,geom,proj] = tifCollect(rasterpath,year,indexname,mask)

savepath = 'd:\\data\\droughtindices\\spi\\nad83\\1month\\'
toRasters(indexlist,savepath,geom,proj)






################################# Solo Tests #######################################################  

path = "e:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\temp\\"
rast = gdal.Open(path)
array = np.array(rast.GetRasterBand(1).ReadAsArray())
array = array.astype(float)
array[array==navalue] = np.nan
array = array*mask

path = "e:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\"
toRaster(indexlist,path,geom,proj)








# Now let's check one against an existing one

checkpath =  'palmer\\pdsi\\nad83\\'
files = glob.glob(checkpath+'*.tif')
file = checkpath+'pdsi201410.tif'
sample = gdal.Open(file)
check = np.array(sample.GetRasterBand(1).ReadAsArray())
check[check == -9999.] = np.nan

checkee = indexlist[801][1]
checkee[checkee == -9999.] = np.nan

ax2 = plt.subplot(111)
im2 = ax2.imshow(check)
divider2 = make_axes_locatable(ax2)
cax2 = divider2.append_axes("right", size="5%", pad=0.05)
plt.colorbar(im2, cax=cax2)
title2=("Old PDSI - October, 2014 \n Somewhat different in appearance, data back to only 2000")
plt.title(title2,loc = 'right')