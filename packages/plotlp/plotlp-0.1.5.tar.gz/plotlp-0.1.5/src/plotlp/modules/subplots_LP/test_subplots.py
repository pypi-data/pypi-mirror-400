#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : subplots

"""
This file allows to test subplots

subplots : Wrapper function defining subplots in a StyledFigure.
"""



# %% Libraries
from corelp import print, debug
from plotlp import subplots, plt
import numpy as np
debug_folder = debug(__file__)



# %% Function test
def test_subplot() :
    '''
    Test subplot function
    '''
    x = np.linspace(-10,10,50)
    y = x**2
    v = np.linspace(-10,10,100)
    X, Y = np.meshgrid(v,v)
    R = np.sqrt(X**2+Y**2)
    img = np.exp(-R**2/2/4**2)

    fig, ax = subplots(2, 2, darkmode=True)
    ax[0,0].plot(x, -y)
    ax[0,1].plot(x, y)
    ax[1,0].imshow(img, barname='intensity')
    fig.axis = 0
    plt.xlabel('axis 0')
    fig.axis = 1
    fig.axis.set_ylabel('axis 1')
    fig.title = 'test title'
    fig.paper_index()
    plt.savefig(path_png = debug_folder / 'subplot_png', close=False)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)