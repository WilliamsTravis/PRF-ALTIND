# -*- coding: utf-8 -*-
"""
I've been wanting to animate three Dimensional arrays.


Created on Wed Apr 10 08:33:11 2019

@author: User
"""
import datetime as dt
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation
from matplotlib._cm_listed import cmaps as cmaps_listed  # dict of colors with color objects
from matplotlib._cm import datad  # dict of colors with actual maps

pdsi = nc.Dataset('f:/data/droughtindices/netcdfs/pdsi.nc')
array = pdsi.variables['value'][:]
dates = pdsi.variables['time'][:]
base = dt.datetime(1900, 1, 1)
dates2 = [base + dt.timedelta(d) for d in dates]
dates3 = ['PDSI: ' + dt.datetime.strftime(d, "%Y-%m") for d in dates2]
ckeys = list(cmaps_listed.keys())
[ckeys.insert(0, d) for d in list(datad.keys())]
ckeys.sort()


# Matplotlib:
def movie(array, titles=None, axis=0):
    '''
    if the time axis is not 0, specify which it is.
    '''
    if titles is None:
        titles = ["" for t in range(len(array))]
    if type(titles) is str:
        titles = [titles + ': ' + str(t) for t in range(len(array))]

    fig, ax = plt.subplots()

    ax.set_ylim((array.shape[1], 0))
    ax.set_xlim((0, array.shape[2]))

    im = ax.imshow(array[0, :, :], cmap='viridis_r')

    def init():
        if axis == 0:
            im.set_data(array[0, :, :])
        elif axis == 1:
            im.set_data(array[:, 0, :])
        else:
            im.set_data(array[:, :, 0])
        return im,

    def animate(i):
        if axis == 0:
            data_slice = array[i, :, :]
        elif axis == 1:
            data_slice = array[:, i, :]
        else:
            data_slice = array[:, :, i]
        im.set_data(data_slice)
        ax.set_title(titles[i])
        return im,
    
    anim = FuncAnimation(fig, animate, init_func=init, blit=False, repeat=True)

    return anim

movie(array)
