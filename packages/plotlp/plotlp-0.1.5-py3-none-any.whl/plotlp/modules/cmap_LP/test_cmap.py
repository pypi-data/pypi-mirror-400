#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-11-17
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : cmap

"""
This file allows to test cmap

cmap : This module adds custom cmaps to matplotlib.
"""



# %% Libraries
from corelp import print, debug
import pytest
from plotlp import cmap
from matplotlib import pyplot as plt
import numpy as np
debug_folder = debug(__file__)

v = np.arange(101)
X,Y = np.meshgrid(v,v)

# %% Function test


# %% Function test
def save_color(name, color) :
    '''
    save a color
    '''
    figure = plt.figure()
    plt.imshow(np.asarray([[color.RGBA]]))
    plt.savefig(debug_folder / f'_color_{name}_{color}.png')
    plt.close(figure)



cmaps = ['cmapLP', 'coldLP', 'warmLP', 'gradientLP', 'convergingLP', 'divergingLP', 'rainbowLP',
        'hot', 'jet', 'viridis']

@pytest.mark.parametrize("name", cmaps)
def test_names(name) :
    '''
    Test cmaps with name values
    '''
    figure = plt.figure()
    plt.imshow(X, cmap=name)
    plt.savefig(debug_folder / f'{name}.png')
    plt.close(figure)

    cm = cmap(name)
    color = cm.color
    save_color(name, color)


# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)