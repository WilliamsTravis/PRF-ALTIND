# Issues:
    # PCF maps are empty
    # The Monthly Trend Box is not aligned
    # Map changes could be quicker
    # I took garbage collection out troubleshooting, put it back in
    # Consider automatic gunicorn reloading with a webhook responding to github pushes, something like this:
	# https://www.julo.ch/blog/lovely-deploy-with-gunicorn/ (maybe, it's old though)

# In[]:
################################# Switching to/from Ubuntu VPS ##############################################################

from sys import platform
import os

if platform == 'win32':
    homepath = "C:/users/user/github/"
    os.chdir(homepath + "PRF-ALTIND")
else:
    homepath = "/home/ubuntu/"
    os.chdir(homepath+"PRF-ALTIND")


#############################################################################################################################

from functions import *

################# Test with Local Drive or Online with AWS files? ###########################################################
# In[]:
############################ Set up initial Signal and data #################################################################
import warnings
warnings.filterwarnings("ignore") # The empty slice warnings are too much

# For insurance grid IDs
grid = np.load(homepath + "data/prfgrid.npz")["grid"]
mask = grid * 0 +  1

# For the scatterplot maps
source = xr.open_dataarray(homepath + "data/source_array.nc")
source_signal = '["noaa", 2018, [2000, 2017], 0.7, "indemnities"]'

# For the datatable at the bottom
datatable = pd.read_csv(homepath + "data/PRFIndex_specs.csv").to_dict('RECORDS')


############################# Set Scales by Signal ##########################################################################
# Create a dictionary that finds the max values for each strike level and return type
scaletable = pd.read_csv(homepath + "data/PRF_Y_Scales.csv")

############################# Option #2: Calculate Payouts ##################################################################
########################## Load Index Arrays #################################################################################
## Actuarial Rates
#indices = ['noaa','pdsi','pdsisc','pdsiz','spi1','spi2','spi3','spi6','spei1','spei2','spei3','spei6']
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

######################### Total Project Description #########################################################################
#description= open("README.txt").read() # Does anyone know how justify a text file for RMarkdown?
description_text = '''
##### Pasture, Rangeland, and Forage Rainfall-Index Insurance Program Alternate Index Project


Pasture, Rangeland,  and Forage (PRF) is  a  weather-based index  insurance  program that  uses  rainfall as a basis for  payout. It is provided  through the USDA's Risk Management Agency (RMA) and is 
intended for grazing livestock  and hay  production. Grazing  production is  examined here. With the PRF policyholders will receive a payout if the  amount of  rainfall, according to anindependent and 
government-measured  index, for a given  two-month  period  is below a chosen  percentage of the  average value for  that period  in the location of the policy.
The percentage of average rainfall that could trigger a payout  is between 75%  and 90%, in 5% intervals, of average  rainfall for  each location and  time period and is chosen by the policyholder  in 
advance of  the insurance  year. This percentages is referred  to the strike level here. The government subsidizes premiums at rates  dependent on the strike level, with the lowest level receiving 59%
subsidization and  the highest 51%. Higher strike  levels  increase premiums and decrease  subsidies, but  also increase the  chance  of payout. The degree  to  which a present  index falls below  the
baseline average for a  particular interval is taken into account when determining the amount of payout, i.e. an index of .3 pays more than .5.This is done using what is called the payment calculation 
factor (PCF), which is the ratio of the  difference  between the strike  level and observed  index values and the  strike level ((strike – index)/strike). Therefore, higher strike levels also increase
the chances of larger  payouts.

Importantly, it is not possible to insure the entire year and the policyholder must  choose how to allocate coverage over the eligible time periods. Eligible time periods are, as mentioned,  organized
into two-month intervals.  These intervals overlap  such that the first includes  January  and February, the second  February and March and so on. December and January do  not overlap resulting  in 11 
intervals per year. There are lower and upper limits to the amount of coverage that can be allocated to any one interval, depending on the county. 100% of the total coverage chosen by the policyholder
must be split between these  intervals, however consecutive intervals may not be chosen because that would result in insurance of the same month twice. It is advised, by the RMA, that the intervals in
which rainfall is most  important to forage production are chosen for the largest portions of  coverage. For example, 30% coverage could be allocated to the March-April  interval, 30%  to May-Jun, and
40% to July-August.  There is, however, significant incentive not to insure growing season months for large portions of the country.
This project examines  how payouts patterns would change if the insurance program used any of a collection of alternate indices, with a focus on the seasonality of payment incentive. What is displayed
below are potential payments  for every interval for a 500-acre policy allocating 50%  of  protection to each interval.  This shows  which intervals would have triggered  payment should they have been
chosen by a policyholder.   This is displayed as a map of average payments for each location over time, a bar chart of average payments  in each insurance interval for a chosen location over time, and 
a time series of individual potential payments at a chosen location.  Actuarial rates can be based-off of either the 2017 or 2018  insurance year, in case there  is  interest in the effects of changes
on payment distributions.  Maps and charts can display potential values of producer premiums after subsidization, total indemnities, net  indemnities accounting for  premium payments,  payment trigger
frequencies, payment  calculation factors, and unsubsidized loss ratios between  indemnities and  premiums.  Available alternate drought  indices include  the Palmer Drought Severity Index (PDSI), the
self-calibrated Palmer  Drought Severity Index (PDSIsc),  the Palmer Z-index (Z Index), 1-, 2-, 3-, and  6-month Standardized Precipitation  Indices (SPI), and the 1-, 2-, 3-, and 6-month Standardized
Precipitation Evapotranspiration Indices (SPEI).

Drought indices were  adjusted for outliers, standardized,  associated with strike values proportional  to those of the rainfall index,  and payments  were  scaled in order to account for an actuarial 
system designed around rainfall. The results must be interpreted in terms of payout potential and not as a simulation of possible insurance plan configurations.

Earth Lab – CIRES at the University of Colorado Boulder
Author: Travis Williams
Email: Travis.Williams@colorado.edu
Date: 5-26-2018


                        '''
