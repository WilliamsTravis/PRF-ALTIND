# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:10:35 2019

@author: Travis
"""
import copulas
from copulas.univariate.gaussian import GaussianUnivariate
from copulas.multivariate.gaussian import GaussianMultivariate
import os
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import warnings
warnings.filterwarnings('ignore')
os.chdir('c:/users/user/github/prf-altind')
from functions import prodCorr, RasterArrays, im, agYear, indexHist


# In[] This gives an idea of short and long term trends
hay_df_1984 = prodCorr('data/nass_hay_1959_2008.csv', 1984, 2008)
hay_df_1984.to_csv('data/alfalfa_1984_correlations.csv')
hay_df_1959 = prodCorr('data/nass_hay_1959_2008.csv', 1959, 2008)
hay_df_1959.to_csv('data/alfalfa_1959_correlations.csv')

wheat_df_1984 = prodCorr('data/nass_wheat_1949_2007.csv', 1984, 2007)
wheat_df_1984.to_csv('data/wheat_1984_correlations.csv')
wheat_df_1949 = prodCorr('data/nass_wheat_1949_2007.csv', 1949, 2007)
wheat_df_1949.to_csv('data/wheat_1949_correlations.csv')

alfalfa_1984 = prodCorr('data/nass_alfalfa_1959_2009.csv', 1984, 2009)
alfalfa_1984.to_csv('data/alfalfa_1984_correlations.csv')
alfalfa_1959 = prodCorr('data/nass_alfalfa_1959_2009.csv', 1959, 2009)
alfalfa_1959.to_csv('data/alfalfa_1959_correlations.csv')

# Now experimenting with copulas - sampling a univariate distribution
iris = pd.read_csv('https://raw.githubusercontent.com/mwaskom/' +
                   'seaborn-data/master/iris.csv')
sl = iris['sepal_length']
plt.scatter(sl.index, sl)
gu = GaussianUnivariate()
gu.fit(sl)
print(gu)
gu.probability_density(5.85)
gu.cumulative_distribution(5.85)
gu.sample(10)

gc = GaussianMultivariate()
gc.fit(iris[['sepal_length', 'sepal_width', 'petal_length', 'petal_width']]) 
print(gc)


# A sample 3d array
hay = np.load('data/nass_hay_1959_2008.npy')
arrays = RasterArrays('f:/data/droughtindices/pdsi/nad83', -9999)
pdsi_years = agYear(arrays)
indexlist = np.array([[a[0], a[1]] for a in pdsi_years if
             int(a[0][-4:]) > 1958 and int(a[0][-4:]) < 2009])

years = [hay[i][0] for i in range(len(hay))]
hay = np.array([h[1] for h in hay])
pdsi = np.array([p[1] for p in indexlist])

# Sample location, one with data in both
hay_ts = hay[:, 30, 80]
pdsi_ts = pdsi[:, 30, 80]

styles = plt.style.library
plt.style.use('fivethirtyeight')
plt.scatter(years, hay_ts)
plt.scatter(years, pdsi_ts)
