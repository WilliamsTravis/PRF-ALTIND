# -*- coding: utf-8 -*-
"""
The Drought Index Insurance Analysis Laboratory (DIIAL)
    
    This simulates insurance payouts and other outputs from the Pasture,
    Rangeland, and Forage program according to various drought indices. Rather,
    it visualizes premade simulations.


Things to do:
    1) Calculate insurance outputs on the fly. With a stronger machine and
       multiple CPUs this should be possible without much lag. 
    2) After #1 allow for average values within a user-defined area.
    3) Add a data download option.

@author: Travis Williams
"""

# In[] Set up environment
import copy
import dash
from dash.dependencies import Input, Output, State
from dash.exceptions import PreventUpdate
import dash_core_components as dcc
import dash_table_experiments as dte
import dash_html_components as html
from flask_caching import Cache
import gc
from inspect import currentframe, getframeinfo
import json
import numpy as np
import pandas as pd
import os
from sys import platform
import time
import xarray as xr

frame = getframeinfo(currentframe()).filename
path = os.path.dirname(os.path.abspath(frame))
os.chdir(path)

from functions import npzIn

if platform == 'win32':
    homepath = "C:/users/user/github/"
    payoutpath = "f:/"
    startyear = 1948
else:
    homepath = "/home/ubuntu/"
    payoutpath = homepath
    startyear = 1980


# In[] Set up initial Signal and data
import warnings
warnings.filterwarnings("ignore")  # The empty slice warnings are too much

# Options:
# For insurance grid IDs
grid = np.load(payoutpath + "data/prf_altind/prfgrid.npz")["grid"]
grids = np.unique(grid[~np.isnan(grid)])
grids = [str(int(g)) for g in grids]
grids = [{'label': g, 'value': int(g)} for g in grids]
mask = grid * 0 +  1

# For the scatterplot maps
source = xr.open_dataarray(payoutpath + "data/prf_altind/source_array.nc")
source_signal = ('["noaa", 2018, [2000, 2017], 0.7, "indemnities", ' +
                 '"light", "24099"]')

# For the datatable at the bottom
table_path = payoutpath + "data/prf_altind/PRFIndex_specs.csv"
datatable = pd.read_csv(table_path).to_dict('RECORDS')

# For the city list
cities_df = pd.read_csv("data/cities.csv")
cities = [{'label':cities_df['NAME'][i]+ ", " + cities_df['STATE'][i],
           'value':cities_df['grid'][i]} for i in range(len(cities_df))]

    # Set Scales by Signal
# Create dictionary that finds max values for each strike level and return type
scaletable = pd.read_csv(payoutpath + "data/prf_altind/PRF_Y_Scales.csv")

############################# Option #2: Calculate Payouts ####################
# This option will be necessary for the full app of the future. Currently, all
    # of the payouts are pre-calculated for speed in the online app. This is
    # because I haven't quite yet figured out installation of gdal or rasterio
    # on the virtual linux machine. Once that happens we'll be able to
    # calculate hypothetical payouts back to 1948 (or longer) and adjust the
    # baseline rate to see what happens with that as well. This would also
    # allow for customization of acreage, allocation, productivity level, etc.
    # I believe it will necessarily be slightly slower when calculating the
    # initial insurance package of any individual index but will not slow
    # responsivity once the first call is returned. 
    # Also, by adding a few workers or threads to even a one core machine, it
    # might end up being comparably fast

## Actuarial Rates
#indices = ['noaa','pdsi','pdsisc','pdsiz','spi1','spi2','spi3','spi6','spei1',
# 'spei2','spei3','spei6']
#
## Actuarial rate paths -- to be simplified
#with np.load(homepath + 'data/actuarial/premium_arrays_2017.npz') as data:
#    arrays = data.f.arr_0
#    data.close()
#with np.load(homepath + 'data/actuarial/premium_dates_2017.npz') as data:
#    dates = data.f.arr_0
#    data.close()
#premiums2017 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]
#
#with np.load(homepath + 'data/actuarial/premium_arrays_2018.npz') as data:
#    arrays = data.f.arr_0
#    data.close()
#with np.load(homepath + 'data/actuarial/premium_dates_2018.npz') as data:
#    dates = data.f.arr_0
#    data.close()
#premiums2018= [[str(dates[i]),arrays[i]] for i in range(len(arrays))]
#
#with np.load(homepath + 'data/actuarial/base_arrays_2017.npz') as data:
#    arrays = data.f.arr_0
#    data.close()
#with np.load(homepath + 'data/actuarial/base_dates_2017.npz') as data:
#    dates = data.f.arr_0
#    data.close()
#bases2017 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]
#
#with np.load(homepath + 'data/actuarial/base_arrays_2018.npz') as data:
#    arrays = data.f.arr_0
#    data.close()
#with np.load(homepath + 'data/actuarial/base_dates_2018.npz') as data:
#    dates = data.f.arr_0
#    data.close()
#bases2018 = [[str(dates[i]),arrays[i]] for i in range(len(arrays))]

######################### Total Project Description ###########################
description_text = open("project_description.txt").read()

# These become titles for hover info
description  = ''
mapinfo = ''
trendinfo = ''
seriesinfo = ''

