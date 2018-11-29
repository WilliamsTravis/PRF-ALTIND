# -*- coding: utf-8 -*-
"""
Just a place to calculate the full model. Soon, I would like to reincorporate
the full model in the app, but it just takes too long atm. 

Created on Fri Nov 16 13:22:08 2018

@author: User
"""
# In[]
import os
import sys
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, 'c:/users/user/github/PRF-ALTIND')
from functions import *
os.chdir('c:/users/user/github/')

# In[] Argument Definitions
grid, geom, proj = readRaster("data/rma/prfgrid.tif", 1, -9999)
actuarialyear = 2018
baselineyears = [1948, 2016]
studyears = [1948, 2017]
productivity = 1
strike = .8
acres = 500
allocation = .5
returndict = {'producerpremiums': 0, 'indemnities': 1, 'frequencies': 2,
              'pcfs': 3, 'nets': 4, 'lossratios': 5, 'meanppremium': 6,
              'meanindemnity': 7, 'frequencysum': 8, 'meanpcf': 9, 'net': 10,
              'lossratio': 11}
index = 'spi6'
returntype = 'meanindemnity'

# In[] Support functions
def npzIn(array_path, date_path):
    # Get all of the premium rates
    with np.load(array_path) as data:
        arrays = data.f.arr_0
        data.close()
    with np.load(date_path) as data:
        dates = data.f.arr_0
        data.close()
    arraylist = [[str(dates[i]), arrays[i]] for i in range(len(arrays))]

    return arraylist

# In[] Paths
premium_path1 = 'data/actuarial/premium_arrays_2018.npz'
premium_path2 = 'data/actuarial/premium_dates_2018.npz'
base_path1 = 'data/actuarial/base_arrays_2018.npz'
base_path2 = 'data/actuarial/base_dates_2018.npz'
indices = ['noaa', 'pdsi', 'pdsisc', 'pdsiz', 'spi1', 'spi2', 'spi3',
           'spi6', 'spei1', 'spei2', 'spei3', 'spei6', 'eddi1', 'eddi2', 
           'eddi3', 'eddi6']
index_paths = {index: "data/indices/percentiles/" + index + "_arrays.npz" for
               index in indices}
date_paths = {index: "data/indices/percentiles/" + index + "_dates.npz" for
              index in indices}
index_path = index_paths[index]
date_path = date_paths[index]

# In[] Array lists
premiums = npzIn(premium_path1, premium_path2)
bases = npzIn(base_path1, base_path2)

# In[] Function call
for i in tqdm(indices, position=0):
    savepath = ('data/rasters/standardization_tifs/nad83/' + i + '_' +
                returntype + "_" + str(studyears[0]) + "_" +
                str(studyears[1]) + '.tif')
    indexlist = npzIn(index_paths[i], date_paths[i])
    df = indexInsurance_perc(indexlist,  # Index Path
                             grid,
                             premiums,
                             bases,
                             actuarialyear,  # Actuarial Year
                             studyears,  # Study years
                             baselineyears,  # Baseline
                             1,  # Productivity
                             strike,  # Strike
                             acres,  # Acres
                             allocation,  # Allocation
                             scale=False,
                             plot=False)

    # Get return and save to a geotiff
    data = df[returndict[returntype]]
    toRaster(data, savepath, geom, proj)
