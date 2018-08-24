# -*- coding: utf-8 -*-
"""
Take a large shapefile of cities and associate them with RMA grid IDs. This city file has some gaps in the West, 
    but should be a good standin for now.

Created on Wed Aug 22 17:04:44 2018

@author: User
"""

import geopandas as gpd
import os
import rasterio
from rasterio.mask import mask

#
# Read in the city shapefile
cities = gpd.read_file("c:/users/user/github/data/shapefiles/citiesx020.shp")

# Extract geometries in geojson format
cities = [[cities[i].NAME, for i in range(len(cities))]

# Unpack the coordiates into a list of dictionaries
from shapely.geometry import mapping
geoms = [mapping(geoms[i]) for i in range(len(geoms))]
#geoms = [mapping(geoms[0])]

# Load the raster and extract?
with rasterio.open("C:/users/user/github/data/prfgrid.tif") as data:
    overlay, transform = sample(data, geoms, crop =True)

import numpy as np
where = np.where(overlay != 0) 
city = np.extract(data != 0, data)

from rasterio import Affine # or from affine import Affine
t1 = transform * Affine.translation(0.5, 0.5) # reference the pixel centre
rc2xy = lambda r, c: (c, r) * t1  

d = gpd.GeoDataFrame({'col':col,'row':row,'city':city})

# coordinate transformation
d['x'] = d.apply(lambda row: rc2xy(row.row,row.col)[0], axis=1)
d['y'] = d.apply(lambda row: rc2xy(row.row,row.col)[1], axis=1)
# geometry
from shapely.geometry import Point
d['geometry'] =d.apply(lambda row: Point(row['x'], row['y']), axis=1)
# first 2 points
d.head(2)

# save to a shapefile
d.to_file('result.shp', driver='ESRI Shapefile')