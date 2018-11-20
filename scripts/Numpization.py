# -*- coding: utf-8 -*-
"""
Create single multidimensional numpy files for each index
Created on Fri Jun  8 20:48:33 2018

@author: User
"""
import os
os.chdir(r"C:\Users\User\github\PRF-ALTIND")
from functions import *
os.chdir("C:/users/user/github/")
mask = readRaster("d:\\data\\masks\\nad83\\mask25.tif",1,-9999)[0]
indexnames = ['d:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\',
              'd:\\data\\droughtindices\\palmer\\pdsi\\nad83\\',
              'd:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\',
              'd:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
              'd:\\data\\droughtindices\\spi\\nad83\\1month\\',
              'd:\\data\\droughtindices\\spi\\nad83\\2month\\',
              'd:\\data\\droughtindices\\spi\\nad83\\3month\\',
              'd:\\data\\droughtindices\\spi\\nad83\\6month\\',
              'd:\\data\\droughtindices\\spei\\nad83\\1month\\', 
              'd:\\data\\droughtindices\\spei\\nad83\\2month\\', 
              'd:\\data\\droughtindices\\spei\\nad83\\3month\\', 
              'd:\\data\\droughtindices\\spei\\nad83\\6month\\',
              'd:\\data\\droughtindices\\eddi\\nad83\\1month\\',
              'd:\\data\\droughtindices\\eddi\\nad83\\2month\\',
              'd:\\data\\droughtindices\\eddi\\nad83\\3month\\',
              'd:\\data\\droughtindices\\eddi\\nad83\\6month\\']
savenames = ['noaa','pdsi','pdsisc','pdsiz','spi1','spi2','spi3','spi6',
             'spei1','spei2','spei3','spei6', 'eddi1', 'eddi2', 'eddi3',
             'eddi6']

for i in tqdm(range(len(indexnames))):
    arraylist = readRasters2(indexnames[i], -9999)[0]
    arrays = [a[1]*mask for a in arraylist]
    dates = [a[0] for a in arraylist]
    np.savez_compressed("data\\indices\\"+savenames[i]+"_arrays.npz",arrays)
    np.savez_compressed("data\\indices\\"+savenames[i]+"_dates.npz",dates)
    
# Base rates and premiums
# The premiums and base values are now in raster form, so we just need to convert to arrays
premiums2017 = readRasters2("data\\actuarial\\2017\\rasters\\nad83\\premiums\\",-9999.)[0]      
p2017 = [a[1] for a in premiums2017]
n2017 = [a[0] for a in premiums2017]
premiums2018 = readRasters2("data\\actuarial\\2018\\rasters\\nad83\\premiums\\",-9999.)[0] 
p2018 = [a[1] for a in premiums2018]
n2018 = [a[0] for a in premiums2018]
bases2017 = readRasters2('data\\actuarial\\2017\\rasters\\nad83\\bases\\rates\\',-9999.)[0]     
b2017 = [a[1] for a in bases2017]
bn2017 = [a[0] for a in bases2017]
bases2018 = readRasters2('data\\actuarial\\2018\\rasters\\nad83\\bases\\rates\\',-9999.)[0]     
b2018 = [a[1] for a in bases2018]
bn2018 = [a[0] for a in bases2018]

np.savez_compressed("data\\actuarial\\premiums_arrays_2017.npz",p2017)
np.savez_compressed("data\\actuarial\\premium_dates_2017.npz",n2017)
np.savez_compressed("data\\actuarial\\premium_arrays_2018.npz",p2018)
np.savez_compressed("data\\actuarial\\premium_dates_2018.npz",n2018)
np.savez_compressed("data\\actuarial\\base_arrays_2017.npz",b2017)
np.savez_compressed("data\\actuarial\\base_dates_2017.npz",bn2017)
np.savez_compressed("data\\actuarial\\base_arrays_2018.npz",b2018)
np.savez_compressed("data\\actuarial\\base_dates_2018.npz",bn2018)