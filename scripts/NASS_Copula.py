# -*- coding: utf-8 -*-
"""
Created on Tue Apr  2 11:10:35 2019

@author: Travis
"""

import pandas as pd

alfalfa = pd.read_csv('data/nass_alfalfa_1959_2009.csv')

states = pd.unique(alfalfa['State'])
counties = pd.unique(alfalfa['County'])

hay = pd.read_csv('data/nass_hay_1959_2008.csv')

states = pd.unique(hay['State'])
counties = pd.unique(hay['County'])

wisconsin = pd.read_csv('data/nass_hay_haylage_wisconsin_1994_2008.csv')