# These become titles for hover info
description  = ''
mapinfo = ''
trendinfo = ''
seriesinfo = ''

# In[]:
####################################################################################################
############################ Create the App Object #################################################
####################################################################################################
# Create Dash Application Object
app = dash.Dash(__name__)

# I am using a cascading style sheet from one of the DASH examples (oil and gas extraction in New York)
# I really need to get my own stylesheet, if anyone know how to do this...
# Check this site: https://www.w3.org/Style/CSS/Overview.en.html
app.css.append_css({'external_url': 'https://cdn.rawgit.com/plotly/dash-app-stylesheets/2d266c578d2a6e8850ebce48fdb52759b2aef506/stylesheet-oil-and-gas.css'})  # noqa: E501

# Create server object
server = app.server

# No idea
#CORS(server)

# Create and initialize a cache for storing data - data pocket - not totally sure about this yet.
cache = Cache(config = {'CACHE_TYPE':'simple'})
cache.init_app(server)


# In[]:
###############################################################################
############################ Create Lists and Dictionaries ####################
###############################################################################
# Index Paths
# Index names, using the paths we already have. These are for titles.
indices = [{'label':'Rainfall Index','value':'noaa'},
           {'label':'PDSI','value':'pdsi'},
           {'label':'PDSI-Self Calibrated','value':'pdsisc'},
           {'label':'Palmer Z Index','value':'pdsiz'},
           {'label':'SPI-1' ,'value': 'spi1'},
           {'label':'SPI-2' ,'value': 'spi2'},
           {'label':'SPI-3' ,'value': 'spi3'},
           {'label':'SPI-6' ,'value': 'spi6'},
           {'label':'SPEI-1' ,'value': 'spei1'},
           {'label':'SPEI-2' ,'value': 'spei2'},
           {'label':'SPEI-3' ,'value': 'spei3'},
           {'label':'SPEI-6','value': 'spei6'}]

indexnames = {'noaa': 'NOAA CPC-Derived Rainfall Index',
              'pdsi': 'Palmer Drought Severity Index',
              'pdsisc': 'Self-Calibrated Palmer Drought Severity Index',
              'pdsiz': 'Palmer Z Index',
              'spi1':'Standardized Precipitation Index - 1 month',
              'spi2':'Standardized Precipitation Index - 2 month',
              'spi3':'Standardized Precipitation Index - 3 month',
              'spi6':'Standardized Precipitation Index - 6 month',
              'spei1': 'Standardized Precipitation-Evapotranspiration Index - 1 month',
              'spei2': 'Standardized Precipitation-Evapotranspiration Index - 2 month',
              'spei3': 'Standardized Precipitation-Evapotranspiration Index - 3 month',
              'spei6': 'Standardized Precipitation-Evapotranspiration Index - 6 month'}

