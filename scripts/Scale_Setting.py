# -*- coding: utf-8 -*-
"""
Created on Sat Jun  9 16:12:57 2018

@author: User
"""

############################# Set Scales by Signal ##########################################################################
import os  
os.chdir("C:/Users/user/github/PRF-ALTIND/")
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
strikes = [.7,.75,.8,.85,.9]

# Column names
columns = ["index",
           "actuarialyear",
           "strike",
           "max_indemnities",
           "min_indemnities",
           "max_frequencies",
           "min_frequencies",
           "max_pcfs",
           "min_pcfs",
           "max_nets",
           "min_nets",
           "max_lossratios",
           "min_lossratios"]
    
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

            # Return Order:
            # producerpremiums, indemnities, frequencies, pcfs, nets, lossratios, meanppremium, meanindemnity, 
            # frequencysum, meanpcf, net, lossratio
            maxpay = np.nanmax(data[7]) # INDEMNITY
            minpay = np.nanmin(data[7])
            maxfre = np.nanmax(data[8])
            minfre = np.nanmin(data[8])
            maxpcf = np.nanmax(data[9]) 
            minpcf = np.nanmin(data[9]) 
            maxnet = np.nanmax(data[10])
            minnet = np.nanmin(data[10])
            maxloss = np.nanmax(data[11])
            minloss = np.nanmin(data[11])
            
            # Create a row for the df! Pay attention to order
            print("Appending to dataframe...")
            row = [name,ay,s,maxpay,minpay,maxfre,minfre,maxpcf,minpcf,maxnet,minnet,maxloss,minloss]
            rowdict = dict(zip(columns,row))
            prfdf = prfdf.append(rowdict,ignore_index=True)
            print(str(iteration) + " / " + str(totaliterations) + "  |  " + str(round(iteration/totaliterations,2)*100) + "%")

prfdf.to_csv("data\\PRF_Y_Scales.csv",index = False)
