# -*- coding: utf-8 -*-
"""
An Attempt to use the Rangeland Productivity Monitoring Service dataset from
Dr. Reeves at the Rocky Mountain Research Station to find correlations with
drought indices
Created on Sun Nov 18 20:22:08 2018

@author: User
"""
import numpy as np
import matplotlib.pyplot as plt
import os
import pandas as pd
import sys
import warnings

# Set Working Directory to the root folder
path = os.path.dirname(sys.argv[0])
os.chdir(os.path.join(path, '..'))
from functions import agYear, cellCorr, RasterArrays, readRaster
warnings.filterwarnings('ignore')

# In[]
paths = [r'F:\data\droughtindices\noaa\nad83',
         r"F:\data\droughtindices\pdsi\nad83",
         r'F:\data\droughtindices\pdsisc\nad83',
         r'F:\data\droughtindices\pdsiz\nad83',
         r'F:\data\droughtindices\spei\nad83\1month',
         r'F:\data\droughtindices\spei\nad83\2month',
         r'F:\data\droughtindices\spei\nad83\3month',
         r'F:\data\droughtindices\spei\nad83\6month',
         r'F:\data\droughtindices\spi\nad83\1month',
         r'F:\data\droughtindices\spi\nad83\2month',
         r'F:\data\droughtindices\spi\nad83\3month',
         r'F:\data\droughtindices\spi\nad83\6month']

# In[]
# Okay, now we can read them in
grasslands = RasterArrays(r"F:\data\RPMS_RangeProd_For_Posting\tifs\nad83_lowres",
                          -32768.)
mask, geom, proj = readRaster("F:/data/masks/nad83/mask25.tif", 1, -9999)

correlations = {}
meancorrs = {}
indexnames = []
for path in paths:
    print(path)
    # Okay now, get a drought index!
    indices = RasterArrays(path, -9999.)

    # Get name for dataframe
    indexname = indices.namedlist[0][0][:-7]
    indexnames.append(indexname)

    # Aggregate by into bi-monthly bins, then by year
    if 'noaa' in path:
        indexyears = agYear(indices, bimonthly=True)
    else:
        indexyears = agYear(indices, bimonthly=True)

    # Ok, now fix these up
    grassyears = grasslands.namedlist
    grassyears = [[grassyears[i][0][-6:-2], grassyears[i][1]] for
                  i in range(len(grassyears))]
    grassyears = [n for n in grassyears if
                  int(n[0]) >= 2000 and int(n[0]) <= 2016]
    indexyears = [n for n in indexyears if
                  int(n[0]) >= 2000 and int(n[0]) <= 2016]
    indexrays = np.dstack([a[1] for a in indexyears])
    grassrays = np.dstack([a[1] for a in grassyears])

    corrs = cellCorr(indexrays, grassrays)
    meancorr = np.nanmean(corrs)
    meancorrs[indexname] = meancorr
    correlations[indexname] = corrs

# Create data frame of mean correlations
df = pd.DataFrame([meancorrs]).T
df.columns = ["Correlation"]
df = df.round(4)
df.sort_values("Correlation", ascending=False)
df.to_csv('data/correlations/rvs_1984_2016_correlations.csv')

# # Find maximum correlations like Dr Reeves did
# positions = {i: k for i, k in enumerate(correlations.keys())}

# # Create a function that ranks correlations at each cell
# def rankCheck(correlations, mask):
#     stack = [correlations[i] for i in indexnames]

#     # Get rid of nans
#     for i in stack:
#         i[np.isnan(i)] = -9999

#     def bestIndex(stack):
#         def bestOne(lst):
#             lst = list(lst)
#             ts = np.copy(lst)
#             ts.sort()
#             value = ts[len(ts)-1]
#             p1 = lst.index(value)
#             return p1
#         return np.apply_along_axis(bestOne, axis=0, arr=stack)

#     def bestCorrelation(stack):
#         def bestOne(lst):
#             lst = list(lst)
#             ts = np.copy(lst)
#             ts.sort()
#             value = ts[len(ts)-1]
#             return value
#         return np.apply_along_axis(bestOne, axis=0, arr=stack)

#     x = bestIndex(stack)
#     x = x*mask
#     y = bestCorrelation(stack)
#     y = y*mask
#     y[y == -9999] = 0

#     #Plot
#     colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
#               '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
#               '#ffff99', '#b15928', '#24c13e']
#     labels = indexnames[::-1]

#     fig = plt.figure()
#     ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
#     ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

#     # Ranks
#     ax1.imshow(x, cmap='Paired', label=labels)
#     ax1.tick_params(which='both', right='off', left='off', bottom='off',
#                     top='off', labelleft='off', labelbottom='off')
#     ax1.set_title('Highest Correlating Index')
#     legend_elements = [Patch(facecolor=colors[i],
#                              label=labels[i]) for i in range(0,13)]
#     ax1.legend(handles=legend_elements,
#                loc="right",
#                fontsize=15,
#                bbox_to_anchor=(.98, .4))
#     # divider1 = make_axes_locatable(ax1)
#     # cax1 = divider1.append_axes("left", size="5%", pad=0.05)
#     # cbar = plt.colorbar(im1, cax=cax1)
#     # cbar.set_label('', rotation=90, size=10, labelpad=10,
#     #                fontweight='bold')
#     # cbar.ax.yaxis.set_label_position('left')
#     # cbar.ax.yaxis.set_ticks_position('left')
#     ax2.imshow(y)
#     ax2.tick_params(which='both', right='off', left='off', bottom='off',
#                     top='off', labelleft='off', labelbottom='off')
#     ax2.set_title('Highest Correlation')

#     plt.imshow(x, cmap='Paired', label='Index')
#     plt.title("Index With Highest Correlation")
#     plt.legend(loc='lower right')
#     plt.legend("Anything")
#     return x, y

# tops, highest = rankCheck(correlations, mask)
# tops = tops*mask
# highest = highest*mask

# plt.imshow(tops, cmap='Paired')

# In[] For if you have to start over
# They aren't named with dates - but we know it starts in 1984
# files = os.listdir()

# # They have the numbers 1 through 35 to distinguish years, no leading zero
# for f in files:
#     print(len(f))
#     if len(f) == 13:
#         print(f)
#         os.rename(os.path.abspath(f),
#                   os.path.abspath(f)[:-5] + "0" + os.path.abspath(f)[-5:])

# # Create a dictionary to associate years - use '00' for month
# i_s = ['{:02}'.format(i) for i in range(1, 36)]
# y_s = [str(y) + '00' for y in range(1984, 2019)]
# t_s = dict(zip(i_s, y_s))

# # Now rename again
# files = os.listdir()
# for f in files:
#     path = os.path.abspath(f)
#     i = path[-6:-4]
#     t = t_s[i]
#     newpath = path.replace(i, '_' + t)
#     os.rename(path,
#               newpath)