# In[]: Create the App Object 
app = dash.Dash(__name__)

# The stylesheet is based one of the DASH examples
app.css.append_css({'external_url':
    'https://rawgit.com/WilliamsTravis/PRF-USDM/master/dash-stylesheet.css'})

# Create server object
server = app.server

# Create and initialize a cache for storing data - data pocket
cache = Cache(config={'CACHE_TYPE': 'simple'})
cache.init_app(server)

# In[] Create Lists and Dictionaries
# Index Paths
indices = [{'label': 'Rainfall Index', 'value': 'noaa'},
           {'label': 'PDSI', 'value': 'pdsi'},
           {'label': 'PDSI-Self Calibrated', 'value': 'pdsisc'},
           {'label': 'Palmer Z Index', 'value': 'pdsiz'},
           {'label': 'SPI-1', 'value': 'spi1'},
           {'label': 'SPI-2', 'value': 'spi2'},
           {'label': 'SPI-3', 'value': 'spi3'},
           {'label': 'SPI-6', 'value': 'spi6'},
           {'label': 'SPEI-1', 'value': 'spei1'},
           {'label': 'SPEI-2', 'value': 'spei2'},
           {'label': 'SPEI-3', 'value': 'spei3'},
           {'label': 'SPEI-6', 'value': 'spei6'},
           {'label': 'EDDI-1', 'value': 'eddi1'},
           {'label': 'EDDI-2', 'value': 'eddi2'},
           {'label': 'EDDI-3', 'value': 'eddi3'},
           {'label': 'EDDI-6', 'value': 'eddi6'}]

indexnames = {'noaa': 'NOAA CPC-Derived Rainfall Index',
              'pdsi': 'Palmer Drought Severity Index',
              'pdsisc': 'Self-Calibrated Palmer Drought Severity Index',
              'pdsiz': 'Palmer Z Index',
              'spi1': 'Standardized Precipitation Index - 1 month',
              'spi2': 'Standardized Precipitation Index - 2 month',
              'spi3': 'Standardized Precipitation Index - 3 month',
              'spi6': 'Standardized Precipitation Index - 6 month',
              'spei1': 'Standardized Precipitation-Evapotranspiration Index' +
                       ' - 1 month',
              'spei2': 'Standardized Precipitation-Evapotranspiration Index' +
                       ' - 2 month',
              'spei3': 'Standardized Precipitation-Evapotranspiration Index' +
                       ' - 3 month',
              'spei6': 'Standardized Precipitation-Evapotranspiration Index' +
                       ' - 6 month',
              'eddi1': 'Evaporative Demand Drought Index - 1 month',
              'eddi2': 'Evaporative Demand Drought Index - 2 month',
              'eddi3': 'Evaporative Demand Drought Index - 3 month',
              'eddi6': 'Evaporative Demand Drought Index - 6 month'}

# This is for accessing the dataset
returns = [{'label': 'Potential Producer Premiums', 'value': 'premiums'},
          {'label': 'Potential Indemnities', 'value': 'indemnities'},
          {'label': 'Potential Payout Frequencies', 'value': 'frequencies'},
          {'label': 'Potential Payment Calculation Factors', 'value': 'pcfs'},
          {'label': 'Potential Net Payouts', 'value': 'nets'},
          {'label': 'Potential Loss Ratios', 'value': 'lossratios'}]

# These get the right number for the return type chosen
returnumbers = {'premiums': 0,
               'indemnities': 1,
               'frequencies': 2,
               'pcfs': 3,
               'nets': 4,
               'lossratios': 5}

# This is for labeling
returndict = {'premiums': 'Potential Producer Premiums',
              'indemnities': 'Potential Indemnities',
              'frequencies': 'Potential Payout Frequencies',
              'pcfs': 'Potential Payment Calculation Factors',
              'nets': 'Potential Net Payouts',
              'lossratios': 'Potential Loss Ratios'}
trenddict = {'premiums': 'Average Premium ($)',
             'indemnities': 'Average Indemnity ($)',
             'frequencies': 'Average Payout Frequency',
             'pcfs': 'Average Payment Calculation Factor',
             'nets': 'Average Net Payout ($)',
             'lossratios': 'Average Loss Ratio'}
seriesdict = {'premiums': 'Premium ($)',
              'indemnities': 'Indemnity ($)',
              'frequencies': 'Payout Frequency',
              'pcfs': 'Payment Calculation Factor',
              'nets': 'Net Payout ($)',
              'lossratios': 'Loss Ratio'}

# Strike levels
strikes = [{'label': '70%', 'value': .70},
           {'label': '75%', 'value': .75},
           {'label': '80%', 'value': .80},
           {'label': '85%', 'value': .85},
           {'label': '90%', 'value': .90}]

# Map types'light', 'basic', 'outdoors', 'satellite', or 'satellite-streets'
maptypes = [{'label': 'Light', 'value': 'light'},
            {'label': 'Dark', 'value': 'dark'},
            {'label': 'Basic', 'value': 'basic'},
            {'label': 'Outdoors', 'value': 'outdoors'},
            {'label': 'Satellite', 'value': 'satellite'},
            {'label': 'Satellite Streets', 'value': 'satellite-streets'}]

