# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 12:47:52 2018
    
******* Careful This script is from the research folder that reads the rasters and not numpy arrays in! Change, first"***********
Collecting all the information from each index and set of parameters

@author: trwi0358
"""
import os  
os.chdir("C:/Users/user/github/PRF-ALTIND")
from functions import *
os.chdir("C:/Users/user/github/")

import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation

# Load mask 
with np.load("data\\mask.npz") as data:
    mask = data.f.mask
    data.close()
    
# Load RMA grid
with np.load("data\\prfgrid.npz") as data:
    grid = data.f.grid
    data.close()
    
# Establish parameters lists.
# Index paths
indices = ['data\\indices\\noaa_arrays.npz',
             'data\\indices\\pdsi_arrays.npz',    
             'data\\indices\\pdsisc_arrays.npz',
             'data\\indices\\pdsiz_arrays.npz',
             'data\\indices\\spi1_arrays.npz',
             'data\\indices\\spi2_arrays.npz',
             'data\\indices\\spi3_arrays.npz',
             'data\\indices\\spi6_arrays.npz',
             'data\\indices\\spei1_arrays.npz', 
             'data\\indices\\spei2_arrays.npz',
             'data\\indices\\spei3_arrays.npz',
             'data\\indices\\spei6_arrays.npz']

indexnames = {'data\\indices\\noaa_arrays.npz':'NOAA',
             'data\\indices\\pdsi_arrays.npz':'PDSI',    
             'data\\indices\\pdsisc_arrays.npz':'PDSIsc',
             'data\\indices\\pdsiz_arrays.npz':'PDSIz',
             'data\\indices\\spi1_arrays.npz':'SPI-1',
             'data\\indices\\spi2_arrays.npz':'SPI-2',
             'data\\indices\\spi3_arrays.npz':'SPI-3',
             'data\\indices\\spi6_arrays.npz':'SPI-6',
             'data\\indices\\spei1_arrays.npz':'SPEI-1', 
             'data\\indices\\spei2_arrays.npz':'SPEI-2',
             'data\\indices\\spei3_arrays.npz':'SPEI-3',
             'data\\indices\\spei6_arrays.npz':'SPEI-6'}

# Lists of other parameters
actuarialyear = [2017,2018]
studyears = [[1948,2017],[1968,2017],
             [1988,2017], [2008,2017]] 
#productivities = [.6,1,1.5] 
strikes = [.7,.75,.8,.85,.9]
#acres = [500,1000,1500] # Effects would be linear I think, might as well just in case.
allocation = .5 # This seems odd to vary to me, effects would be linear

# Column names
columns = ["Drought Index",
           "Actuarial Year",
           "Index COV",
           "Strike",
           "Temporal Scale",
           "Max Payment",
           "Minimum Payment",
           "Median Payment",
           "Mean Payment",
           "Payment SD",
           "Monthly Payment SD",
           "Mean PCF",
           "PCF SD",
           "Monthly PCF SD",
           "Mean Payout Frequency",
           "Monthly Payout Frequency SD"]
    
# Empty Data Frame
prfdf = pd.DataFrame(columns = columns)

# Iteratively call every parameter to generate prfdf rows. Could take a minute, 
    # This gives us 235,200 iterations :D
#prfdf = pd.read_csv("G:\\My Drive\\THESIS\\data\\Index Project\\PRFIndex_specs.csv")
iteration = len(prfdf.index)
totaliterations = len(indices)*len(actuarialyear)*len(strikes)

# I am taking out the other baseline years for now. It is meaningless for anything but the rainfall index
for i in indices:
    print(i)
    indexlist = readArrays(i)
    indexlist = [[a[0],a[1]*mask] for a in indexlist]
    indexcov = covCellwise(indexlist)
    name = indexnames.get(i)                            
    for ay in actuarialyear:
        print("Bundling Actuarials...Year: "+str(ay))
        if ay == 2017:
            actuarialpath = 'data\\actuarial\\2017\\rasters\\nad83\\'
        elif ay == 2018:
            actuarialpath = 'data\\actuarial\\2018\\rasters\\nad83\\'
        premiumpath = actuarialpath+'premiums\\'
        basepath = actuarialpath+'bases\\rates\\'

        premiums = readRasters2(premiumpath,-9999.)[0] #[0] because we can use the original geometry to write these to rasters.     
        bases = readRasters2(basepath,-9999.)[0]     
        for s in strikes:
            print("Choosing Strike Level..." + str(s))
            iteration += 1 
            print("Building Dataset...")
            data = indexInsurance(indexlist,grid, premiums, bases, ay, [2000,2017], [1948,2016], 1, 
                                   s, 500, .5,difference = 0, scale = True,plot = False)
            strike = s
            if "-" in name:
                scale = int(name[-1:])
            elif  "z" in name or name == 'NOAA':
                scale = 1
            else:
                scale = np.nan
                
                
            # Return Order:
            #producerpremiums, indemnities, frequencies, pcfs, nets, lossratios, meanppremium, meanindemnity, 
            #             frequencysum, meanpcf, net, lossratio
            maxpay = np.nanmax(data[7]) # INDEMNITY
            minpay = np.nanmin(data[7]) 
            medpay = np.nanmedian(data[7])
            meanpay = np.nanmean(data[7])
            paysd = np.nanstd(data[7]) # Standard Deviation in payments between locations
            monthpaysd = monthlySD(data[1]) # Standard Deviation between monthly cell-wise average payments
            meanpcf = np.nanmean(data[9]) 
            pcfsd = np.nanstd(data[9]) # Standard Deviation in PCFs bwetween locations
            monthpcfsd = monthlySD(data[3]) # Standard Deviation between monthly cell-wise average PCFs
            meanfre = np.nanmean(data[8])
            fresd = np.nanstd(data[8]) # Standard Deviation in payouts between locations
            monthfresd = monthlySD2(data[2]) # Standard Deviation between monthly cell-wise average payout frequencies
            
            # Create a row for the df! Pay attention to order
            print("Appending to dataframe...")
            row = [name,ay,indexcov,strike, scale,maxpay,minpay,medpay,meanpay,
                   paysd,monthpaysd,meanpcf,pcfsd,monthpcfsd,meanfre,monthfresd]
            rowdict = dict(zip(columns,row))
            prfdf.to_csv("data\\PRFIndex_specs.csv")
            prfdf = prfdf.append(rowdict,ignore_index=True)
            print(str(iteration) + " / " + str(totaliterations) +"  |  " + str(round(iteration/totaliterations,2)*100) + "%")

prfdf = pd.read_csv("C:\\Users\\user\\Github\\data\\PRFIndex_specs.csv")
prfdf.columns = ['DI', 'AY', 'ICOV', 'S', 'TS', 'MAX',
       'MINP', 'MEDP', 'MEANP', 'PSD', 'MOPSD', 'MEANPCF',
       'SDPCF', 'MOSDPCF', 'MEANPF', 'MOSDPF']
prfdf.to_csv("C:\\Users\\user\\Github\\data\\PRFIndex_specs.csv", index = False)