# This is for accessing the dataset
returns = [{'label':'Potential Producer Premiums','value':'premiums'},
          {'label':'Potential Indemnities','value':'indemnities'},
          {'label':'Potential Payout Frequencies','value':'frequencies'},
          {'label':'Potential Payment Calculation Factors','value':'pcfs'},
          {'label':'Potential Net Payouts','value':'nets'},
          {'label':'Potential Loss Ratios','value':'lossratios'}]

# These get the right number for the return type chosen
returnumbers = {'premiums':0,
               'indemnities':1,
               'frequencies':2,
               'pcfs':3,
               'nets':4,
               'lossratios':5}

# This is for labeling
returndict = {'premiums':'Potential Producer Premiums',
               'indemnities':'Potential Indemnities',
               'frequencies':'Potential Payout Frequencies',
               'pcfs':'Potential Payment Calculation Factors',
               'nets':'Potential Net Payouts',
               'lossratios':'Potential Loss Ratios'}
trenddict = {'premiums':'Average Premium ($)',
               'indemnities':'Average Indemnity ($)',
               'frequencies':'Average Payout Frequency',
               'pcfs':'Average Payment Calculation Factor',
               'nets':'Average Net Payout ($)',
               'lossratios':'Average Loss Ratio'}
seriesdict = {'premiums':'Premium ($)',
               'indemnities':'Indemnity ($)',
               'frequencies':'Payout Frequency',
               'pcfs':'Payment Calculation Factor',
               'nets':'Net Payout ($)',
               'lossratios':'Loss Ratio'}
# Strike levels
strikes = [{'label':'70%','value':.70},
          {'label':'75%','value':.75},
          {'label':'80%','value':.80},
          {'label':'85%','value':.85},
          {'label':'90%','value':.90}]

# Year Markes for Slider
years = [int(y) for y in range(2000,2018)]
yearmarks =dict(zip(years,years))
# Data Frame Column Names
dfcols = [{'label':"DI: Drought Index", 'value': 1},
         { 'label':"AY: Actuarial Year", 'value': 2},
         {'label':"ICOV: Index Coefficient of Variance", 'value': 3},
         { 'label':"S: Strike" , 'value': 4},
#         { 'label':" B.R.: Baseline Year Range", 'value': 5},
#         { 'label':"S.R.: Study Year Range", 'value': 6},
         { 'label':"TS: Temporal Scale", 'value': 5},
         { 'label':"MAXP($): Max Payment", 'value': 6},
         { 'label':"MINP($): Minimum Payment", 'value': 7},
         { 'label':"MEDP($): Median Payment", 'value': 8},
         { 'label':"MEANP($): Mean Payment", 'value': 9},
         { 'label':"SDP: Payment Standard Deviation", 'value': 10},
         { 'label':"MOSDP: Monthly Payment Standard Deviation", 'value': 11},
         { 'label':"MEANPCF: Mean Payment Calculation Factor", 'value': 12},
         { 'label':"SDPCF: Payment Calculation Factor Standard Deviation", 'value': 13},
         { 'label':"MOSDPCF: Monthly Payment Calculation Factor Standard Deviation", 'value': 14},
         { 'label':"MEANPF: Mean Payout Frequency", 'value': 15},
         { 'label':"MOSDPF: Monthly Payout Frequency Standard Deviation", 'value': 16}]

# Create Coordinate Index - because I can't find the array position in the
# click event!
xs = range(300)
ys = range(120)
lons = [-130 + .25*x for x in range(0,300)]
lats = [49.75 - .25*x for x in range(0,120)]
londict = dict(zip(lons, xs))
latdict = dict(zip(lats, ys))
londict2  = {y:x for x,y in londict.items()} # This is backwards to link simplified column
latdict2  = {y:x for x,y in latdict.items()} # This is backwards to link simplified column

# Create global chart template
mapbox_access_token = 'pk.eyJ1IjoidHJhdmlzc2l1cyIsImEiOiJjamZiaHh4b28waXNkMnptaWlwcHZvdzdoIn0.9pxpgXxyyhM6qEF_dcyjIQ'

