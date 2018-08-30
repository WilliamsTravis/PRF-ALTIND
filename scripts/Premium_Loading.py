# -*- coding: utf-8 -*-
"""
An attempt to recreate appropriate premium rates for the drought indices

Created on Wed Aug 29 18:33:14 2018

@author: User
"""

runfile('C:/Users/user/Github/PRF-ALTIND/functions.py', wdir='C:/Users/user/Github/PRF-ALTIND')
os.chdir('c:/Users/User/Github/data')
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
grid = readRaster("prfgrid.tif",1,-9999)[0]

############### Argument Definitions ##########################################
actuarialyear = 2018
baselineyears = [1948,2016] 
studyears = [2000,2017]  
productivity = 1 
strike = .8
acres = 500
allocation = .5

############### Testing... ####################################################
# Get all of the premium rates
with np.load('actuarial/premium_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load('actuarial/premium_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
premiums = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

# Get all of the baserates
with np.load('actuarial/base_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load('actuarial/base_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
bases = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

# Get all of the rainfall indices 
with np.load("indices/noaa_arrays.npz") as data:
    arrays = data.f.arr_0
    data.close()
with np.load("indices/noaa_dates.npz") as data:
    names = data.f.arr_0
    data.close()
indexlist = [[str(names[y]),arrays[y]] for y in range(len(arrays))]

# Get sample indemnities at 70% - which allocation?
df = indexInsurance(indexlist, # Index Path
                    grid,
                    premiums,
                    bases,
                    2018, # Actuarial Year
                    [1948,2017], # Study years
                    [1948,2016], # Baseline
                    1, # Productivity
                    .7, # Strike
                    1, # Acres
                    1, # Allocation
                    scale = True,
                    plot = False)
payouts = df[1]

# now take the premium rates at 70%
premiums_70 = [p for p in premiums if p[0][7:9] == "70"]

# Payouts showed no pattern, let's take both premiums and pcfs in the first interval
p = premiums_70[0][1] # p for premium
pcfs = df[3]
pcfs = [i[1] for i in pcfs if i[0][-2:] == "01"]
pcf = np.nanmean(pcfs,axis = 0)
ratio = p/pcf
np.nanmean(ratio)

# 1.19 seems right after the loading factors are incorporated. There were clear adjustments in some places
# but the replica premium rate map looks virtually the same. 
replica = 1.19*pcf
difference = p - replica
np.nanmean(difference)
np.nanmax(difference)
np.nanmin(difference)
len(np.unique(difference))

# Create quick function to get the pcfs out of the indexInsurance function:
def getPCFs(index,strike):
    # Get all of the  indices 
    with np.load("indices/"+index+"_arrays.npz") as data:
        arrays = data.f.arr_0
        data.close()
    with np.load("indices/"+index+"_dates.npz") as data:
        names = data.f.arr_0
        data.close()
    indexlist = [[str(names[y]),arrays[y]] for y in range(len(arrays))]
    
    # Get sample returns
    df = indexInsurance(indexlist, # Index Path
                        grid,
                        premiums,
                        bases,
                        2018, # Actuarial Year
                        [1948,2017], # Study years
                        [1948,2016], # Baseline
                        1, # Productivity
                        strike, # Strike
                        1, # Acres
                        1, # Allocation
                        scale = True,
                        plot = False)
    pcfs = df[3]
    return([indexlist,pcfs])


# Let's create a function to calculate this for each strike-intervale
    # This will go into the main function to dynamically recalculate 
    # premiums
def premiumLoading(indexlist,pcfs,premiums,bases,strike = .7, interval = 1):
    # We need strings and numeric strikes and intervals
    interval_string = "%02d"%interval
    strike_string = "%02d"%int(strike*100)
    
    # Get the pcfs from the right interval, the strike is already incorporated
    pcf_specific = [p[1] for p in pcfs if p[0][-2:] == interval_string]
    pcf = np.nanmean(pcf_specific,axis = 0)

    # Get the right RMA premium rates
    premium_specific = [p for p in premiums if p[0][-5:-3] == strike_string and p[0][-2:] == interval_string][0][1]

    # get the ratio
    ratios = premium_specific/pcf
    ratio = np.nanmean(ratios)    
    
    premium = ratio*pcf
    return premium_specific,premium


# Try a few
strike = .85
interval = 11
indexlist,pcfs = getPCFs("noaa",.8)
original,new = premiumLoading(indexlist,pcfs,premiums,bases,strike, interval)
difference = original - new
#%varexp --imshow original
#%varexp --imshow new
#%varexp --imshow difference
