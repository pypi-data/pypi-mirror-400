#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : imgfigure

"""
This file allows to test imgfigure

imgfigure : Figure function for showing images.
"""



# %% Libraries
from corelp import print, debug
from plotlp import imgfigure, plt
import numpy as np
debug_folder = debug(__file__)


def test_imshow() :
    '''
    Test figure function
    '''
    v = np.linspace(-10,10,100)
    X, Y = np.meshgrid(v,v)
    R = np.sqrt(X**2+Y**2)
    img = np.exp(-R**2/2/4**2)
    imgfigure(img, cmap='warmLP')
    plt.savefig(path_png = debug_folder / 'imshow_png', close=False)


# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)