# In[]:
# Map Layout:
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
        t=65,
        pad = 4
    ),

    hovermode="closest",
    plot_bgcolor="#eee",
    paper_bgcolor="#083C04",
    legend=dict(font=dict(size=10), orientation='h'),
    title='<b>Potential Payout Frequencies</b>',
    mapbox=dict(
        accesstoken=mapbox_access_token,
        style="light",
        center=dict(
            lon= -95.7,
            lat= 37.1
        ),
        zoom=3,
    )
)

# In[]:
# Create app layout
app.layout = html.Div(
    [
             html.Div(# One
            [
        # Title and Image
                html.A(html.Img(
                    src = "https://github.com/WilliamsTravis/Pasture-Rangeland-Forage/blob/master/data/earthlab.png?raw=true",
                    className='one columns',
                    style={
                        'height': '75',
                        'width': '200',
                        'float': 'right',
                        'position': 'static'
                        },
                            ),
                        href = "https://www.colorado.edu/earthlab/",
                        target = "_blank"
                        ),
                html.A(html.Img(
                    src = "https://github.com/WilliamsTravis/Pasture-Rangeland-Forage/blob/master/data/wwa_logo2015.png?raw=true",
                    className='one columns',
                    style={
                        'height': '100',
                        'width': '300',
                        'float': 'right',
                        'position': 'static',
                        },
                            ),
                        href = "http://wwa.colorado.edu/",
                        target = "_blank"
                            ),
                 html.A(html.Img(
                    src = "https://github.com/WilliamsTravis/Pasture-Rangeland-Forage/blob/master/data/nidis.png?raw=true",
                    className='one columns',
                    style={
                        'height': '100',
                        'width': '400',
                        'float': 'right',
                        'position': 'relative',
                        },
                            ),
                        href = "https://www.drought.gov/drought/",
                        target = "_blank"
                        ),
                 html.A(html.Img(
                    src = "https://github.com/WilliamsTravis/Pasture-Rangeland-Forage/blob/master/data/cires.png?raw=true",
                    className='one columns',
                    style={
                        'height': '100',
                        'width': '200',
                        'float': 'right',
                        'position': 'relative',
                        'margin-right':'20',
                        },
                            ),
                        href = "https://cires.colorado.edu/",
                        target = "_blank"
                        ),

                ],
                className = 'row'
                ),
        html.Div(# One
            [
                html.H1(
                    'Drought Index Insurance Analysis Laboratory',
                    className='twelve columns'
                ),
#                html.Button(id = 'loading_button',
#                            children = 'Loading Project',
#                            type='button'),
                html.Button(id = 'description_button',
                            children = 'Project Description (Click)',
                            title = description,
                            type='button'),
            ],
            className='row' ,
            style = {'font-weight':'bold',
                     'text-align':'center',
                     'margin-top':'40',
                     'margin-bottom':'40'}
        ),
            html.Div(
                    [
                        dcc.Markdown(id = "description",
                                    children = description)
                    ],
                    style = {'text-align':'justify',
                             'margin-left':'150',
                             'margin-right':'150'}
                    ),
                html.Div(
                    [
                        dcc.Markdown(id = "loading...",
                                    children = description)
                    ],
                    style = {'text-align':'justify',
                             'margin-left':'150',
                             'margin-right':'150'}
                    ),

        # Year Slider Text
        html.Div(# Two
            [
                html.H5(
                    '',
                    id='year_text',
                    className='six columns',
                    style={'text-align': 'justify'}
                ),

#                html.H5(
#                    '',
#                    id='year_text2',
#                    className='two columns',
#                    style={'text-align': 'center'}
#                ),
            ],
            className='row'
        ),
        # Year Sliders
        html.Div(
            [
                html.P('Study Period Year Range'),
                dcc.RangeSlider(
                    id='year_slider',
                    value=[2000, 2017],
                    min=2000,
                    max=2017,
                    marks = yearmarks
                ),
#                html.P('Baseline Average Year Range'),
#                dcc.RangeSlider(
#                    id='year_slider2',
#                    value=[1948, 2016],
#                    min=1948,
#                    max=2017
#                ),
            ],
            className = "twelve columns",
            style={'margin-top': '20',
                   'margin-bottom': '40'}
        ),

        # Selections
        html.Div(# Four
            [
                # Dropdowns
                html.Div(# Four-a
                    [
                        html.P('Drought Index'),
                        dcc.Dropdown(
                            id = 'index_choice',
                            options = indices,
                            value = "noaa",
                            placeholder = "NOAA CPC-Derived Rainfall Index"
                        ),
                        html.P('Choose Information Type'),
                        dcc.Dropdown(
                            id = 'return_type',
                            value = 'indemnities',
                            multi = False,
                            options = returns
                        ),
#                        html.P('Number of Acres'),
#                        dcc.Input(
#                            id = 'acres',
#                            placeholder = 'Number of acres...',
#                            value = 500,
#                            type = 'number'
#                            )
                        ],
                    className='four columns'
                ),
                # Other Selections
                html.Div(# Four-a
                    [
                        html.P('Guarantee Level'),
                        dcc.RadioItems(
                            id='strike_level',
                            options=strikes,
                            value=.75,
                            labelStyle={'display': 'inline-block'}
                        ),
                        html.P('Actuarial Year'),
                        dcc.RadioItems(
                            id='actuarial_year',
                            value=2018,
                            options=[{'label':'2017','value':2017},
                                      {'label':'2018','value':2018}],
                            labelStyle={'display': 'inline-block'}
                        ),

                        html.Button(id='submit', type='submit', n_clicks = 0, children='submit')

                    ],
                    className='four columns'
                ),
               ],
                className = 'row'
            ),
        # Hidden DIV to store the signal
        html.Div(id='signal',
                 style={'display': 'none'}
#                 children = ['noaa',2018,[2000, 2017],[1948, 2016], 0.8, 500,"indemnities"]
            ),
        # Single Interactive Map
        html.Div(#Five...If any one sees this, what is wrong with the alignment! Just fix it, go ahead I don't care this is ridiculous
            [
                html.Div(#Five-a
                    [
                        dcc.Graph(id='main_graph'),
                        html.Button(id='map_info',
                                    title = mapinfo,
                                    type='button',
                                    n_clicks = 0,
                                    children='Map Info \uFE56 (Hover)'),
                    ],
                    className='seven columns',
                    style={'float':'left',
                            'margin-top': '40'
                            }
                ),
                html.Div(# Five-b
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
        html.Div(#Six
            [
                html.Div(#Six-a
                    [
                        dcc.Graph(id='series_graph'),
                        html.Button(id='series_info',
                                    type='button',
                                    title = seriesinfo,
                                    n_clicks = 0,
                                    children='Time Series Info \uFE56 (Hover)'),
                    ],
#                    className='twelve columns',
                    style={'margin-top': '10'}
                ),
            ],
            className='row',
#            style = {'margin-right':'50'},

        ),
        # Data chart
        html.Div(#Seven
            [
                html.Div(
                    [   html.H1(" "),
                        html.H4('Summary Statistics'),
                        html.H5("Column Key"),
                        dcc.Dropdown(options = dfcols,
                                     placeholder = "Acronym: Description (Click)"),
                        dt.DataTable(
                             rows = datatable,
                             id = "summary_table",
                             editable=False,
                             filterable=True,
                             sortable=True,
                             row_selectable=True,
#                             min_width = 1655,
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
#    signal = ["noaa", 2018, [2000, 2017], 0.7, "indemnities"]

    # Rename signals for comprehension
    index = signal[0]
    actuarialyear = signal[1]
    studyears = signal[2] # No study years yet :/
    strike = signal[3]
    returntype = signal[4]
    
    
    ################## Option #1: Retrieve Payouts ###########################
    path = (homepath + "data/payouts/AY" + str(actuarialyear) + 
               "/" + str(int(strike*100)) + "/" 
                 + returntype + "/" +
                   index
                  )
    with np.load(path + "/arrays.npz") as data:
        arrays = data.f.arr_0
        data.close()        
    dates = pd.read_csv(path+"/dates.csv")

    df = [[str(dates['dates'][y]),arrays[y]] for y in range(len(arrays))]

    ################## Option #2: Calculate Payouts ##########################
#    # Create a few copies
#    if actuarialyear == 2017:
#        bases = bases2017
#        premiums = premiums2017
#    elif actuarialyear == 2018:
#        bases = bases2018
#        premiums = premiums2018
#    # Get index arrays
#    with np.load(homepath + "data/indices/"+index+"_arrays.npz") as data:
#        arrays = data.f.arr_0
#        data.close()
#    with np.load(homepath + "data/indices/"+index+"_dates.npz") as data:
#        names = data.f.arr_0
#        data.close()
#    indexlist = [[str(names[y]),arrays[y]] for y in range(len(arrays))]
#
#
#    # Calculate insurance payments and create a dictionary of the returns
#    # indexlist,grid, premiums, bases, actuarialyear, studyears, baselineyears, productivity, strike, acres, allocation,difference = 0, scale = True,plot = True
#    df = indexInsurance(indexlist,grid,premiums, bases,actuarialyear,
#                        studyears, [1948,2016], 1,
#                        strike, 500, .5,
#                        difference = 0, scale = True, plot = False)
#    # Return Order
#    # producerpremiums,indemnities,frequencies,pcfs,nets, lossratios,meanppremium,meanindemnity,frequencysum,meanpcf, net, lossratio
#    indx = returnumbers.get(returntype)
#    df = df[indx]
    
    
    return df

def retrieve_data(signal):
    if str(type(signal)) == "<class 'NoneType'>":
        signal = source_signal
    df = global_store(signal)
    return df


###############################################################################
########################### Get Signal ########################################
###############################################################################
# Store the data in the cache and hide the signal to activate it in the hidden div
@app.callback(Output('signal', 'children'),
              [Input('submit','n_clicks')],
              [State('index_choice', 'value'),
               State('actuarial_year','value'),
               State('year_slider','value'),
               State('strike_level','value'),
               State('return_type','value')])
def compute_value(clicks,index_choice,actuarial_year,year_slider,strike_level,returntype):
    signal = json.dumps([index_choice,actuarial_year,year_slider,strike_level,returntype])
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
    mapinfo = (" Click the map for local information. This shows the average amount of payout potential at each of the available "
               "grid cells using the experimental index insurance program with a 50% allocation of "
               "total protection to each insurance interval  from a hypothetical policy on a 500 "
               "acre ranch at the "+ str(int(strike_level*100)) + "% Strike Level and 100% "
               "productivity level.")
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
###############################################################################
######################### Graph Builders ######################################
###############################################################################
@app.callback(Output('main_graph', 'figure'),
              [Input('signal','children')])
def makeMap(signal):
    """
    This will be the map itself, it is not just for changing maps.
        In order to map over mapbox we are creating a scattermapbox object.
    """
    # Clear memory space -- ??
    #print(gc.garbage) # https://rushter.com/blog/python-garbage-collector/
    #gc.collect(2)

    # Get data
    df = retrieve_data(signal)

    # Get signal for labeling
    signal = json.loads(signal)
    return_type = signal[4]
    strike_level = signal[3]
    date1 = signal[2][0]
    date2 = signal[2][1]
    actuarialyear = signal[1]

#    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and int(d[0][-6:-2]) <= date2]
    df = [a[1] for a in df]
    if return_type == 'frequencies':
        df = np.nansum(df,axis = 0)*mask
    else:
        df = np.nanmean(df,axis = 0)*mask

    # Data symbol for hover data
    if return_type == "premiums" or return_type == "indemnities" or return_type == "nets":
        datasymbol = "$"
    else:
        datasymbol = ""
    # Second, convert data back into an array, but in a from xarray recognizes
    array = np.array([df],dtype = "float32")
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
    pdf['grid'] = grid2[pdf['gridy'],pdf['gridx']]
    pdf['grid'] = pdf['grid'].apply(int).apply(str)
#    pdf['grid'] = pdf['grid'].apply(str)
    pdf['data'] = pdf['data'].astype(float).round(3)
    pdf['printdata'] = "GRID #: " + pdf['grid'] +"<br>Data: " + pdf['data'].apply(str)
    # below adds commas but takes too long
#    pdf['printdata'] =  "<br>Data: "+datasymbol+pdf.apply(lambda x: x['data'] if pd.isnull(x['data']) else "{:,}".format(round(x['data'])), axis=1)#.apply(str)
    groups = pdf.groupby(("latbin", "lonbin"))
    df_flat = pdf.drop_duplicates(subset=['latbin', 'lonbin'])
    df= df_flat[np.isfinite(df_flat['data'])]

    # Add Grid IDs
    colorscale = [[0, 'rgb(2, 0, 68)'], [0.25, 'rgb(17, 123, 215)'],# Make darker (pretty sure this one)
                    [0.35, 'rgb(37, 180, 167)'], [0.45, 'rgb(134, 191, 118)'],
                    [0.6, 'rgb(249, 210, 41)'], [1.0, 'rgb(255, 249, 0)']] # Make darker

# Get Y-scale
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
        maxy =  100 if return_type == "frequencies" else maxy
    else:
        maxy = 2000
        
# Create the scattermapbox object
    data = [
        dict(
        type = 'scattermapbox',
        lon = df['lonbin'],
        lat = df['latbin'],
        text = df['printdata'],
        mode = 'markers',
        hoverinfo = 'text',
        marker = dict(
            colorscale = colorscale,
            cmin = 0,
            color = df['data'],
            cmax = maxy*.55,
            opacity=0.85,
            size = 5,
            colorbar=dict(
                textposition = "auto",
                orientation = "h",
                font = dict(size = 15)
                )
            )
        ), # This will be for a point to be placed on the map, lot's of things to do that
#        dict(
#            type = 'scattermapbox',
#            lon = point['lonbin'],
#            lat = point['latbin'],
#            text = np.round(point['data'],2),
#            mode = 'markers',
#            marker = dict(
#                 size = point['size'],
#                 color = 'rgb(249, 0, 0)'
#                 )
#            )
        ]


    # Title Business
    if return_type == 'frequencies':
        calc = "Sum "
    else:
        calc = "Average "

    layout['title'] = ("<b>" +indexnames.get(signal[0]) +"<br>" +calc+returndict.get(return_type)
                        +" | " +str(signal[2][0]) + " to " + str(signal[2][1])+ " | "
                        + str(int(strike_level*100)) + "% Strike Level</b>")
    layout['titlefont'] = {'color':'#CCCCCC','size' : 15}
    # Seventh wrap the data and layout into one
    figure = dict(data=data, layout=layout)
#    return {'figure':figure,'info': index_package_all}
    return figure


# In[]
###############################################################################
###############################################################################
###############################################################################
@app.callback(Output('trend_graph','figure'),
               [Input('main_graph','clickData'),
               Input('signal','children')])
def makeTrendBar(clickData,signal):
    '''
    Makes a monthly trend bar for the selected information type at the clicked
        location.
    '''
    if clickData is None:
        x = londict.get(-100)
        y = latdict.get(40)
        targetid  = grid[y,x]
    else:
        x = londict.get(clickData['points'][0]['lon'])
        y = latdict.get(clickData['points'][0]['lat'])
        targetid  = grid[y,x]

    # Get signal for labeling

#        signal = json.dumps(["noaa", 2018, [2000, 2017], 0.9, "indemnities"])
    df = retrieve_data(signal)
    signal = json.loads(signal)
    return_type = signal[4]
    date1 = signal[2][0]
    date2 = signal[2][1]

#    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and int(d[0][-6:-2]) <= date2]

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
    valuelist = [[series[1] for series in timeseries if series[0][-2:] ==  interval] for interval in intervals]

    # In tuple form for the bar chart
    if return_type == 'frequencies':
        averages =  tuple(np.asarray([np.sum(sublist) for sublist in valuelist]))
        calc = "Sums "
    else:
        averages =  tuple(np.asarray([np.mean(sublist) for sublist in valuelist]))
        calc = "Averages "

    intlabels = [months.get(i) for i in range(1,12)]
    x = np.arange(len(intervals))

    layout_count = copy.deepcopy(layout)
    colors = [
            "#050f51",#'darkblue',
            "#1131ff",#'blue',
            "#09bc45",#'somegreensishcolor',
            "#6cbc0a",#'yellowgreen',
            "#0d9e00",#'forestgreen',
            "#075e00",#'darkgreen',
            "#1ad10a",#'green',
            "#fff200",#'yellow',
            "#ff8c00",#'red-orange',
            "#b7a500",#'darkkhaki',
            "#6a7dfc" #'differentblue'
            ]
    data = [
#        dict(
#            type='scatter',
#            mode='markers',
#            x=x,
#            y=averages,
#            name= returndict.get(return_type),
#            opacity=0,
#            hoverinfo='skip',
#        ),
        dict(
            type='bar',
            marker = dict(color = colors,line = dict(width = 3.5, color = "#000000")),
#            yaxis = dict(range = [0,2500]),
            x=x,
            y=averages
        ),
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
        maxy = 15 if return_type == "frequencies" else maxy
    else:
        maxy = 5000
        
    if max(averages) < .75*maxy:
        yaxis = dict(
                title = trenddict.get(return_type),
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
                title = trenddict.get(return_type),
                autorange = False,
                range = [ylow,max(averages)*1.2],
                type = 'linear'
                )
        annotation = dict(
            text= "<b>(rescaled)</b>",
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            bgcolor = "#eee",
            xref="paper",
            yref="paper"
        )
    layout_count['title'] = ("<b>" +returndict.get(return_type)
                             + ' Monthly Trends <br> Grid ID: '
                             + str(int(targetid)) + "</b>")
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False 
    layout_count['annotations'] = [annotation]
    layout_count['xaxis'] = dict(title= "Insurance Interval",tickvals = x, ticktext = intlabels,
                                tickangle = 45)
    layout['titlefont'] = {'color':'#CCCCCC','size' : 18}
    layout_count['yaxis'] = yaxis
#    layout_count['margin'] =   dict(l=60, r=35, b=75,t=65, pad = 4)
    figure = dict(data=data, layout=layout_count )
    return figure

# In[]
###############################################################################
######################## Time Series ##########################################
###############################################################################
@app.callback(Output('series_graph','figure'),
               [Input('main_graph','clickData'),
               Input('signal','children')])
def makeSeries(clickData,signal):
    '''
    Just like the trend bar, but for a time series.
    '''
    if clickData is None:
        x = londict.get(-100)
        y = latdict.get(40)
        targetid  = grid[y,x]

    else:
        x = londict.get(clickData['points'][0]['lon'])
        y = latdict.get(clickData['points'][0]['lat'])
        targetid  = grid[y,x]

    # Get data
#    if not signal:
 #       signal = source_signal
    df = retrieve_data(signal)
    # Get the signal for Labeling
    signal = json.loads(signal)
    return_type = signal[4]
    return_label = returndict.get(return_type)
    date1 = signal[2][0]
    date2 = signal[2][1]

    #    # Filter by year range
    df = [d for d in df if int(d[0][-6:-2]) >= date1 and int(d[0][-6:-2]) <= date2]

    # For title
    dates = [item[0][-6:-2]+"-"+ item[0][-2:] for item in df]
    intervals = [int(d[-2:]) for d in dates]

    xlabels = [y for y in range(date1,date2+1)]

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
            text= valuesum,
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            xref="paper",
            yref="paper"
        )

    data = [
        dict(
            x=dates,
            y=values,
            type='bar',
            name= return_label+' Value Ditribution',
            opacity=1,
            hoverinfo='skip',
            marker = dict(color = colors,
                          line = dict(width=1, color = "#000000")
                          )
        ),
#        dict(
#            type='bar',
#            x=bins,
#            y=hists,
#            marker = dict(
#                    color = '#000000'
#            ),
#        ),
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
            text= valuesum +"<br><b> (rescaled)</b>",
            x=0.95,
            y=0.95,
            font = dict(size = 17,color = "#000000"),
            showarrow=False,
            bgcolor = "#eee",
            xref="paper",
            yref="paper"
        )
    layout_count = copy.deepcopy(layout)
    layout_count['title'] = "<b>" + return_label+' Time Series <br> Grid ID: ' + str(int(targetid)) +"</b>"
    layout_count['dragmode'] = 'select'
    layout_count['showlegend'] = False
    layout_count['annotations'] = [annotation]
    layout_count['yaxis'] = yaxis
    layout_count['xaxis'] = dict(title= "Year",tickvals = xlabels, ticktext =xlabels, tickangle = 45 )


    figure = dict(data=data, layout=layout_count)
    return figure


# In[]:
# Main
#if __name__ == '__main__':
#    app.server.run(use_reloader = False, threaded=True)#debug=True

if __name__ == '__main__':
    app.run_server()
#threaded=True