# Year Marks for Slider
years = [int(y) for y in range(startyear, 2018)]
yearmarks = dict(zip(years, years))
for y in yearmarks:
    if y % 5 != 0:
        yearmarks[y] = ""

# Data Frame Column Names
dfcols = [{'label': "DI: Drought Index", 'value': 1},
          {'label': "AY: Actuarial Year", 'value': 2},
          {'label': "ICOV: Index Coefficient of Variance", 'value': 3},
          {'label': "S: Strike", 'value': 4},
          {'label': "TS: Temporal Scale", 'value': 5},
          {'label': "MAXP: Max Payment", 'value': 6},
          {'label': "MINP: Minimum Payment", 'value': 7},
          {'label': "MEDP: Median Payment", 'value': 8},
          {'label': "MEANP: Mean Payment", 'value': 9},
          {'label': "PSD: Payment Standard Deviation", 'value': 10},
          {'label': "MOSDP: Monthly Payment Standard Deviation", 'value': 11},
          {'label': "MEANPCF: Mean Payment Calculation Factor", 'value': 12},
          {'label': "SDPCF: Payment Calculation Factor Standard Deviation", 
           'value': 13},
          {'label': "MOSDPCF: Monthly Payment Calculation Factor" +
           " Standard Deviation", 'value': 14},
          {'label': "MEANPF: Mean Payout Frequency", 'value': 15},
          {'label': "MOSDPF: Monthly Payout Frequency Standard Deviation",
           'value': 16}]

# Create Coordinate Index
xs = range(300)
ys = range(120)
lons = [-130 + .25*x for x in range(0,300)]
lats = [49.75 - .25*x for x in range(0,120)]
londict = dict(zip(lons, xs))
latdict = dict(zip(lats, ys))
londict2 = {y: x for x, y in londict.items()}
latdict2 = {y: x for x, y in latdict.items()}


# In[] Map Layout
mapbox_access_token = ('pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNk' +
                       'MnptaWlwcHZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ')

# Check this out! https://paulcbauer.shinyapps.io/plotlylayout/
layout = dict(
    autosize=True,
    height=500,
    font=dict(color='#CCCCCC'),
    titlefont=dict(color='#CCCCCC', size='20'),
    margin=dict(
        l=55,
        r=35,
        b=65,
        t=95,
        pad=4
    ),
    hovermode="closest",
    plot_bgcolor="#eee",
    paper_bgcolor="#083C04",
    legend=dict(font=dict(size=10), orientation='h'),
    title='<b>Potential Payout Frequencies</b>',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="satellite-streets",  #'light', 'basic', 'outdoors', 'satellite'
        center=dict(
            lon=-95.7,
            lat=37.1
        ),
        zoom=2,
    )
)

