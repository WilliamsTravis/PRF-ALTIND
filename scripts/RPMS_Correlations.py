# -*- coding: utf-8 -*-
"""
An Attempt to use the Rangeland Productivity Monitoring Service dataset from
Dr. Reeves at the Rocky Mountain Research Station to find correlations with
drought indices
Created on Sun Nov 18 20:22:08 2018

@author: User
"""
import os
import matplotlib.pyplot as plt
from scipy import signal
import warnings
warnings.filterwarnings('ignore')
os.chdir(r"c:\users\user\github\prf-altind")
from functions import *
os.chdir(r"D:\data\RPMS_RangeProd_For_Posting\tifs\nad83")


# In[] Helper functions
# Okay now, aggregate by year
def agYear(rasterarrays, bimonthly=True):
    '''
    Aggregate by year
    '''
    namedlist = rasterarrays.namedlist  # get the list
    if bimonthly:
        namedlist= adjustIntervals(namedlist)
    years = [str(y) for y in range(1984, 2018)]
    yearays = [[n[1] for n in namedlist if y in n[0]] for y in years]
    yearays = [np.nanmean(n, axis=0) for n in yearays]
    yearays = [[years[i], yearays[i]] for i in range(len(years))]
    return yearays


def cellCorr(indexrays, grassrays):
    '''cellwise correlations between to time series of arrays'''
    template = np.zeros((indexrays.shape[0], indexrays.shape[1]))
    for i in tqdm(range(indexrays.shape[0])):
        for j in range(indexrays.shape[1]):
            x = indexrays[i, j]
            y = grassrays[i, j]
            r = np.corrcoef(x, y)[1, 0]
            template[i, j] = r
    return template


# In[]
paths = [r'D:\data\droughtindices\noaa\nad83',
         r"D:\data\droughtindices\pdsi\nad83",
         r'D:\data\droughtindices\pdsisc\nad83',
         r'D:\data\droughtindices\pdsiz\nad83',
         r'D:\data\droughtindices\spei\nad83\1month',
         r'D:\data\droughtindices\spei\nad83\2month',
         r'D:\data\droughtindices\spei\nad83\3month',
         r'D:\data\droughtindices\spei\nad83\6month',
         r'D:\data\droughtindices\spei\nad83\1month',
         r'D:\data\droughtindices\spi\nad83\1month',
         r'D:\data\droughtindices\spi\nad83\2month',
         r'D:\data\droughtindices\spi\nad83\3month',
         r'D:\data\droughtindices\spi\nad83\6month']

# In[]
# Okay, now we can read them in
grasslands = RasterArrays(r"D:\data\RPMS_RangeProd_For_Posting\tifs\nad83",
                          -32768.)
mask, geom, proj = readRaster("D:/data/masks/mask25.tif", 1, -9999)

correlations = {}
meancorrs = {}
indexnames = []
for path in paths:
    print(path)
    # Okay now, get a drought index!
    indices = RasterArrays(path,
                           -9999.)

    # Get name for dataframe
    indexname = indices.namedlist[0][0][:-7]
    indexnames.append(indexname)

    # Aggregate by into bi-monthly bins, then by year
    indexyears = agYear(indices)

    # Ok, now fix these up
    grassyears = grasslands.namedlist
    grassyears = [[grassyears[i][0][-6:-2], grassyears[i][1]] for
                  i in range(len(grassyears))]
    grassyears = [n for n in grassyears if
                  int(n[0]) >= 1984 and int(n[0]) < 2017]
    indexyears = [n for n in indexyears if
                  int(n[0]) >= 1984 and int(n[0]) < 2017]
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

# Find maximum correlations like Dr Reeves did
positions = {i: k for i, k in enumerate(correlations.keys())}

# Create a function that ranks correlations at each cell
def rankCheck(correlations, mask):
    stack = [correlations[i] for i in indexnames]
    
    # Get rid of nans
    for i in stack:
        i[np.isnan(i)] = -9999

    def bestIndex(stack):
        def bestOne(lst):
            lst = list(lst)
            ts = np.copy(lst)
            ts.sort()
            value = ts[len(ts)-1]
            p1 = lst.index(value)
            return p1
        return np.apply_along_axis(bestOne, axis=0, arr=stack)

    def bestCorrelation(stack):
        def bestOne(lst):
            lst = list(lst)
            ts = np.copy(lst)
            ts.sort()
            value = ts[len(ts)-1]
            return value
        return np.apply_along_axis(bestOne, axis=0, arr=stack)

    x = bestIndex(stack)
    x = x*mask
    y = bestCorrelation(stack)
    y = y*mask
    y[y == -9999] = 0

    #Plot
    colors = ['#a6cee3', '#1f78b4', '#b2df8a', '#33a02c', '#fb9a99',
              '#e31a1c', '#fdbf6f', '#ff7f00', '#cab2d6', '#6a3d9a',
              '#ffff99', '#b15928', '#24c13e']
    labels = indexnames[::-1]

    fig = plt.figure()
    ax1 = plt.subplot2grid((2, 2), (0, 0), colspan=2)
    ax2 = plt.subplot2grid((2, 2), (1, 0), colspan=2)

    # Ranks
    ax1.imshow(x, cmap='Paired', label=labels)
    ax1.tick_params(which='both', right='off', left='off', bottom='off',
                    top='off', labelleft='off', labelbottom='off')
    ax1.set_title('Highest Correlating Index')
    legend_elements = [Patch(facecolor=colors[i],
                             label=labels[i]) for i in range(0,13)]
    ax1.legend(handles=legend_elements,
               loc="right",
               fontsize=15,
               bbox_to_anchor=(.98, .4))
    # divider1 = make_axes_locatable(ax1)
    # cax1 = divider1.append_axes("left", size="5%", pad=0.05)
    # cbar = plt.colorbar(im1, cax=cax1)
    # cbar.set_label('', rotation=90, size=10, labelpad=10,
    #                fontweight='bold')    
    # cbar.ax.yaxis.set_label_position('left')
    # cbar.ax.yaxis.set_ticks_position('left')
    
    
    ax2.imshow(y)
    ax2.tick_params(which='both', right='off', left='off', bottom='off',
                    top='off', labelleft='off', labelbottom='off')
    ax2.set_title('Highest Correlation')

    plt.imshow(x, cmap='Paired', label='Index')
    plt.title("Index With Highest Correlation")
    plt.legend(loc='lower right')
    
    
    
    
    plt.legend("Anything")
    return x, y

tops, highest = rankCheck(correlations, mask)
tops = tops*mask
highest = highest*mask

plt.imshow(tops, cmap='Paired')

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
