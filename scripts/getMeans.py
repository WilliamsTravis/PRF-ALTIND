# -*- coding: utf-8 -*-
"""
This creates the chart of average national payments. Toggle scale to False to
show original differences in payouts, and True to see the result of the scaling
process.

Created on Fri Apr 20 14:39:02 2018

@author: trwi0358
"""
import os
import sys
import warnings
sys.path.insert(0, 'c:/users/user/github/PRF-ALTIND')
from functions import *
warnings.filterwarnings("ignore")
os.chdir('C:/Users/user/Github')

# In[] Get material
grid = readRaster("data/rma/prfgrid.tif", 1, -9999)[0]
mask = grid * 0 + 1

# Actuarial rates
premiums = npzIn('data/actuarial/premium_arrays_2018.npz',
                 'data/actuarial/premium_dates_2018.npz')
bases = npzIn('data/actuarial/base_arrays_2018.npz',
              'data/actuarial/base_dates_2018.npz')

# Index paths
indices = ['noaa', 'pdsi', 'pdsisc', 'pdsiz', 'spi1', 'spi2', 'spi3',
           'spi6', 'spei1', 'spei2', 'spei3', 'spei6']

# Index Lists
arraydict = []
for i in tqdm(range(len(indices)), position=0):
    timeseries = npzIn("data/indices/" + indices[i] + "_arrays.npz",
                       "data/indices/" + indices[i] + "_dates.npz")
    arraydict.append(timeseries)
arraydict = {indices[i]: arraydict[i] for i in range(len(indices))}

# Index names for the table
indexnames = {'noaa': 'NOAA',  'pdsi': 'PDSI', 'pdsisc': 'PDSIsc',
              'pdsiz': 'PDSIz', 'spei1': 'SPEI-1', 'spei2': 'SPEI-2',
              'spei3': 'SPEI-3', 'spei6': 'SPEI-6', 'spi1': 'SPI-1',
              'spi2': 'SPI-2', 'spi3': 'SPI-3', 'spi6': 'SPI-6'}

# Insurance parameters
strikes = [.7, .75, .8, .85, .9]
studyears = [1948, 2017]
baselineyears = studyears
actuarialyear = 2018
productivity = 1
acres = 500
allocation = .5
difference = 1

# Loop through and get average national values for each strike and index
averages = []
for i in tqdm(indices, position=0):
    for s in strikes:
        indexname = indexnames[i]
        df = indexInsurance(arraydict[i],  # Index Path
                            grid,
                            premiums,
                            bases,
                            actuarialyear,  # Actuarial Year
                            studyears,  # Study years
                            baselineyears,  # Baseline
                            productivity,  # Productivity
                            s,  # Strike
                            acres,  # Acres
                            allocation,  # Allocation
                            scale=False,
                            plot=False)

        # Get Drought index stats
        indemnities = df[1]
        arrays = [r[1] for r in indemnities]
        dmean = np.nanmean(arrays)

        # add to list
        averages.append([indexname, s, dmean])

avdf = pd.DataFrame(averages)
avdf.columns = ['index', 'strike', 'meanpayment']
avdf.to_csv("G:/my drive/thesis/data/Index Project/" +
            "PRF_meanpayments_unscaled.csv")
avdf = pd.read_csv("G:/my drive/thesis/data/Index Project/" +
                   "PRF_meanpayments_unscaled.csv")

# Plot distribution
fig = plt.figure()
y = avdf['meanpayment']
xpos = [i for i in range(0, 12*5)]
width = .35
plot = plt.bar(xpos, y, width)