# In[] Create app layout
app.layout = html.Div([

               html.Div([
                 # Title and Banner
                 html.A(
                   html.Img(
                     src=("https://github.com/WilliamsTravis/" +
                          "Pasture-Rangeland-Forage/blob/master/" +
                          "data/earthlab.png?raw=true"),
                     className='one columns',
                     style={'height': '40',
                            'width': '100',
                            'float': 'right',
                            'position': 'static'}),
                   href="https://www.colorado.edu/earthlab/",
                   target="_blank"),
                 html.A(
                   html.Img(
                     src=('https://github.com/WilliamsTravis/Pasture-' +
                          'Rangeland-Forage/blob/master/data/' +
                          'wwa_logo2015.png?raw=true'),
                     className='one columns',
                     style={'height': '50',
                            'width': '150',
                            'float': 'right',
                            'position': 'static'}),
                   href="http://wwa.colorado.edu/",
                   target="_blank"),
                 html.A(
                   html.Img(
                     src=("https://github.com/WilliamsTravis/Pasture-" +
                          "Rangeland-Forage/blob/master/data/" +
                          "nidis.png?raw=true"),
                     className='one columns',
                     style={'height': '50',
                            'width': '200',
                            'float': 'right',
                            'position': 'relative'}),
                   href="https://www.drought.gov/drought/",
                   target="_blank"),
                 html.A(
                   html.Img(
                     src=("https://github.com/WilliamsTravis/Pasture-" +
                          "Rangeland-Forage/blob/master/data/" +
                          "cires.png?raw=true"),
                     className='one columns',
                     style={'height': '50',
                            'width': '100',
                            'float': 'right',
                            'position': 'relative',
                            'margin-right': '20'}),
                   href="https://cires.colorado.edu/",
                   target="_blank")],
                 className='row'),
         html.Div([
           html.H1('Drought Index Insurance Analysis Laboratory',
                   className='twelve columns'),
           html.Button(id='description_button',
                       children='Project Description (Click)',
                       title=description,
                       type='button')],
           className='row' ,
           style={'font-weight': 'bold',
                  'text-align': 'center',
                  'margin-top': '40',
                  'margin-bottom': '40'}),
         html.Div([
           dcc.Markdown(id="description",
                        children=description)],
           style={'text-align': 'justify',
                  'margin-left': '150',
                  'margin-right': '150'}),
 
         # Year Slider Text
         html.Div([
           html.H5('',
                   id='year_text',
                   className='six columns',
                   style={'text-align': 'justify'})],
           className='row'),
         # Year Sliders
         html.Div([
           html.P('Study Period Year Range'),
             dcc.RangeSlider(id='year_slider',
                             value=[startyear, 2017],
                             min=startyear,
                             max=2017,
                             marks=yearmarks)],
           className = "twelve columns",
           style={'margin-top': '20',
                  'margin-bottom': '40'}),

        # Selections
        html.Div([
          # Dropdowns
          html.Div([
            html.P('Drought Index'),
            dcc.Dropdown(id='index_choice',
                         options=indices,
                         value="noaa",
                         placeholder="NOAA CPC-Derived Rainfall Index"),
            html.P(""),
            html.P('Choose Information Type'),
            dcc.Dropdown(id='return_type',
                         value='indemnities',
                         multi=False,
                         options=returns)],
            className='four columns'),

          # Other Selections
          html.Div([
            html.P('Strike Level'),
            dcc.RadioItems(id='strike_level',
                           options=strikes,
                           value=.75,
                           labelStyle={'display': 'inline-block'}),
            html.P('Actuarial Year'),
            dcc.RadioItems(id='actuarial_year',
                           value=2018,
                           options=[{'label': '2017', 'value': 2017},
                                    {'label': '2018', 'value': 2018}],
                           labelStyle={'display': 'inline-block'}),
            html.Button(id='submit', 
                        type='submit', 
                        n_clicks=0, 
                        n_clicks_timestamp='0',
                        children='submit')],
            className='four columns'),

          # Map Selector
          html.Div([
            html.P("Map Type"),
            dcc.Dropdown(id="map_type",
                         value="light",
                         options=maptypes,   
                         multi=False),
            html.P(" "),
            html.P("RMA Grid ID"),
            dcc.Dropdown(id="grid_choice",
                         value=24099,
                         placeholder="Type Grid ID",
                         options=grids,
                         multi=False,
                         searchable=True),
            html.P(" "),
            html.P("City"),
            dcc.Dropdown(id="city_choice",
                         value=24099,
                         placeholder="Type city name",
                         options=cities,
                         multi=False,
                         searchable=True)],
            className='four columns')],
            className='row'),

        # Hidden DIV to store the signal
        html.Div(id='signal',
                 style={'display': 'none'}
            ),

        # Hidden DIV to store the grid_choice
        html.Div(id='click_store',
                 children = '24099',
                 style={'display': 'none'}
            ),
        html.Div(id='city_store',
                 children='24099',
                 style={'display': 'none'}
            ),
        html.Div(id='grid_store',
                 children='24099',
                 style={'display': 'none'}
            ),

        # Hidden DIV to store the final target id used by the bar charts
        html.Div(id='targetid_store',
                 children='24099',
                 style={'display': 'none'}
            ),

        # Single Interactive Map
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='main_graph'),
                        html.Button(id='map_info',
                                    title = mapinfo,
                                    type='button',
                                    n_clicks = 0,
                                    children='Map Info \uFE56 (Hover)'),
                    ],
                    className='seven columns',
                    style={'float': 'left',
                            'margin-top': '40'
                            }
                ),
                html.Div(
                    [
                        dcc.Graph(id='trend_graph'),
                        html.Button(id='trend_info',
                                    type='button',
                                    title = trendinfo,
                                    n_clicks = 0,
                                    children='Trend Info \uFE56 (Hover)'),
                    ],
                    className='five columns',
                    style={
                           'float':'right',
                           'margin-top': '40'
                           },

                )
            ],
            className='row',
        ),

        # Time-Series
        html.Div(
            [
                html.Div(
                    [
                        dcc.Graph(id='series_graph'),
                        html.Button(id='series_info',
                                    type='button',
                                    title = seriesinfo,
                                    n_clicks = 0,
                                    children='Time Series Info \uFE56 (Hover)'),
                    ],
                    style={'margin-top': '10'}
                ),
            ],
            className='row',

        ),

        # Data chart
        html.Div(
            [
                html.Div(
                    [   html.H1(" "),
                        html.H4('Summary Statistics'),
                        html.H5("Column Key"),
                        dcc.Dropdown(options=dfcols,
                                     placeholder="Acronym: Description (Click)"),
                        dte.DataTable(
                             rows = datatable,
                             id = "summary_table",
                             editable=False,
                             filterable=True,
                             sortable=True,
                             row_selectable=True,
                             )
                    ],
                    className='twelve columns',
                    style={'width':'100%',
                           'display': 'inline-block',
                           'padding': '0 20'},
                ),
            ],
            className='row'
        ),
    ],
    className='ten columns offset-by-one'
  )


# In[]:
###############################################################################
######################### Create Cache ########################################
###############################################################################
@cache.memoize()
# Next step, create a numpy storage unit to store previously loaded arrays
def global_store(signal):
    # Unjson the signal (Back to original datatypes)
    signal = json.loads(signal)
    # signal = ["noaa", 2018, [2000, 2017], 0.7, "indemnities","strike"]

    # Rename signals for comprehension
    index = signal[0]
    actuarialyear = signal[1]
    studyears = signal[2]
    strike = signal[3]
    returntype = signal[4]
  
    ################## Option #1: Retrieve Payouts ###########################
    #  I am now storing the windows payout data on a d drive...fix this
    path = (payoutpath + "data/payouts/AY" + str(actuarialyear) + "_" +
            str(int(strike*100)) + "_" + returntype + "_" + index)    
    df = npzIn(path + "_arrays.npz", path + "_dates.npz")

    return df

