# -*- coding: utf-8 -*-
"""
Pasture, Rangeland, and Forage Statistics

Created on Thu Nov 15 12:08:27 2018

@author: User
"""
import os
import pandas as pd
os.chdir('c:/users/user/github/data/rma/summary_of_business_reports/')
df = pd.read_csv('sob_master.csv')
df = df[['Commodity Year', 'State Abbreviation', 'County Name',
         'Commodity Name', 'Insurance Plan Abbreviation',
         'Coverage Level Percent', 'Liability Amount', 'Total Premium Amount',
         'Subsidy Amount', 'Indemnity Amount', 'Loss Ratio',
         'Endorsed Commodity']]
df['Commodity Name'] = df['Commodity Name'].apply(lambda x: x.lower())
df2 = df[df['Commodity Name'] == 'pasture,rangeland,forage']

# Total Subsidies
premiums = df2['Total Premium Amount'].dropna()
indemnities = df2['Indemnity Amount'].dropna()
subsidies = df2['Subsidy Amount'].dropna()
total_premiums = '{:,}'.format(sum(premiums))
total_indemnities = '{:,}'.format(sum(indemnities))
total_subsidies = '{:,}'.format(sum(subsidies))

# What if we grouped by commodity and ranked each.
df3 = df[df['Commodity Year'] >= 2007]
ranked_premiums = df3.groupby('Commodity Name')['Total Premium Amount'].sum()
ranked_indemnities = df3.groupby('Commodity Name')['Indemnity Amount'].sum()
ranked_subsidies = df3.groupby('Commodity Name')['Indemnity Amount'].sum()



