# -*- coding: utf-8 -*-
"""
This will loop through all combinations of paramters for the online model and
    save the average outputs as npz and save the payment time series for the
    time series graph

Created on Mon May  7 20:29:57 2018

@author: trwi0358
"""

import os
import sys
import warnings
os.chdir('c:/users/user/github/PRF-ALTIND')
from functions import *
warnings.filterwarnings("ignore")
os.chdir('C:/Users/user/Github')

# In[]
# mask, geom, proj = readRaster("e:\\data\\droughtindices\\masks\\nad83\\mask4.tif",1,-9999)
homepath = ''
grid = readRaster("data/rma/prfgrid.tif", 1, -9999)[0]
########################## Load Index Arrays #################################################################################
# Actuarial Rates
indices = ['noaa', 'pdsi', 'pdsisc', 'pdsiz', 'spi1', 'spi2', 'spi3',
           'spi6', 'spei1', 'spei2', 'spei3', 'spei6', 'eddi1', 'eddi2',
           'eddi3', 'eddi6']


# Actuarial rate paths -- to be simplified
premiums2017 = npzIn('data/actuarial/premium_arrays_2017.npz',
                     'data/actuarial/premium_dates_2017.npz')
premiums2018= npzIn('data/actuarial/premium_arrays_2018.npz',
                    'data/actuarial/premium_dates_2018.npz')

bases2017 = npzIn('data/actuarial/base_arrays_2017.npz',
                  'data/actuarial/base_dates_2017.npz')
bases2018 = npzIn('data/actuarial/base_arrays_2018.npz',
                  'data/actuarial/base_dates_2018.npz')

# Indices
arraydict = []
for i in tqdm(range(len(indices)), position=0):
    timeseries = npzIn("data/indices/" + indices[i] + "_arrays.npz",
                       "data/indices/" + indices[i] + "_dates.npz")
    arraydict.append(timeseries)

arraydict = {indices[i]:arraydict[i] for i in range(len(indices))}
gc.collect(2)

# Strike level
strikes = [.7, .75, .8, .85, .9]

# Info Type
infotype = [i for i in range(6, 12)]

# Actuarial Year
actuarialyears = [2017, 2018]

# Number of Acres....uh oh...better make this discrete
acres = 500

# In[] Switching to the D Drive, not enough space on my computer
os.chdir("d:/data/prf_altind/limited")

# rasterpath, actuarialyear, studyears, baselineyears, productivity, strike,
# acres, allocation,difference = 0, scale = True, plot = True
for p in range(len(indices)):
    print(indices[p])
    indexlist = arraydict.get(indices[p])
    for ay in actuarialyears:
        if ay == 2017:
            bases = bases2017
            premiums = premiums2017
        elif ay == 2018:
            bases = bases2018
            premiums = premiums2018            
        print(ay)
        for s in strikes:
            print(s)
            df = indexInsurance(indexlist,  # Index Path
                                grid,
                                premiums,
                                bases,
                                ay,  # Actuarial Year
                                [1980, 2018],  # Study years
                                [1948, 2016],  # Baseline
                                1,  # Productivity
                                s,  # Strike
                                500,  # Acres
                                .5,  # Allocation
                                scale=True,
                                plot=False)

            #  returns = producerpremiums,indemnities,frequencies,pcfs,nets, lossratios
            # ,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
            # Premiums
            array = df[6]
            np.savez_compressed(
                     "data\\payouts\\AY" + str(ay) + "\\" + str(int(s*100)) +
                     "\\premiums\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[0]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\premiums\\"+indices[p]+"\\dates.csv", index = False)

            # Indemnities
            array = df[7]
            np.savez_compressed( # Save this as an array, too 
                     "data\\payouts\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[1]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\indemnities\\"+indices[p]+"\\dates.csv", index = False)            

            # frequencies
            array = df[8]
            np.savez_compressed( # Save this as an array, too 
                     "data\\payouts\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[2]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\frequencies\\"+indices[p]+"\\dates.csv", index = False)

            # pcfs
            array = df[9]
            np.savez_compressed( # Save this as an array, too 
                     "data\\payouts\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[3]            
            dates = pd.DataFrame([a[0] for a in arrays]) # Also, just to keep things solid, lets save the dates. 
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\pcfs\\"+indices[p]+"\\dates.csv", index = False)

            # nets
            array = df[10]
            np.savez_compressed( # Save this as an array, too 
                     "data\\payouts\\AY"
                     +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\array",array)
            
            # Instead of Pickling use a numpy specific file 
            arrays = df[4]            
            dates = pd.DataFrame([a[0] for a in arrays])
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY"
                         +str(ay)+"\\"+str(int(s*100))+"\\nets\\"+indices[p]+"\\dates.csv", index = False)

            # lossratios
            array = df[11]
            np.savez_compressed(  # Save this as an array, too 
                     "data\\payouts\\AY" + str(ay) + "\\" + str(int(s*100)) +
                     "\\lossratios\\" + indices[p] + "\\array",array)

            # Instead of Pickling use a numpy specific file 
            arrays = df[5]            
            dates = pd.DataFrame([a[0] for a in arrays])
            dates.columns = ["dates"]
            jarrays = np.array([a[1] for a in arrays])
            np.savez_compressed("data\\payouts\\AY" + str(ay) + "\\" +
                                str(int(s*100)) + "\\lossratios\\" +
                                indices[p] + "\\arrays", jarrays)
            dates.to_csv("data\\payouts\\AY" + str(ay) + "\\" +
                         str(int(s*100)) + "\\lossratios\\" + indices[p] +
                         "\\dates.csv", index = False)