def retrieve_data(signal):
    if str(type(signal)) == "<class 'NoneType'>":
        signal = source_signal
    df = global_store(signal)
    return df

###############################################################################
########################### Get Signal ########################################
###############################################################################
# Store data in the cache and hide the signal to activate it in the hidden div
@app.callback(Output('signal', 'children'),
              [Input('submit','n_clicks')],
              [State('index_choice', 'value'),
               State('actuarial_year','value'),
               State('year_slider','value'),
               State('strike_level','value'),
               State('return_type','value'),
               State('map_type','value')])
def submitSignal(clicks, index_choice, actuarial_year, year_slider,
                 strike_level, returntype, maptype):
    signal = json.dumps([index_choice, actuarial_year, year_slider,
                         strike_level, returntype, maptype])
    return signal

# In[]
###############################################################################
######################### Create Callbacks ####################################
###############################################################################
# Other Call Backs
 # Slider1 -> Base line Year text
@app.callback(Output('year_text', 'children'),
              [Input('year_slider', 'value')])
def update_year_text(year_slider):
    return "Study Period: {} - {} ".format(year_slider[0], year_slider[1])

@app.callback(Output('description', 'children'),
              [Input('description_button', 'n_clicks')])
def toggleDescription(click):
    if not click:
        click = 0
    if click%2 == 1:
        description = description_text
    else:
        description = ""
    return description

# Button2 -> Map Info Text
@app.callback(Output('map_info', 'title'),
              [Input('signal', 'children')])
def update_mapinfo(signal):
    # For the strike level
    if not signal:
        signal = source_signal
    signal = json.loads(signal)
    strike_level = signal[3]
        # Description for Info Button:
    mapinfo = (" Click the map for local information. This shows the " +
                   "average amount of payout potential at each of the available " +
                   "grid cells using the experimental index insurance program " +
                   "with a 50% allocation of total protection to each insurance " +
                   "interval from a hypothetical policy on a 500 acre ranch at " +
                   "the "+ str(int(strike_level*100)) + "% Strike Level and " +
                   "100% productivity level. Scroll to zoom in and out, click " +
                   "and drag to pan, and hold control while clicking and " + 
                   "dragging to change the viewing aspect. Click on any single " +
                   "point to update the information graphs to the right and " + 
                   "below.")
    return mapinfo

# Button3 -> Trend Info Text
@app.callback(Output('trend_info', 'title'),
              [Input('signal', 'children'),
               Input('main_graph','clickData')])
def update_trendinfo(signal,clickData):
    # For the strike level
    if not signal:
        signal = source_signal
    signal = json.loads(signal)
    strike_level = signal[3]
    # For the grid id
    if clickData is None:
        x = londict.get(-100)
        y = latdict.get(40)
        targetid  = grid[y,x]
    else:
        x = londict.get(clickData['points'][0]['lon'])
        y = latdict.get(clickData['points'][0]['lat'])
        targetid  = grid[y,x]
    targetid = str(int(targetid))

    # Description for Info Button:
    trendinfo = (" This bar chart shows the average monthly amount of payout potential at grid cell #"
                + targetid + " using the experimental index insurance program with a 50% allocation of "
               "total protection to each insurance interval from a hypothetical policy on a 500 "
               "acre ranch at the "+ str(int(strike_level*100)) + "% Strike Level and 100% "
               "productivity level.")
    return trendinfo

# Button4 -> Time Series Info Text
@app.callback(Output('series_info', 'title'),
              [Input('signal', 'children'),
               Input('main_graph','clickData')])
def update_seriesinfo(signal,clickData):
    # For the strike level
    if not signal:
        signal = source_signal
    signal = json.loads(signal)
    strike_level = signal[3]
    year1 = signal[2][0]
    year2 = signal[2][1]

    # For the grid id
    if clickData is None:
        x = londict.get(-100)
        y = latdict.get(40)
        targetid  = grid[y,x]
    else:
        x = londict.get(clickData['points'][0]['lon'])
        y = latdict.get(clickData['points'][0]['lat'])
        targetid  = grid[y,x]
    targetid = str(int(targetid))

    # Description for Info Button:
    seriesinfo = (" This is a time series of potential payouts that would have been received between "
                  +  str(year1) + " and " + str(year2) + " at grid cell #"
                  + targetid + " using the experimental index insurance program with a 50% allocation of "
                  "total protection to each insurance interval from a hypothetical policy on a 500 "
                  "acre ranch at the "+ str(int(strike_level*100)) + "% Strike Level and 100% "
                  "productivity level.")

    return seriesinfo

# In[] 
@app.callback(Output('click_store','children'),
              [Input('main_graph','clickData')])
