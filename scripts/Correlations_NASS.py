# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:10:35 2019

@author: Travis
"""
import inspect
import matplotlib.pyplot as plt
import numpy as np
import os
import pandas as pd
import sys
import warnings

# Set Working Directory to the root folder
path = os.path.dirname(sys.argv[0])
os.chdir(os.path.join(path, '..'))
from functions import prodCorr, im, agYear, indexHist
plt.style.use('fivethirtyeight')
styles = plt.style.library
warnings.filterwarnings('ignore')

# In[] This gives an idea of short and long term trends
hay_df_1984 = prodCorr('data/nass_hay_1959_2008.csv', 1984, 2008)
hay_df_1984.to_csv('data/correlations/hay_1984_2008_correlations.csv')
hay_df_1959 = prodCorr('data/nass_hay_1959_2008.csv', 1959, 2008)
hay_df_1959.to_csv('data/correlations/hay_1959_2008_correlations.csv')

alfalfa_1984 = prodCorr('data/nass_alfalfa_1959_2009.csv', 1984, 2009)
alfalfa_1984.to_csv('data/correlations/alfalfa_1984_2009_correlations.csv')
alfalfa_1959 = prodCorr('data/nass_alfalfa_1959_2009.csv', 1959, 2009)
alfalfa_1959.to_csv('data/correlations/alfalfa_1959_2009_correlations.csv')

wheat_df_1984 = prodCorr('data/nass_wheat_1929_2007.csv', 1984, 2007)
wheat_df_1984.to_csv('data/correlations/wheat_1984_2007_correlations.csv')

wheat_df_1959 = prodCorr('data/nass_wheat_1929_2007.csv', 1959, 2007)
wheat_df_1959.to_csv('data/correlations/wheat_1959_2007_correlations.csv')

wheat_df_1948 = prodCorr('data/nass_wheat_1929_2007.csv', 1948, 2007)
wheat_df_1948.to_csv('data/correlations/wheat_1948_2007_correlations.csv')
