# -*- coding: utf-8 -*-
"""
Prepare PRISM temp and precip, this time indexing according to their 1948 
    baseline averages

Created on Mon Feb 26 12:10:44 2018

@author: Travis
"""
runfile('C:/Users/Travis/Google Drive/Thesis/Index Project/scripts/functions.py', wdir='C:/Users/Travis/Google Drive/Thesis/Index Project/scripts')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
os.chdir(r'F:\data\PRISM\temperature\tifs')

# READ IN RASTERS - be careful, these are very large fine resolution rasters
precips, geom, proj = readRasters('F:\\data\\PRISM\\precipitation\\nad83',-9999)
pnorms = normalize(precips,1948,2016)
toRasters(pnorms,r'F:\data\PRISM\precipitation\nad83\indexed',geom,proj)

temps, geom, proj = readRasters('F:\\data\\PRISM\\temperature\\nad83',-9999)
arrays = [temps[i][1] for i in range(len(temps))]
amin = np.nanmin(arrays)
amax = np.nanmax(arrays)
temps = standardize(temps,amin,amax)
tnorms = normalize(temps,1948,2016)
toRasters(tnorms,r'F:\data\PRISM\temperature\nad83\indexed',geom,proj)