def clickOut(clickData):
    if clickData is None:
        click_choice = 24099
        when = time.time()
    else:
        print(clickData)
        end_digit = clickData['points'][0]['text'].index("<")
        click_choice = int(clickData['points'][0]['text'][8:end_digit])
        when = time.time()
    print("Click: " + str(click_choice)+", time: " + str(when))
    return json.dumps([click_choice, when])

@app.callback(Output('city_store','children'),
              [Input('city_choice','value')])
def cityOut(city_choice):
    if city_choice is None:
        city_choice = 24099
    when = time.time()
    print("City: "+ str(city_choice) + ", time: " + str(when))
    return json.dumps([city_choice, when])

@app.callback(Output('grid_store','children'),
              [Input('grid_choice','value')])
def gridOut(grid_choice):
    if grid_choice is None:
        grid_choice = 24099
    when = time.time()
    print("Grid: " + str(grid_choice) + ", time: " + str(when))
    grid_store = json.dumps([grid_choice, when])
    return grid_store

@app.callback(Output('targetid_store','children'),
              [Input('click_store','children'),
              Input('city_store','children'),
              Input('grid_store','children')])
def whichGrid(click_store, city_store, grid_store):
    cls,clt = json.loads(click_store)
    cis,cit = json.loads(city_store)
    grs,grt = json.loads(grid_store)

    if clt > cit and clt > grt:
        targetid = cls
    if cit > clt and cit > grt:
        targetid = cis
    if grt > clt and grt > cit:
        targetid = grs

    print("whichGrid Target ID: " + str(targetid))

    return json.dumps(targetid)

# In[]
###############################################################################
######################### Graph Builders ######################################
###############################################################################
@app.callback(Output('main_graph', 'figure'),
              [Input('signal', 'children'),
               Input('map_type', 'value')])           
def makeMap(signal, maptype):
    """
    This will be the map itself, it is not just for changing maps.
        In order to map over mapbox we are creating a scattermapbox object.
    """
    # Clear memory space
    gc.collect()

    # Get data
    df = retrieve_data(signal)
    
    # Get signal for labeling
    signal = json.loads(signal)
    indexname = signal[0]
    return_type = signal[4]
    strike_level = signal[3]
    date1 = signal[2][0]
    date2 = signal[2][1]
    actuarialyear = signal[1]

    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and
          int(d[0][-6:-2]) <= date2]
    df = [a[1] for a in df]
    if return_type == 'frequencies':
        df = np.nansum(df, axis=0)*mask
    else:
        df = np.nanmean(df, axis=0)*mask

    # Data symbol for hover data
    if return_type == "premiums" or return_type == "indemnities"or return_type == "nets":
        datasymbol = "$"
    else:
        datasymbol = ""

    # Second, convert data back into an array, but in a from xarray recognizes
    array = np.array([df], dtype = "float32")

    # Third, change the source array to this one. Source is defined up top
    source.data = array

    # Fourth, bin the values into lat, long points for the dataframe
    dfs = xr.DataArray(source, name = "data")
    pdf = dfs.to_dataframe()
    step = .25
    to_bin = lambda x: np.floor(x / step) * step
    pdf["latbin"] = pdf.index.get_level_values('y').map(to_bin)
    pdf["lonbin"] = pdf.index.get_level_values('x').map(to_bin)
    pdf['gridx']= pdf['lonbin'].map(londict)
    pdf['gridy']= pdf['latbin'].map(latdict)
    grid2 = np.copy(grid)
    grid2[np.isnan(grid2)] = 0
    pdf['grid'] = grid2[pdf['gridy'], pdf['gridx']]
    pdf['grid'] = pdf['grid'].apply(int).apply(str)
    pdf['data'] = pdf['data'].astype(float).round(3)
    pdf['printdata'] = "GRID #: " + pdf['grid'] + "<br>Data: " + pdf['data'].apply(str)

    df_flat = pdf.drop_duplicates(subset=['latbin', 'lonbin'])
    df = df_flat[np.isfinite(df_flat['data'])]

    # Add Grid IDs
    colorscale = [[0, 'rgb(68, 13, 84)'], 
                  [0.1, 'rgb(47, 107, 142)'],
                  [0.2, 'rgb(32, 164, 134)'],
                  [.3, 'rgb(255, 239, 71)'],
                  [.45, 'rgb(229, 211, 13)'],
                  [.9, 'rgb(252, 63, 0)'],
                  [1, 'rgb(140, 35, 0)']] 

# Get Y-scale
    # Copy Scaletable
    if return_type != "premiums" or return_type != "nets":
        st = scaletable
        maxy = max(st['max_' + return_type])
        miny = min(st['min_' + return_type])
    elif return_type == "premiums":
        st = scaletable
        miny = 0
        maxy = max(st['max_indemnities'])
    elif return_type == "nets":
        st = scaletable
        miny = 0
        maxy = max(st['max_indemnities'])      

