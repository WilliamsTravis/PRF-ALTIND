# -*- coding: utf-8 -*-
"""
In case I have to pull from AWS ever...this goes into the script around line 550 under the test == False condition. '

Created on Fri Jun  8 11:04:44 2018

@author: User
"""

averagepath = ("onlinedata/AY"
           + str(actuarialyear) + "/"+str(int(strike*100)) + "/"+str(returntype)
           +"/"+rasterpath+"/array.npz") # This is where it breaks, because there is no rasterpath at first

# Time-series path
timeseriespath = ("onlinedata/AY"
           + str(actuarialyear) + "/"+str(int(strike*100)) + "/"+str(returntype)
           +"/"+rasterpath+"/arrays.npz")

# Dates and Index name Path
datepath = ("onlinedata/AY"
           + str(actuarialyear) + "/"+str(int(strike*100)) + "/"+str(returntype)
           +"/"+rasterpath+"/dates.csv")

# Get with getNPY and getNPYs
array = getNPY(averagepath)
arrays = getNPYs(timeseriespath,datepath)
#        arrays.append(array) # Now the average is last, call it with [-1]
df = arrays