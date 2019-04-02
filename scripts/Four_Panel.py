# -*- coding: utf-8 -*-
"""
A four panel sample of payouts at particular locations

Created on Wed May  2 20:26:19 2018

@author: trwi0358
"""
import os
import sys
import warnings
sys.path.insert(0, 'c:/users/user/github/PRF-ALTIND')
from functions import *
warnings.filterwarnings("ignore")
os.chdir('C:/Users/user/Github')

############## Get all of the rates ###############################
grid = readRaster("data/rma/prfgrid.tif",1,-9999)[0]
with np.load('data/actuarial/premium_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load('data/actuarial/premium_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
premiums = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

# Get all of the baserates
with np.load('data/actuarial/base_arrays_2018.npz') as data:
    arrays = data.f.arr_0
    data.close()
with np.load('data/actuarial/base_dates_2018.npz') as data:
    dates = data.f.arr_0
    data.close()
bases = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

############### Argument Definitions ##########################################
actuarialyear = 2018
baselineyears = [1948, 2016] 
studyears = [2000, 2016]  
productivity = 1 
strike = .8
acres = 500
allocation = .5

############################ Set the indices to compare #######################
index1 = "noaa"
# index = "spi6"
index = "spei6"
# index = "pdsiz"

############## Get the index values  ##########################################
noaalist = npzIn("data/indices/" + index1 + "_arrays.npz",
                 "data/indices/" + index1 + "_dates.npz")

indexlist = npzIn("data/indices/" + index + "_arrays.npz",
                  "data/indices/" + index + "_dates.npz")

# Function Call
# Return order:
#    producerpremiums, indemnities, frequencies, pcfs, nets, lossratios, 
#    meanppremium, meanindemnity, frequencysum, meanpcf, net, lossratio
noaas = indexInsurance(noaalist,grid,premiums,bases, actuarialyear, studyears, 
                       baselineyears, productivity, strike, acres, allocation,
                       scale=True, plot=False) 
indexes = indexInsurance(indexlist, grid,premiums,bases,actuarialyear,
                         studyears, baselineyears, productivity, strike, acres,
                         allocation, scale=True, plot=False) 

############################## Time Series ####################################
if len(noaas[0]) < len(indexes[0]):
    shorter = noaas
else:
    shorter = indexes
ndates = [a[0][-6:-2] + "-" + a[0][-2:] for a in shorter[0]]

# get indemnities  or nets
pcfs_n = noaas[1]
pcfs_n = [a[1] for a in pcfs_n[:len(ndates)]]
pcfs_s = indexes[1]
pcfs_s = [a[1] for a in pcfs_s[:len(ndates)]]

# Billings, MT 
grid_loc = np.where(grid == 30986)
mt_n = [float(pcf[grid_loc]) for pcf in pcfs_n]
mt_s = [float(pcf[grid_loc]) for pcf in pcfs_s]

# Coleman, TX 
grid_loc = np.where(grid == 14223)
tx_n = [float(pcf[grid_loc]) for pcf in pcfs_n]
tx_s = [float(pcf[grid_loc]) for pcf in pcfs_s]

# Kearney, NE 
grid_loc = np.where(grid == 24724)
ne_n = [float(pcf[grid_loc]) for pcf in pcfs_n]
ne_s = [float(pcf[grid_loc]) for pcf in pcfs_s]

# Oklahoma
grid_loc = np.where(grid == 18430)
ok_n = [float(pcf[grid_loc]) for pcf in pcfs_n]
ok_s = [float(pcf[grid_loc]) for pcf in pcfs_s]

# Now find a place with little difference in overall payment potential 
# Make sure it's a cattle ranching place, say Texas or Oklahoma, for relevance
diff = abs(np.nansum(pcfs_n,axis = 0) - np.nansum(pcfs_s,axis = 0))
diff[diff > 1000] = np.nan
paylist = indexes[1]
def seasonBar(diff, paylist):
    i = int(float(input("enter iterator: ")))
    # Create the arrays 
    arrays = [a[1] for a in paylist]
    names = [a[0] for a in paylist]
    index = names[0][:-7]
    dates = [n[-6:] for n in names]
    
    # choose a location from the minimu, difference array
    mins = list(diff[diff>0])
    mins.sort()
    loc = np.where(diff == mins[i])
    gridid = grid[loc]
    
    # Create the data frame
    ys = [float(array[loc]) for array in arrays]
    intervals = [format(int(interval),'02d') for interval in range(1,12)]
    months = {1:'Jan-Feb',
              2:'Feb-Mar',
              3:'Mar-Apr',
              4:'Apr-May',
              5:'May-Jun',
              6:'Jun-Jul',
              7:'Jul-Aug',
              8:'Aug-Sep',
              9:'Sep-Oct',
              10:'Oct-Nov',
              11:'Nov-Dec'}
    intervalist = [[y[1][loc] for y in paylist if y[0][-2:] ==  interval] for
                   interval in intervals]
    averages =  tuple(np.asarray([np.nanmean(sublist) for
                                  sublist in intervalist]))

    # Create the Time Series
    xs = []
    for d in range(len(dates)):
        if d % 10 == 0:
            xs.append(str(dates[d]))
        else:
            xs.append("")

    # Create the Monthly Trends
    x2s = [months.get(interval) for interval in range(1, 12)]
    y2s = averages

    # Create Bar Graphs of time series and seasonal trends.
    figure = plt.figure()
    manager = plt.get_current_fig_manager()
    manager.window.setGeometry(10, 1500, 3800, 500)
    figure.suptitle(str(int(gridid))+ "\n", fontsize = 25)
    ax1 = plt.subplot2grid((1, 4), (0, 0), colspan = 3)
    ax2 = plt.subplot2grid((1, 4), (0, 3), colspan = 1)  
    ax1.bar(dates,ys)
    ax1.set_xticklabels(xs)
    ax1.set_title("Time Series")
    ax2.bar(x2s,y2s)
    ax2.set_title("Trends")
    ax2.set_ylim([0, 2000])
    figure.autofmt_xdate()

# Check these for seasonal trends
#seasonBar(diff,paylist)

#  Sweetwater County, Wyoming
grid_loc = np.where(grid == 26816)
wy_n = [float(pcf[grid_loc]) for pcf in pcfs_n]
wy_s = [float(pcf[grid_loc]) for pcf in pcfs_s]

################################# Make Data Frame #############################
df_n = pd.DataFrame([mt_n, tx_n,ne_n,ok_n])
df_n.columns = ndates
df_n['index'] = list(np.repeat("rainfall", 4))

df_s = pd.DataFrame([mt_s, tx_s,ne_s,ok_s])
df_s.columns = ndates
df_s['index'] = list(np.repeat(index, 4))

locations = np.tile(["MT","TX","NE","OK"],2)

df = pd.concat([df_n, df_s])
df['location'] = locations
df = df.reset_index()

df.to_csv(r"G:\My Drive\THESIS\data\Index Project\fourpanel_" + index.upper() +
          "_" + str(round(strike*100)) + ".csv")
