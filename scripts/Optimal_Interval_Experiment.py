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

########################### Some Instruction ##################################
# For informing info and target info choose an index number for this list:
### 0: producerpremiums, 1: indemnities, 2: frequencies, 3: pcfs, 4: nets, 
#        5: lossratios, 6: meanppremium, 7: meanindemnity, 8: frequencysum,
#            9: meanpcf, 10: net, 11: lossratio

# Arguments:
#       rasterpath, targetinfo, targetarrayname, studyears, informinginfo, 
#                                   informingarrayname, informingyears,savename

rows = list()
paths = ['d:\\data\\droughtindices\\noaa\\nad83\\indexvalues\\',
         'd:\\data\\droughtindices\\palmer\\pdsi\\nad83\\',
         'd:\\data\\droughtindices\\palmer\\pdsisc\\nad83\\',
         'd:\\data\\droughtindices\\palmer\\pdsiz\\nad83\\',
         'd:\\data\\droughtindices\\spi\\nad83\\1month\\',
         'd:\\data\\droughtindices\\spi\\nad83\\2month\\',
         'd:\\data\\droughtindices\\spi\\nad83\\3month\\',
         'd:\\data\\droughtindices\\spi\\nad83\\6month\\',
         'd:\\data\\droughtindices\\spei\\nad83\\1month\\',
         'd:\\data\\droughtindices\\spei\\nad83\\2month\\',
         'd:\\data\\droughtindices\\spei\\nad83\\3month\\',
         'd:\\data\\droughtindices\\spei\\nad83\\6month\\']

indices = ["noaa", "pdsi", "pdsisc", "pdsiz", "spi1", "spi2", "spi3", "spi6",
           "spei1", "spei2", "spei3", "spei6"]
strikes = [.7, .75, .8, .85, .9]

for i in range(len(paths)):
    for s in range(len(strikes)):
        print("#####################################")
        print(paths[i])
        print("##################################")
        rows.append(optimalIntervalExperiment(rasterpath=paths[i],
                                              targetinfo=4,
                                              targetarrayname=indices[i],
                                              studyears=[2000, 2016], 
                                              informinginfo=3,
                                              informingarrayname="PCF",
                                              informingyears=[1948, 2016],
                                              strike=strikes[s],
                                              savename=indices[i]))

dfrm = pd.DataFrame(rows)
dfrm.to_csv("G:\\My Drive\\THESIS\\data\\Index Project\\PRFOptimals_nets.csv")