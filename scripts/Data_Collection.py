# -*- coding: utf-8 -*-
"""
Created on Thu Mar 22 12:47:52 2018

Collecting all the information from each index and set of parameters

@author: trwi0358
"""
import os  
os.chdir("C:/Users/user/github/PRF-ALTIND")
from functions import *
import warnings
warnings.filterwarnings("ignore") #This is temporary, toggle this on for presentation
mask = readRaster("e:\\data\\droughtindices\\masks\\nad83\\mask4.tif",1,-9999)[0]
grid = readRaster("e:\\data\\droughtindices\\rma\\nad83\\prfgrid.tif",1,-9999.)[0]

# Establish parameters lists.
# Index paths
indices = ['e:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\',
 'e:\\data\\droughtindices\\palmer\\pdsi\\nad83\\',
 'e:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\',
 'e:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
 'e:\\data\\droughtindices\\spi\\nad83\\1month\\',
 'e:\\data\\droughtindices\\spi\\nad83\\2month\\',
 'e:\\data\\droughtindices\\spi\\nad83\\3month\\',
 'e:\\data\\droughtindices\\spi\\nad83\\6month\\',
 'e:\\data\\droughtindices\\spei\\nad83\\1month\\',
 'e:\\data\\droughtindices\\spei\\nad83\\2month\\',
 'e:\\data\\droughtindices\\spei\\nad83\\3month\\',
 'e:\\data\\droughtindices\\spei\\nad83\\6month\\']

# Index names for the table
indexnames = {'e:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\': 'NOAA',
            'e:\\data\\droughtindices\\palmer\\pdsi\\nad83\\': 'PDSI',
          'e:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\': 'PDSIsc',
          'e:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\': 'PDSIz',
          'e:\\data\\droughtindices\\spi\\nad83\\1month\\':'SPI-1',
          'e:\\data\\droughtindices\\spi\\nad83\\2month\\':'SPI-2',
          'e:\\data\\droughtindices\\spi\\nad83\\3month\\':'SPI-3',
          'e:\\data\\droughtindices\\spi\\nad83\\6month\\':'SPI-6',
          'e:\\data\\droughtindices\\spei\\nad83\\1month\\': 'SPEI-1', 
          'e:\\data\\droughtindices\\spei\\nad83\\2month\\': 'SPEI-2', 
          'e:\\data\\droughtindices\\spei\\nad83\\3month\\': 'SPEI-3', 
          'e:\\data\\droughtindices\\spei\\nad83\\6month\\': 'SPEI-6'}

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
    prfdf.to_csv("data\\PRFIndex_specs.csv")
    print(i)
    indexlist = readRasters2(i,-9999)[0]
    indexlist = [[a[0],a[1]*mask] for a in indexlist]
    indexcov = covCellwise(indexlist) # what happened here? that c is probably from the covCellwise function, but *12? 
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
            prfdf = prfdf.append(rowdict,ignore_index=True)
            print(str(iteration) + " / " + str(totaliterations) +"  |  " + str(round(iteration/totaliterations,2)*100) + "%")


prfdf.columns = ['DI', 'AY', 'ICOV', 'S', 'TS', 'MAX($)',
       'MINP($)', 'MEDP($)', 'MEANP($)', 'PSD', 'MOPSD', 'MEANPCF',
       'SDPCF', 'MOSDPCF', 'MEANPF', 'MOSDPF']
prfdf.to_csv("C:\\Users\\user\\Github\\PRF-ALTIND\\data\\PRFIndex_specs.csv")
