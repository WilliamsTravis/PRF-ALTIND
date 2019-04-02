# -*- coding: utf-8 -*-
"""
Working with the rangeland vegetation simulator. 

This is new territory for me, I haven't had to work with raster data too
big for memory.


Created on Thu Feb  7 09:46:52 2019

@author: User
"""

import geopandas as gpd
import os
import warnings
os.chdir(r"c:\users\user\github\rangeland_vegetation_simulator")
from functions import *
warnings.filterwarnings('ignore')

# Set up data paths
shape_path = 'D:\\data\\shapefiles\\nad83'
prefab_path = "D:\\data\\RPMS_RangeProd_For_Posting\\tifs\\nad83\\counties"

# Clip counties - the whole thing is too big
all_counties = gpd.read_file(os.path.join(shape_path,
                                          'cb_2017_us_county_500k.shp'))
state_info = pd.read_csv(os.path.join(shape_path, 'us-state-ansi-fips.csv'))

# One county at a time. 'county_stateabbr'
counties = ['hardin_sd', 'sioux_ne', 'mckenzie_nd']

# Create individual county shapes
def getCounty(all_counties, county_string):
    county_name = county_string.split('_')[0].upper()
    state_abbr = county_string.split('_')[1]
    state_fips = state_info.st[state_info.stusps == state_abbr.upper()]
    county = gpd.all_counties[(all_counties. == all_counties.) & (all_counties. == all_counties.)]    


# Create array classes
classes = [RasterArrays(os.path.join(data, c), -32768.) for c in counties]

# get average with year
def getAverage(arrays):
    # The naming scheme is off sorry
    years = {i: 1983 + i for i in range(1, 36)}
    averages = {}
    for a in arrays.namedlist:
        location =  a[0][a[0].index('_')+1:]
        name = a[0][:a[0].index('_')]
        index = int("".join([s for s in name[-2:] if s.isnumeric()]))
        year = years[index]
        averages[year] = np.nanmean(a[1])
    df = pd.DataFrame([averages]).T
    df.columns = ['lbs_ac']
    df['county'] = location
    return df

# Merge however many counties
dfs = [getAverage(c) for c in classes]

# Create one dataframe
df = pd.concat(dfs)

# Add wheat production data
wheat = pd.read_csv('d:/data/yields/NASS_1949_2007_Wheat_NDSDNE.csv')
wheat = wheat['Year', 'County']
