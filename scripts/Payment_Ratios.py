# -*- coding: utf-8 -*-
"""
Created on Tue Apr 24 20:43:15 2018

@author: trwi0358
"""
import os
os.chdir('c:/users/user/github/PRF-ALTIND')
from functions import *
import warnings
warnings.filterwarnings("ignore")
noaapath = 'c:/users/user/github/data/indices/noaa_arrays.npz'

# Paths
paths = [
           'c:/users/user/github/data/indices/noaa_arrays.npz',
           'c:/users/user/github/data/indices/pdsi_arrays.npz',
           'c:/users/user/github/data/indices/pdsisc_arrays.npz',
           'c:/users/user/github/data/indices/pdsiz_arrays.npz',
           'c:/users/user/github/data/indices/spi1_arrays.npz',
           'c:/users/user/github/data/indices/spi2_arrays.npz',
           'c:/users/user/github/data/indices/spi3_arrays.npz',
           'c:/users/user/github/data/indices/spi6_arrays.npz',
           'c:/users/user/github/data/indices/spei1_arrays.npz',
           'c:/users/user/github/data/indices/spei2_arrays.npz',
           'c:/users/user/github/data/indices/spei3_arrays.npz',
           'c:/users/user/github/data/indices/spei6_arrays.npz',
           # 'c:/users/user/github/data/indices/eddi1_arrays.npz',
           # 'c:/users/user/github/data/indices/eddi2_arrays.npz',
           # 'c:/users/user/github/data/indices/eddi3_arrays.npz',
           # 'c:/users/user/github/data/indices/eddi6_arrays.npz'
]

# Just names
indices = ['noaa', 'pdsi', 'pdsisc', 'pdsiz', 'spi1', 'spi2', 'spi3', 'spi6',
           'spei1', 'spei2', 'spei3', 'spei6',
           # 'eddi1', 'eddi2', 'eddi3',
           # 'eddi6'
           ]

############### Argument Definitions ##########################################
actuarialyear = 2018
baselineyears = [1948, 2016]
studyears = [1948, 2016]
productivity = 1
strikes = [.7, .75, .8, .85, .9]
acres = 500
allocation = .5
difference = 0  # 0 = indemnities, 1 = net payouts, 2 = lossratios

# Actuarial rate paths -- to be simplified
grid = readRaster("C:/users/user/github/data/rma/nad83/prfgrid.tif",
                  1, -9999)[0]
premiums = npzIn('C:/USERS/USER/GITHUB/data/actuarial/premium_arrays_2018.npz',
                 'C:/USERS/USER/GITHUB/data/actuarial/premium_dates_2018.npz')

bases = npzIn('C:/USERS/USER/GITHUB/data/actuarial/base_arrays_2018.npz',
              'C:/USERS/USER/GITHUB/data/actuarial/base_dates_2018.npz')

############################ Normal NOAA Method ###############################
noaas = []
for i in range(len(strikes)):
    [producerpremiums, indemnities, frequencies, pcfs, nets,
     lossratios, meanppremium, meanindemnity, frequencysum,
     meanpcf, net, lossratio] = indexInsurance(noaapath,
                                               grid,
                                               premiums,
                                               bases,
                                               actuarialyear, 
                                               studyears,
                                               baselineyears,
                                               productivity,
                                               strikes[i],
                                               acres,
                                               allocation,
                                               difference,
                                               scale=True,
                                               plot=False) 
    payments = [n[1] for n in indemnities]
    noaas.append(np.nanmean(payments))

noaamean = np.mean(noaas)

####################### Test methods for drought indices ######################
# Step one, scalar one
levels = []
for i in range(len(paths) - 10):
    print(indices[i])
    # Step one, scalar one -- strike level ratios
    for s in range(len(strikes)):
        # Get payouts at this strike level
        [producerpremiums, indemnities, frequencies, pcfs, nets,
         lossratios, meanppremium, meanindemnity, frequencysum,
         meanpcf, net, lossratio] = indexInsurance(paths[i],
                                                   grid,
                                                   premiums,
                                                   bases,
                                                   actuarialyear,
                                                   studyears,
                                                   baselineyears,
                                                   productivity,
                                                   strikes[s],
                                                   acres,
                                                   allocation,
                                                   difference,
                                                   scale=False,
                                                   plot=False) 

        # Get just the payouts at this strike level
        payments = [n[1] for n in indemnities]

        # Get the ratio between payouts at this strike level and the rainfall one
        ratio = noaas[s] / np.nanmean(payments)

        # Add indexname, strike level and total ratio to the full levels set
        levels.append([indices[i], strikes[s], ratio])

scalars = pd.DataFrame(levels)
scalars.columns = ["index", "strike", "ratio"]

# Get the Strikewise ratios
scalars.to_csv("C:/users/user/github/data/Index_Adjustments/" +
               "index_ratios_test4.csv", index=False)

################### Step two, overall scaling #############################
ratios = []
for i in range(len(paths)-10):   
    print(indices[i])  

    # Step one, scalar one -- strike level ratios   
    allstrikes = []
    for s in range(len(strikes)):
        # Get payouts at this strike level
        [producerpremiums, indemnities, frequencies, pcfs, nets,
         lossratios, meanppremium, meanindemnity, frequencysum,
         meanpcf, net, lossratio] = indexInsurance(paths[i],
                                                   grid,
                                                   premiums,
                                                   bases,
                                                   actuarialyear, 
                                                   studyears,
                                                   baselineyears,
                                                   productivity,
                                                   strikes[s],
                                                   acres,
                                                   allocation,
                                                   difference,
                                                   scale=True,
                                                   plot=False) 

        # Get just the payouts at this strike level
        payments = [n[1] for n in indemnities]

        # Get the ratio between payouts at this strike level and the rainfall one
        allstrikes.append(np.nanmean(payments))

    # Find overall mean payment
    indexmean = np.mean(allstrikes) 
    overallratio = noaamean/indexmean
    ratios.append([indices[i], overallratio])

# Get the Strikewise ratios           
scalars1 = pd.read_csv("C:/users/user/github/data/Index_Adjustments/" +
                       "index_ratios_test2.csv")

scalars1.columns = ['index', 'strike', 'ratio1']

#Get the overall ratios
scalars2 = pd.DataFrame(ratios)
scalars2.columns = ['index', 'ratio2']

# Join and generate the composite ratio
scalars3 = pd.merge(scalars1, scalars2, on='index')
scalars3['ratio'] = scalars3['ratio1'] * scalars3['ratio2']


scalars3.to_csv("C:/users/user/github/data/Index_Adjustments/" +
                "index_ratios_test3.csv", index=False)