# Create the scattermapbox object
    data = [
        dict(
        type='scattermapbox',
        lon=df['lonbin'],
        lat=df['latbin'],
        text=df['printdata'],
        mode='markers',
        hoverinfo='text',
        marker=dict(
            colorscale=colorscale,
            cmin=miny,
            color=df['data'],
            cmax=maxy,
            opacity=0.85,
            size=5,
            colorbar=dict(
                textposition = "auto",
                orientation = "h",
                font = dict(size = 15)
                )
            )
        )]

    # Title Business
    if return_type == 'frequencies':
        calc = "Sum "
    else:
        calc = "Average "

    layout['title'] = ("<b>" + indexnames.get(signal[0]) + "<br>" + calc+returndict.get(return_type)
                        + " | " +str(signal[2][0]) + " to " + str(signal[2][1]) + " | "
                        + str(int(strike_level*100)) + "% Strike Level</b>")
    layout['titlefont'] = {'color':'#CCCCCC','size' : 15}
    layout['mapbox']=dict(
        accesstoken=mapbox_access_token,
        style=maptype,
        center=dict(
            lon= -95.7,
            lat= 37.1
        ),
        zoom=2,
        )
    print("Mapbox Layout: " + str(layout['mapbox']))
          
    figure = dict(data=data, layout=layout)

    return figure


# In[]
###############################################################################
###############################################################################
###############################################################################
@app.callback(Output('trend_graph','figure'),
              [Input('main_graph','clickData'),
               Input('signal','children'),
               Input('targetid_store','children')])
def makeTrendBar(clickData, signal, targetid):
    '''
    Makes a monthly trend bar for the selected information type at the clicked
        location.
    '''
    # Get dataframe then signal for labeling
    df = retrieve_data(signal)
    signal = json.loads(signal)
    return_type = signal[4]
    date1 = signal[2][0]
    date2 = signal[2][1]
    
    # Check that the grid id routing works
    targetid = int(targetid)
    print("############## Trend Map Target ID: " +
          str(targetid) + ", type: " + str(type(targetid)) +
          " #####################")

    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and
          int(d[0][-6:-2]) <= date2]

    # Catch the target grid cell
    index = np.where(grid == targetid)

    # Create the time series of data at that gridcell
    timeseries = [[item[0],item[1][index]] for item in df]
    dates = [int(item[0][-6:-2]) for item in df]

    # For the x axis and value matching
    intervals = [format(int(interval),'02d') for interval in range(1,12)]
    months = {1:'Jan-Feb',
              2:'Feb-Mar',
              3:'Mar-Apr',
              4:'Apr-May',
              5:'May-Jun',
              6:'Jun-Jul',
              7:'Jul-Aug',
              8:'Aug-Sep',
              9:'Sep-Oct',
              10:'Oct-Nov',
              11:'Nov-Dec'}

    # The actual values
    valuelist = [[series[1] for series in timeseries if
                  series[0][-2:] ==  interval] for interval in intervals]

    # In tuple form for the bar chart
    if return_type == 'frequencies':
        averages =  tuple(np.asarray([np.sum(sublist) for
                                      sublist in valuelist]))
        calc = "Sums "
    else:
        averages =  tuple(np.asarray([np.mean(sublist) for
                                      sublist in valuelist]))
        calc = "Averages "

    # For display
    intlabels = [months.get(i) for i in range(1,12)]
    x = np.arange(len(intervals))
    layout_count = copy.deepcopy(layout)
    colors = [
            "#050f51",  # 'darkblue',
            "#1131ff",  # 'blue',
            "#09bc45",  # 'somegreensishcolor',
            "#6cbc0a",  # 'yellowgreen',
            "#0d9e00",  # 'forestgreen',
            "#075e00",  # 'darkgreen',
            "#1ad10a",  # 'green',
            "#fff200",  # 'yellow',
            "#ff8c00",  # 'red-orange',
            "#b7a500",  # 'darkkhaki',
            "#6a7dfc"   # 'differentblue'
            ]

    data = [
        dict(
            type='bar',
            marker = dict(color=colors, line=dict(width=3.5,
                                                  color="#000000")),
#            yaxis = dict(range = [0,2500]),
            x=x,
            y=averages
        )]

    if 'nets' in return_type:
        signal[4] = 'premiums'
        signal2 = json.dumps(signal)
        df2 = retrieve_data(signal2)
        arrays = [a[1] for a in df2]
        ylow = -np.nanmax(arrays)
    else:
        ylow = 0

    if return_type != "premiums":
        col = "max_"+return_type
        maxy = max(scaletable[col])
        maxy = 15 if return_type == "frequencies" else maxy
    else:
        maxy = 5000  # Didn't I specify this somewhere?
        
    if max(averages) < .75*maxy:
        yaxis = dict(
                title=trenddict.get(return_type),
                autorange=False,
                range=[ylow, .75*maxy],
                type='linear'
                )
        annotation = dict(
            text= "",
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            xref="paper",
            yref="paper"
        )
    else:
        yaxis = dict(
                title=trenddict.get(return_type),
                autorange=False,
                range=[ylow, max(averages)*1.2],
                type='linear'
                )
        annotation=dict(
            text="<b>(rescaled)</b>",
            x=0.95,
            y=0.95,
            font=dict(size=17,
                      color="#000000"),
            showarrow=False,
            bgcolor="#eee",
            xref="paper",
            yref="paper"
        )
            
            
    layout_count['title'] = ("<b>" + returndict.get(return_type)
                             + ' Monthly Trends <br> Grid ID: '
                             + str(int(targetid)) + "</b>")
    layout['titlefont'] = {'color': '#CCCCCC', 'size': 15}
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False 
    layout_count['annotations'] = [annotation]
    layout_count['xaxis'] = dict(title="Insurance Interval",
                                 tickvals=x, ticktext=intlabels,
                                 tickangle=45)
    layout_count['yaxis'] = yaxis
    figure = dict(data=data, layout=layout_count )
    return figure

