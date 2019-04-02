"""
Created on Fri Nov 17 22:19:03 2017
This script allows you to change parameters and call the functions. The working
directory is set in the functions script while this is being tinkered with.
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

# In[] Index Lists
indices = ["noaa", "pdsi", "pdsisc", "pdsiz", "spi1", "spi2", "spi3", "spi6",
           "spei1", "spei2", "spei3", "spei6"]
arraylist = []
for i in tqdm(range(len(indices)), position=0):
    timeseries = npzIn("data/indices/" + indices[i] + "_arrays.npz",
                       "data/indices/" + indices[i] + "_dates.npz")
    arraylist.append(timeseries)
arraydict = {indices[i]: arraylist[i] for i in range(len(indices))}

strikes = [.7, .75, .8, .85, .9]
seriesdict = {0: 'premiums', 1: 'indemnities', 2: 'frequencies', 3: 'pcfs',
              4: 'nets', 5: 'lossratios'}

rows = list()
for i in indices:
    for s in strikes:
        print("#####################################")
        print(i)
        print("#####################################")
        rows.append(optimalIntervalExperiment(indexlist=arraydict[i],
                                              targetinfo=4,
                                              targetarrayname=i,
                                              studyears=[2000, 2016],
                                              informinginfo=3,
                                              informingarrayname="PCF",
                                              informingyears=[1948, 2016],
                                              strike=s,
                                              savename=i,
                                              plot=False,
                                              save=True,
                                              interval_restriction=False))

dfrm = pd.DataFrame(rows)
dfrm.to_csv("G:\\My Drive\\THESIS\\data\\Index Project\\PRFOptimals_nets.csv")