# -*- coding: utf-8 -*-
"""
Download the Unified Gauge-based Analysis of Precipitation Over CONUS and
    index it according to a specified baseline range. Also, create a long 
    form data frame of values for use in the R routines. 

Created on Fri Oct  5 14:24:50 2018

@author: User
"""
# In[]
import gdal
import os
import sys
import urllib
import warnings
os.chdir(r'C:\Users\user\Github')
sys.path.insert(0,'PRF-ALTIND')

from functions import adjustIntervals, normalize, readRaster

# In[] Download data - Monthly values of average daily rainfall in mm
url = "ftp://ftp.cdc.noaa.gov/Datasets/cpc_us_precip/precip.V1.0.mon.mean.nc"
ncpath =  "C:/Users/user/Github/data/rasters/precip.V1.0.mon.mean.nc"
tifpath =  "C:/Users/user/Github/data/rasters/precip.V1.0.mon.mean.tif"
filename = os.path.basename(url)

# Download .NC from the NOAA CPC site
urllib.request.urlretrieve(url, ncpath)

# In[] Get the RMA grid for cell reference and masking out great lakes
grid, geom, proj = readRaster("data/rasters/prfgrid.tif", 1, -9999)
mask = grid * 0 + 1 

raster = gdal.Open(ncpath)
arrays = [readRaster(tifpath, i,
                     -9999)[0][::-1]*mask for i in tqdm(range(1,
                          raster.RasterCount+1), position = 0)]

# Assign year and month to each - starts in Jan 1948
years = [str(y) for y in range(1948, 2019)]
months = [str(m).zfill(2) for m in range(1,13)]
dates = [[y + m for m in months] for y in years]
dates = [lst for sublst in dates for lst in sublst]
indexlist = [["NOAA_" + dates[i],arrays[i]] for i in range(len(arrays))]

# The RMA uses overlapping bi-monthly intervals. This applies that structure. 
indexlist = adjustIntervals(indexlist)
indexlist_raw = adjustIntervals(indexlist)

# The RMA then indexes each value against a baseline of average values between 
    # 1948 and two years prior to the current insurance year. This value is 
    # grouped by interval. The function creates a non-applicable warning: 
    # "Mean of Empty Slice".
with warnings.catch_warnings():
    warnings.simplefilter("ignore", category=RuntimeWarning)
    indexlist = normalize(indexlist, 1948, 2016)

# In[] # Function to build history for each site
def buildHistory(gridid, indexlist):
    loc = np.where(grid == gridid)
    rows = []
    years = [int(index[0][-6:-2]) for index in indexlist]
    for y in range(1948, max(years)+1):
        year_arrays = [index for index in indexlist if int(index[0][-6: -2]) == y]
        values = [float(array[1][loc]) for array in year_arrays]
        values.insert(0, y)
        rows.append(values)
    df = pd.DataFrame(rows)
    intervals = [str(i) for i in range(1, 12)]
    intervals.insert(0, "Year")
    df.columns = intervals
    df.index = df.Year
    df = df.drop(['Year'], axis = 1)
    df = round(df, 4)
    df['grid'] = np.repeat(gridid, df.shape[0])
    
    return df

# In[] Validate outputs
# Get a sample grid cell precipitation history in Boulder, CO - 24099
df = buildHistory(24099, indexlist)

# RMA's values for the same gridcell
ref_df = pd.read_csv("data/rma/HistoricalIndex-24099-2018-10-05.csv")
ref_df.columns = intervals
ref_df.index = ref_df.Year
ref_df = ref_df.drop(['Year'], axis = 1)
ref_df = ref_df.replace(' ', np.nan)

# Create flattened numpy arrays 
df = df.drop(['grid'], axis=1)
test = np.array(df)
ref = np.array(ref_df)[::-1] # It was backwards
ref = ref.astype(float)
test = test[:70] # one is a few months behind
ref = ref[:70]
test = test.flatten()
ref = ref.flatten()

# Find correlation
from scipy.stats.stats import pearsonr  
pearsonr(test, ref) # r2 = 0.9996

# In[] Create long-form data frame
def longForm(df, colname):
    gridid = df['grid'].unique()
    df = df.drop(['grid'], axis=1)
    df = df.stack()
    df = df.reset_index()
    df['grid'] = np.repeat(gridid, df.shape[0])
    df.columns = ['Year', 'interval', colname, 'grid']
    
    return df

# Apply buildHistory and longForm to each grid cell and merge it all
# get all gridids
gridids = np.unique(grid)
gridids = gridids[~np.isnan(gridids)]
gridids = gridids.astype(int)

# Build all histories in wide format, list of data frames
indexed_dfs = [buildHistory(gridids[i], indexlist) for i in tqdm(range(len(gridids)), position=0)] 
raw_dfs = [buildHistory(gridids[i], indexlist_raw) for i in tqdm(range(len(gridids)), position=0)] 

# Convert all histories to long format - list of data frames
indexed_ldfs = [longForm(indexed_dfs[i], 'index') for i in tqdm(range(len(indexed_dfs)), position=0)]
raw_ldfs = indexed_ldfs = [longForm(raw_dfs[i], 'realValue') for i in tqdm(range(len(raw_dfs)), position=0)]

# Merge each list of histories into single dataframes 
indexed_ldf = pd.concat(indexed_ldfs)
raw_ldf = pd.concat(raw_ldfs)
indexed_ldf['realValue'] = raw_ldf['realValue'] 

# Assign the realValue column to the indexed data frame
indexed_ldf['realValue'] = raw_ldf['realValue']

# Save to file
indexed_ldf.to_csv("data\\intervalNOAA_201810.csv")