# In[]
###############################################################################
######################## Time Series ##########################################
###############################################################################
@app.callback(Output('series_graph','figure'),
               [Input('main_graph','clickData'),
                Input('signal','children'),
#                Input('grid_choice','value'),
                Input('targetid_store','children')])
def makeSeries(clickData,signal,targetid):
    '''
    Just like the trend bar, but for a time series.
    '''
    targetid = int(targetid)
    print("############## Series Map Target ID: " + str(targetid) +
          ", type: " + str(type(targetid))+" #####################")

    # Get data
    df = retrieve_data(signal)

    # Get the signal for Labeling
    signal = json.loads(signal)
    return_type = signal[4]
    return_label = returndict.get(return_type)
    date1 = signal[2][0]
    date2 = signal[2][1]

    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and int(d[0][-6:-2]) <= date2]

    # For title
    dates = [item[0][-6:-2]+"-"+ item[0][-2:] for item in df]
    intervals = [int(d[-2:]) for d in dates]

    xlabels = [y for y in range(date1, date2+1)]

    # Catch the target grid cell
    index = np.where(grid == targetid)

    # Create the time series of data at that gridcell
    values = [float(item[1][index]) for item in df]
    if return_type == "pcfs" or return_type == "lossratios":
        valuesum = "<b>Total: {:,}".format(round(np.nanmean(values),4)) + "</b>"
    elif return_type == "frequencies":
        valuesum = "<b>Total: {:,}".format(int(np.nansum(values))) + "</b>"
    else:
        valuesum = "<b>Total: ${:,}".format(int(np.nansum(values))) + "</b>"

    # Create Seasonal Colors
    colors = {
        1:"#050f51",#'darkblue',
        2:"#1131ff",#'blue',
        3:"#09bc45",#'somegreensishcolor',
        4:"#6cbc0a",#'yellowgreen',
        5:"#0d9e00",#'forestgreen',
        6:"#075e00",#'darkgreen',
        7:"#1ad10a",#'green',
        8:"#fff200",#'yellow',
        9:"#ff8c00",#'red-orange',
        10:"#b7a500",#'darkkhaki',
        11:"#6a7dfc" #'differentblue'
        }

    colors = [colors.get(d) for d in intervals]

    annotation = dict(
            text=valuesum,
            x=0.95,
            y=0.95,
            font=dict(size=17, color="#000000"),
            showarrow=False,
            xref="paper",
            yref="paper"
        )

    data = [
        dict(
            x=dates,
            y=values,
            type='bar',
            name=return_label + ' Value Ditribution',
            opacity=1,
            marker=dict(color=colors,
                        line=dict(width=1, color="#000000")
                                  )
        )
    ]

    if 'nets' in return_type:
        signal[4] = 'premiums'
        signal2 = json.dumps(signal)
        df2 = retrieve_data(signal2)
        arrays = [a[1] for a in df2]
        ylow = -np.nanmax(arrays)
    else:
        ylow = 0

    if return_type != "premiums":
        col = "max_"+return_type
        maxy = max(scaletable[col])
        maxy = 1 if return_type == "frequencies" else maxy
    else:
        maxy = 1000

    if max(values) < 1.5*maxy:
        yaxis = dict(
                title = seriesdict.get(return_type),
                autorange=False,
                range=[ylow, 1.5*maxy],
                type='linear'
                )
        annotation = dict(
            text= valuesum,
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            bgcolor = "#eee",
            xref="paper",
            yref="paper"
        )
    else:
        yaxis = dict(
                title = seriesdict.get(return_type),
                autorange = False,
                range = [ylow,max(values)*1.2],
                type = 'linear'
                )
        annotation = dict(
            text=valuesum +"<br><b> (rescaled)</b>",
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            bgcolor = "#eee",
            xref="paper",
            yref="paper"
        )

    layout_count = copy.deepcopy(layout)

    incities = cities_df['NAME'][cities_df['grid'] == targetid] + ", " + cities_df['STATE'][cities_df['grid'] == targetid]
    label = "; ".join(list(incities))         
    layout_count['title'] = ("<b>" + return_label +
                             ' Time Series <br> Grid ID: ' + 
                             str(int(targetid)) + "<br>" + label + "</b>")
    layout['titlefont'] = {'color':'#CCCCCC','size' : 15}
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['annotations'] = [annotation]
    layout_count['yaxis'] = yaxis
    layout_count['xaxis'] = dict(title="Year",
                tickvals=xlabels, ticktext=xlabels, tickangle=45 )

    figure = dict(data=data, layout=layout_count)
    return figure


# In[]:
# Main
#if __name__ == '__main__':
#    app.server.run(use_reloader = False, threaded=True)#debug=True

if __name__ == '__main__':
    app.run_server()
#threaded=True
