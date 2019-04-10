# -*- coding: utf-8 -*-
"""
I've been wanting to animate three Dimensional arrays.


Created on Wed Apr 10 08:33:11 2019

@author: User
"""
import netCDF4 as nc
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation


pdsi = nc.Dataset('f:/data/droughtindices/netcdfs/pdsi.nc')
array = pdsi.variables['value'][:]
# array = array.data
hay = np.load('data/nass_hay_1959_2008.npy')
years = [h[0] for h in hay]
array = np.array([h[1] for h in hay])


# Matplotlib:
fig, ax = plt.subplots()

ax.set_ylim((array.shape[1], 0))
ax.set_xlim((0, array.shape[2]))

im = ax.imshow(array[0, :, :])

def init():
    im.set_data(array[0, :, :])
    return im,

def animate(i):
    data_slice = array[i, :, :]
    im.set_data(data_slice)
    return im,

anim = FuncAnimation(fig, animate, init_func=init, blit=False, repeat=True)

# Plotly:
pdsi = nc.Dataset('f:/data/droughtindices/netcdfs/pdsi.nc')
array = pdsi.variables['value'][:]

