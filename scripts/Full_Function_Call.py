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
index = 'spei1'
actuarialyear = 2018
baselineyears = [1948, 2016]
studyears = [1948, 2017]
productivity = 1
strike = .8
acres = 500
allocation = .5
returntype = 'lossratio'

returndict = {'producerpremiums': 0, 'indemnities': 1, 'frequencies': 2,
              'pcfs': 3, 'nets': 4, 'lossratios': 5, 'meanppremium': 6,
              'meanindemnity': 7, 'frequencysum': 8, 'meanpcf': 9, 'net': 10,
              'lossratio': 11}

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
           'spi6', 'spei1', 'spei2', 'spei3', 'spei6']
index_paths = {index: "data/indices/" + index + "_arrays.npz" for
               index in indices}
date_paths = {index: "data/indices/" + index + "_dates.npz" for
              index in indices}
index_path = index_paths[index]
date_path = date_paths[index]

# In[] Array lists
premiums = npzIn(premium_path1, premium_path2)
bases = npzIn(base_path1, base_path2)
indexlist = npzIn(index_path, date_path)

# In[] Function call
df = indexInsurance(indexlist, # Index Path
                    grid,
                    premiums,
                    bases,
                    2018,  # Actuarial Year
                    [1948, 2018],  # Study years
                    [1948, 2016],  # Baseline
                    1,  # Productivity
                    .7,  # Strike
                    1,  # Acres
                    1,  # Allocation
                    scale=True,
                    plot=False)

# Choose return (as a number from the ordered list):
# 0-producerpremiums, 1-indemnities, 2-frequencies, 3-pcfs, 4-nets,
# 5-lossratios, 6-meanppremium, 7-meanindemnity, 8-frequencysum, 9-meanpcf,
# 10-net, 11-lossratio

data = df[returndict[returntype]]
# savepath = 'rasters/' + index + '_' + returntype + '.tif'
# toRaster(data, savepath, geom, proj)