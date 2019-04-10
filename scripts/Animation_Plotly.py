# -*- coding: utf-8 -*-
"""
https://plot.ly/python/visualizing-mri-volume-slices/

Created on Wed Apr 10 09:43:02 2019

@author: User
"""
import netCDF4 as nc
from osgeo import gdal
import plotly.plotly as py
from plotly.grid_objs import Grid, Column
import time
import numpy as np

vol = gdal.Open('C:/users/user/downloads/attention-mri.tif')
subsets = vol.GetSubDatasets()

vol = np.array([gdal.Open(sub[0]).ReadAsArray() for sub in subsets])

volume = vol.T
r, c = volume[0].shape

pl_bone = [
    [0.0, 'rgb(0, 0, 0)'],
    [0.05, 'rgb(10, 10, 14)'],
    [0.1, 'rgb(21, 21, 30)'],
    [0.15, 'rgb(33, 33, 46)'],
    [0.2, 'rgb(44, 44, 62)'],
    [0.25, 'rgb(56, 55, 77)'],
    [0.3, 'rgb(66, 66, 92)'],
    [0.35, 'rgb(77, 77, 108)'],
    [0.4, 'rgb(89, 92, 121)'],
    [0.45, 'rgb(100, 107, 132)'],
    [0.5, 'rgb(112, 123, 143)'],
    [0.55, 'rgb(122, 137, 154)'],
    [0.6, 'rgb(133, 153, 165)'],
    [0.65, 'rgb(145, 169, 177)'],
    [0.7, 'rgb(156, 184, 188)'],
    [0.75, 'rgb(168, 199, 199)'],
    [0.8, 'rgb(185, 210, 210)'],
    [0.85, 'rgb(203, 221, 221)'],
    [0.9, 'rgb(220, 233, 233)'],
    [0.95, 'rgb(238, 244, 244)'],
    [1.0, 'rgb(255, 255, 255)']]

my_columns = []
nr_frames = 68
for k in range(nr_frames):
    my_columns.extend(
        [Column((6.7 - k * 0.1) * np.ones((r, c)), 'z{}'.format(k + 1)),
         Column(np.flipud(volume[67 - k]), 'surfc{}'.format(k + 1))]
    )
grid = Grid(my_columns)
py.grid_ops.upload(grid, 'anim_sliceshead'+str(time.time()), auto_open=False)

data=[
    dict(
        type='surface', 
        zsrc=grid.get_column_reference('z1'),
        surfacecolorsrc=grid.get_column_reference('surfc1'),
        colorscale=pl_bone,
        colorbar=dict(thickness=20, ticklen=4)
    )
]

frames=[]
for k in range(nr_frames):
    frames.append(
        dict(
            data=[dict(zsrc=grid.get_column_reference('z{}'.format(k + 1)),
                       surfacecolorsrc=grid.get_column_reference('surfc{}'.format(k + 1)))],
            name='frame{}'.format(k + 1)
        )
    )

sliders=[
    dict(
        steps=[dict(method='animate',
                    args= [['frame{}'.format(k + 1)],
                            dict(mode='immediate',
                                 frame= dict(duration=70, redraw= False),
                                 transition=dict(duration=0))],
                    label='{:d}'.format(k+1)) for k in range(68)], 
        transition= dict(duration=0),
        x=0,
        y=0, 
        currentvalue=dict(font=dict(size=12), 
                          prefix='slice: ', 
                          visible=True, 
                          xanchor='center'
                         ),  
        len=1.0
    )
]

axis3d = dict(
    showbackground=True, 
    backgroundcolor="rgb(230, 230,230)",
    gridcolor="rgb(255, 255, 255)",      
    zerolinecolor="rgb(255, 255, 255)",  
)

layout3d = dict(
         title='Slices in volumetric data', 
         font=dict(family='Balto'),
         width=600,
         height=600,
         scene=dict(xaxis=(axis3d),
                    yaxis=(axis3d), 
                    zaxis=dict(axis3d, **dict(range=[-0.1, 6.8], autorange=False)), 
                    aspectratio=dict(x=1, y=1, z=1),
                    ),
         updatemenus=[
             dict(type='buttons',
                  showactive=False,
                  y=1,
                  x=1.3,
                  xanchor='right',
                  yanchor='top',
                  pad=dict(t=0, r=10),
                  buttons=[dict(label='Play',
                                method='animate',
                                args=[
                                    None, 
                                    dict(frame=dict(duration=70, redraw=False),
                                         transition=dict(duration=0),
                                         fromcurrent=True,
                                         mode='immediate')
                                ])])
         ],
        sliders=sliders
)
                                
fig=dict(data=data, layout=layout3d, frames=frames)
py.icreate_animations(fig, filename='animslicesHead'+str(time.time()))