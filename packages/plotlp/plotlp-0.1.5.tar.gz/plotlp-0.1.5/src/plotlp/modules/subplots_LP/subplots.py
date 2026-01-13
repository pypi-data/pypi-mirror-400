#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : subplots

"""
Wrapper function defining subplots in a StyledFigure.
"""



# %% Libraries
from plotlp import StyledFigure
from matplotlib import pyplot as plt



# %% Function
def subplots(*args, **kwargs) :
    '''
    Wrapper function defining subplots in a StyledFigure.
    
    Parameters
    ----------
    args : tuple
        Positional argument to pass to matplotlib subplots function.
    kwargs : dict
        key-word argument to pass to matplotlib subplots function.

    Returns
    -------
    fig : StyledFigure
        Figure.
    axes : tuple[StyledAxes]
        tuple of axes.

    Examples
    --------
    >>> from plotlp import subplots, plt
    ...
    >>> fig, axes = subplots(nrows, ncols, **kwargs) # Works as plt.suplots
    '''

    return plt.subplots(*args, **kwargs, FigureClass=StyledFigure)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)