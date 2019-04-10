# -*- coding: utf-8 -*-
"""
An interface for NASS API

Created on Mon Apr  8 12:20:13 2019

@author: User
"""

from matplotlib import pyplot as plt
import numpy as np
import os
import pandas as pd
import requests
os.chdir('C:/users/user/github/prf-altind/')

class NASS_API:
    '''
    This class just builds queries and returns data from the NASS API.  
    The structure of the query is based on what, when, and where questions.
    You can also filter the results by appending operators to the parameter.
    The three types of queries are separated into the methods
    get_parameter_options, get_query_count, and get_query.
    
    They only allow requests with less than 50,000 entries, which is rather
    small. For the whole thing go here!:

        ftp://ftp.nass.usda.gov/quickstats
    
    To use:
        1) Create an api object: 
           
            api = NASS_API(<your nass key as a string>)

        2) Get a list of available parameters with api.all_parameters

        3) Get a list of the definitions of these parameters using
            api.what_parameters, api.where_parameters, and api.when_parameters

        4) Get a list of input options for any one parameter using
            api.get_parameter_options('parameter')

        5) Build a query as a list of strings like this:

            ['<parameter1>=<input1>', '<parameter2>=<input2>', ...]

        6) Filter each query by appending an operator to each string element:

            '<parameter><operator>=<input>'

        7) For count use the query list as the argument in api.get_query_count:

            data = api.get_query_count(query)

        8) For the data itself use the query list in api.get_query:

            data = api.get_query(query)

        9) Examples:
            Retrieve weekly corn yields from Montana since 1980:
            
                query = ['state_name=MONTANA', 'commodity_desc=CORN',
                         'year__GE=1980', 'freq_desc=WEEKLY']
                data = api.get_query(query)
    
    '''
    def __init__(self, key='DCC6BBF9-EC39-3DD9-B3F5-AC642B764E99'):
        self.key = key
        self.sample_query = ('http://quickstats.nass.usda.gov/api/api_GET/?' +
                             'key=<key>&commodity_desc=CORN&' +
                             'year__GE=2010&state_alpha=VA ')
        self.url = 'http://quickstats.nass.usda.gov/api'
        self.website = 'https://quickstats.nass.usda.gov/api'
        self.what_parameters = pd.read_table('data/nass_api_params_what.txt',
                                             sep='|', index_col=False)
        self.when_paramaters = pd.read_table('data/nass_api_params_when.txt',
                                             sep='|')
        self.where_parameters = pd.read_table('data/nass_api_params_where.txt',
                                             sep='|')
        self.all_parameters = ['source_desc', 'sector_desc', 'group_desc',
                               'commodity_desc', 'class_desc',
                               'prodn_practice_desc', 'util_practice_desc',
                               'statisticcat_desc', 'unit_desc', 'short_desc',
                               'domain_desc', 'domaincat_desc', 'value',
                               'CV %', 'year', 'freq_desc', 'begin_code',
                               'end_code', 'reference_period_desc',
                               'week_ending', 'load_time', 'agg_level_desc',
                               'state_ansi', 'state_fips_code', 'state_alpha',
                               'state_name', 'asd_code', 'asd_desc',
                               'county_ansi', 'county_code', 'county_name',
                               'region_desc', 'zip_5', 'watershed_code',
                               'watershed_desc', 'congr_district_code',
                               'country_code',  'country_name',
                               'location_desc']
    
    def print_operators(self):
        print("__LE = <= \n__LT = <\n__GT = >\n__GE = >= \n" +
              "__LIKE = like\n__NOT_LIKE = not like\n__NE = not equal ")

    def get_parameter_options(self, parameter):
        '''
        Here I want to list an example entry for each parameter, so we don't
        have to go to the quick (not quick) stats tool to get formatting right
        '''
        base = '/'.join([self.url, 'get_param_values', '?key=']) + self.key
        request = '&'.join([base, 'param=' + parameter])
        r = requests.get(request)
        data = r.json()
        options = data[parameter]
        return options
            
    def get_query_count(self, query):
        base = '/'.join([self.url, 'get_counts', '?key=']) + self.key
        query = '&'.join(query)
        request = '&'.join([base, query])
        r = requests.get(request)
        data = r.json()
        number = int(data['count'])
        return number

    def get_query(self, query):
        base = '/'.join([self.url, 'api_GET', '?key=']) + self.key
        query = '&'.join(query)
        request = '&'.join([base, query])
        r = requests.get(request)
        data = r.json()
        try:
            df = pd.DataFrame(data['data']) 
        except:
            return data
        return df

    def query_to_csv(self, query, filename):
        base = '/'.join([self.url, 'api_GET', '?key=']) + self.key
        query = '&'.join(query)
        request = '&'.join([base, query, 'format=csv'])
        r = requests.get(request)
        data = r.json()
        try:
            df = pd.DataFrame(data['data']) 
        except:
            return data
        return df


api = NASS_API()
query = ['state_name=MONTANA', 'commodity_desc=CORN',
         'year__GE=1980', 'freq_desc=WEEKLY']
query = ['commodity=HAY', 'freq_desc=ANNUAL', 'state_name=COLORADO',
         'year__GE=2015']
api.get_query_count(query)
data = api.get_query(query)