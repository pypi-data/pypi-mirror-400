#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : imgfigure

"""
Figure function for showing images.
"""



# %% Libraries
from plotlp import StyledFigure, StyledAxes
from matplotlib import pyplot as plt
import numpy as np



# %% Function
def imgfigure(img, *fig_args, **imshow_kwargs) :
    '''
    Figure function for showing images.
    
    Parameters
    ----------
    img : np.ndarray
        image to plot.
    fig_args : tuple
        Positional argument to pass to matplotlib figure function.
    imshow_kwargs : dict
        key-word argument to pass to imshow method.

    Returns
    -------
    fig : StyledFigure
        Custom Figure object.

    Examples
    --------
    >>> from plotlp import imgfigure, plt
    ...
    >>> fig = imgfigure(img, **kwargs) # Change default attributes of StyleFigure by passing them here
    >>> plt.imshow(img, **kwargs) # Using plt wrappers works as usual
    '''

    ratio = np.shape(img)[1] / np.shape(img)[0]
    fig = plt.figure(*fig_args, figsize_ratio=ratio, tight=False, FigureClass=StyledFigure)
    with plt.style.context(fig.style):
        axis = StyledAxes(fig,[0, 0, 1, 1])
    fig.add_axes(axis)
    fig.axis.imshow(img, **imshow_kwargs)
    return fig



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)