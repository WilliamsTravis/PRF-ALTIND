# -*- coding: utf-8 -*-
"""
 I don't have my hard drive with the rasters in them, but I want to create a new RMW dataset with 
     The PDSISC. I do have the npz files, though the R scripts needs rasters. So, I could instead 
     read in the numpy arrays for the palmers, read in the srs and geometries from the grid tiff
     then write the palmers to a list of raster somewhere. 


Created on Thu Sep  6 13:35:55 2018

@author: User
"""
runfile('C:/Users/user/Github/PRF-ALTIND/functions.py', 
        wdir='C:/Users/user/Github/PRF-ALTIND')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
os.chdir(r'C:\Users\user\Github')

# first get the geo info from the prfgrid file
grid, geom, proj = readRaster("data/prfgrid.tif",1,-9999)
  
# Read in the numpy arrays and file names
with np.load("data/indices/noaa_arrays.npz") as data:
    arrays = data.f.arr_0
    data.close()
with np.load("data/indices/noaa_dates.npz") as data:
    names = data.f.arr_0
    data.close()
timeseries = [[str(names[y]),arrays[y]] for y in range(len(arrays))]

# Now write to a file
savefolder = "data/rasters/nad83/noaa"
toRasters(timeseries,savefolder,geom,proj)


#
## Where are we?
#loc = np.where(grid == 24099)
#
## Just arrays
#arrays = [a[1] for a in timeseries]
#
## Just boulder
#boulder = [[a[0], a[1][loc]] for a in timeseries]
#
#dates = [b[0] for b in boulder]
#numbers = [b[1] for b in boulder]
#
#rows = dict(zip(dates,numbers))
#
#import pandas as pd
#df = pd.DataFrame(rows)
