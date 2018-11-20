# -*- coding: utf-8 -*-
"""
Convert Daily EDDI data into monthlies.

Created on Mon Nov 19 15:22:46 2018

@author: User
"""
import os
os.chdir('C:\\Users\\User\\github\\PRF-ALTIND')
from functions import *

# Split these up, not enough memory
files = glob.glob("D:/data/droughtindices/eddi/nad83/*tif")
rasterpath = 'D:/data/droughtindices/eddi/nad83'
files1 = [f for f in files if '01mn' in f]
files2 = [f for f in files if '02mn' in f]
files3 = [f for f in files if '03mn' in f]
files6 = [f for f in files if '06mn' in f]
file_sets = {1: files1, 2: files2, 3: files3, 6: files6}

def toMonthly(eddis):
    months = ['{:02d}'.format(i) for i in range(1, 13)]
    years = np.unique([eddis[i][0][-8:-4] for i in range(len(eddis))])
    year_groups = [[a for a in eddis if a[0][-8:-4] == y] for y in years]
    final_list = []
    for year in year_groups:
        month_groups = [[[a[0][:4] + a[0][11:12] + a[0][-9:-2], a[1]] for
                         a in year if a[0][-4:-2] == m] for m in months]
        month_groups = [m for m in month_groups if m]
        month_avgs = [[m[0][0], np.nanmean([day[1] for day in m], axis=0)] for
                       m in month_groups]
        final_list.append(month_avgs)
    final_list = [lst for sublst in final_list for lst in sublst]
    return final_list

for i in [1, 2, 3, 6]:
    savepath = 'D:/data/droughtindices/eddi/nad83/' + str(i) + "month"
    eddis, geom, proj = readRasters(file_sets[i])
    eddis = toMonthly(eddis)
    toRasters(eddis, savepath, geom, proj)
