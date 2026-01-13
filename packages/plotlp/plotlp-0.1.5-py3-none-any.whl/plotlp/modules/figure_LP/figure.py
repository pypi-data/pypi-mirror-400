#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : figure

"""
Wrapper function defining a StyledFigure.
"""



# %% Libraries
from plotlp import StyledFigure
from matplotlib import pyplot as plt



# %% Function
def figure(*args, **kwargs) :
    '''
    Wrapper function defining a StyledFigure.
    
    Parameters
    ----------
    args : tuple
        Positional argument to pass to matplotlib figure function.
    kwargs : dict
        key-word argument to pass to matplotlib figure function.

    Returns
    -------
    fig : StyledFigure
        Custom Figure object.

    Examples
    --------
    >>> from plotlp import figure, plt
    ...
    >>> fig = figure() # Change default attributes of StyleFigure by passing them here
    >>> fig.axis.plot(x, y, **kwargs) # Pass axes methods through the axis attribute
    >>> plt.plot(x, y, **kwargs) # Using plt wrappers works as usual
    '''

    fig = plt.figure(*args, **kwargs, FigureClass=StyledFigure)
    fig.add_subplot()
    return fig



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)