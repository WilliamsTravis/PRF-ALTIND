# -*- coding: utf-8 -*-
"""
An attempt to recreate appropriate premium rates for the drought indices

Created on Wed Aug 29 18:33:14 2018

@author: User
"""
import numpy as np
import os
import pandas as pd
import sys
import warnings
warnings.filterwarnings("ignore")
sys.path.insert(0, 'c:/Users/User/Github/PRF-ALTIND')
os.chdir('c:/Users/User/Github')
from functions import npzIn, indexInsurance, insuranceCalc, readRaster

# In[] Argument Definitions
grid, geom, proj = readRaster("data/rma/prfgrid.tif", 1, -9999)
actuarialyear = 2018
baselineyears = [1948, 2016]
studyears = [2000, 2017]
productivity = 1
strike = .8
acres = 500
allocation = .5

# In[] Testing...
# Get premium and base rates
premiums = npzIn('data/actuarial/premium_arrays_2018.npz',
                 'data/actuarial/premium_dates_2018.npz')
bases = npzIn('data/actuarial/base_arrays_2018.npz',
              'data/actuarial/base_dates_2018.npz')

# Get all of the rainfall indices
indexlist = npzIn("data/indices/noaa_arrays.npz",
                  "data/indices/noaa_dates.npz")

# In[] Get sample indemnities at 70% - which allocation?
# indexlist = "data/indices/noaa_arrays.npz"
df = indexInsurance(indexlist,  # Index Path
                    grid,
                    premiums,
                    bases,
                    2018,  # Actuarial Year
                    [1948, 2016],  # Study years
                    [1948, 2016],  # Baseline
                    1,  # Productivity
                    .7,  # Strike
                    1,  # Acres
                    1,  # Allocation
                    scale=True,
                    plot=False,
                    interval_restriction=True)
payouts = df[1]
ppremiums = df[0]
pcf = df[9]

# now take the premium rates at 70%
premiums_70 = [p[1] for p in premiums if p[0][7:9] == "70"]

# Payouts showed no pattern, take both premiums and pcfs in the 1st interval
intervals = ["%02d"%i for i in [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11]]
pcfs_70 = df[3]
# pcfs = [i[1] for i in pcfs_70 if i[0][-2:] == "07"]
pcf_means = [[p[1] for p in pcfs_70 if p[0][-2:] == i] for i in intervals]
pcf_means = [np.nanmean(p, axis=0) for p in pcf_means]
ratios = [premiums_70[i]/pcf_means[i] for i in range(len(pcf_means))]
# pcf = np.nanmean(pcfs, axis=0)
# ratio = p/pcf
# ratio_mean = np.nanmean(ratio)

# take a sample monthly series of ratios and pcf means at some location
sample_pcfs = [p[30, 30] for p in pcf_means]
sample_ratios = [r[30, 30] for r in ratios]
df = pd.DataFrame({'pcfs': sample_pcfs, 'ratios': sample_ratios})



# 1.19 seems right after the loading factors are incorporated. There were clear
# adjustments in some places but the replica premium rate map looks virtually
# the same.
replica = ratio_mean*pcf
difference = p - replica
np.nanmean(difference)
np.nanmax(difference)
np.nanmin(difference)
len(np.unique(difference))


# Create quick function to get the pcfs out of the indexInsurance function:
def getPCFs(index, strike):
    # Get inputs
    indexlist = npzIn("data/indices/" + index + "_arrays.npz",
                      "data/indices/" + index + "_dates.npz")
    grid = readRaster("data/rma/prfgrid.tif", 1, -9999)[0]
    premiums = npzIn('data/actuarial/premium_arrays_2018.npz',
                     'data/actuarial/premium_dates_2018.npz')
    bases = npzIn('data/actuarial/base_arrays_2018.npz',
                  'data/actuarial/base_dates_2018.npz')

    # Get sample returns
    df = indexInsurance(indexlist, grid, premiums, bases,
                        2018,  # Actuarial Year
                        [1948, 2017],  # Study years
                        [1948, 2016],  # Baseline
                        1,  # Productivity
                        strike,  # Strike
                        1,  # Acres
                        1,  # Allocation
                        scale=True, plot=False)
    pcfs = df[3]
    return([indexlist, pcfs])


# Let's create a function to calculate this for each strike-intervale
    # This will go into the main function to dynamically recalculate
    # premiums
def premiumLoading(indexlist, pcfs, premiums, bases,
                   strike=.7, interval=1):
    # We need strings and numeric strikes and intervals
    interval_string = "%02d" % interval
    strike_string = "%02d" % int(strike * 100)

    # Get the pcfs from the right interval, the strike is already incorporated
    pcf_specific = [p[1] for p in pcfs if p[0][-2:] == interval_string]
    pcf = np.nanmean(pcf_specific, axis=0)

    # Get the right RMA premium rates
    premium_specific = [p for p in premiums if p[0][-5:-3] == strike_string and
                        p[0][-2:] == interval_string][0][1]

    # Get the loading ratio and just use that for now. I can't find a pattern
    # loading_rates = pd.read_csv('PRF-ALTIND/loading_rates.csv')

    # get the ratio
    ratios = premium_specific/pcf
    ratio = np.nanmean(ratios)  # Here is the shortcut
    premium = ratio*pcf

    return premium_specific, premium, ratio, np.nanmean(pcf)


# Try a few
strike = .8
interval = 3
indexlist, pcfs = getPCFs("noaa", strike)
justpcfs = [p[1] for p in pcfs]
pcfmap = np.nanmean(justpcfs, axis=0)
original, new, ratio, pcfmean = premiumLoading(indexlist, pcfs, premiums,
                                               bases, strike, interval)
print(ratio)

# corr = np.correlate(new, original)
difference = original - new
# %varexp --imshow original
# %varexp --imshow new
# #%varexp --imshow difference
# %varexp --imshow pcfmap
# %varexp --imshow corr


# Let's get a chart
intervals = [i for i in range(1, 12)]
strikes = [.7, .75, .8, .85, .9]
ratio_list = []
for s in strikes:
    print(str(s))
    indexlist, pcfs = getPCFs("noaa", s)
    for i in intervals:
        print(str(i))
        original, new, ratio, pcfmean = premiumLoading(indexlist, pcfs,
                                                       premiums, bases, s, i)
        old_premium = np.nanmean(original)
        new_premium = np.nanmean(new)
        ratio_list.append([i, s, ratio, pcfmean, old_premium, new_premium])

df = pd.DataFrame(ratio_list)
df.columns = ["intervals", "strike", "loading_factor", "average_pcf",
              "old_premium", "new_premium"]
df.to_csv('PRF-ALTIND/loading_rates.csv')
