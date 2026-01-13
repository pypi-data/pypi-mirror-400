#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-11-17
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : cmap

"""
This module adds custom cmaps to matplotlib.
"""



# %% Libraries
from corelp import selfkwargs, prop
from plotlp import color
from matplotlib.colors import LinearSegmentedColormap, ListedColormap, to_rgba_array
import numpy as np
from matplotlib import pyplot as plt
import matplotlib.cm as cm
import matplotlib
import numpy as np
from scipy.special import erf,erfinv



# %% Function
def cmap(name=None, **kwargs) :
    '''
    This module adds custom cmaps to matplotlib.
    
    Parameters
    ----------
    name : str
        Name of cmap
    black : str
        Automatic variable for color of node 0.00
    white : str
        Automatic variable for color of node 1.00
    dark : str
        Automatic variable for color of node 0.25
    light : str
        Automatic variable for color of node 0.75
    color : str
        Automatic variable for color of node 0.50
    colors : list
        list of automatic color variables
    nodes : list
        list of nodes corresponding to colors
    nodebase : list
        Base defining distribution of colors around center based on erf function, when approching 0 the function tends towards linear distribution

    Returns
    -------
    cmap : Cmap
        colormap.

    Examples
    --------
    >>> from plotlp import cmap
    ...
    >>> cmap() # TODO
    '''

    if name is not None :
        named_cmap = plt.get_cmap(name)
        return Cmap(instance=named_cmap)
    return Cmap(**kwargs)



class Cmap(LinearSegmentedColormap) :
    name = 'cmapLP'

    def __init__(self, instance=None, **kwargs) :
        if instance is not None:
            self.name = instance.name

            if isinstance(instance, LinearSegmentedColormap):
                # Works for segmented colormaps
                cdict = instance._segmentdata
            elif isinstance(instance, ListedColormap):
                # Convert ListedColormap to cdict for LinearSegmentedColormap
                colors = instance.colors
                r, g, b = np.array(colors).T
                # simple linear nodes from 0 to 1
                nodes = np.linspace(0, 1, len(colors))
                cdict = {
                    "red": np.column_stack([nodes, r, r]),
                    "green": np.column_stack([nodes, g, g]),
                    "blue": np.column_stack([nodes, b, b]),
                    "alpha": np.column_stack([nodes, np.ones(len(colors)), np.ones(len(colors))]),
                }
            else:
                raise TypeError(f"Unsupported colormap type: {type(instance)}")
        else:
            # If creating from colors passed in kwargs
            selfkwargs(self, kwargs)
            r, g, b, a = to_rgba_array(self.colors).T
            nodes = self.nodes
            cdict = {
                "red": np.column_stack([nodes, r, r]),
                "green": np.column_stack([nodes, g, g]),
                "blue": np.column_stack([nodes, b, b]),
                "alpha": np.column_stack([nodes, a, a]),
            }

        super().__init__(self.name, cdict)



    _black = 'black'
    @prop(variable=True)
    def black(self) -> str :
        if self._black is None :
            return color(rgb=self(self.get_node(0.)))
        return color(auto=self._black)

    _white =  'white'
    @prop(variable=True)
    def white(self) -> str :
        if self._white is None :
            return color(rgb=self(self.get_node(1.)))
        return color(auto=self._white)

    _color = None
    @prop(variable=True)
    def color(self) :
        if self._color is None :
            return color(rgb=self(self.get_node(0.5)))
        return color(auto=self._color)

    _dark = None #dark color
    @prop(variable=True)
    def dark(self) -> str :
        if self._dark is None :
            return color(rgb=self(self.get_node(0.25)))
        return color(auto=self._dark)

    _light = None #light color
    @prop(variable=True)
    def light(self) -> str :
        if self._light is None :
            return color(rgb=self(self.get_node(0.75)))
        return color(auto=self._light)

    _colors = None #list of colors
    @prop()
    def colors(self) -> str :
        return [getattr(self, attr) for attr in ['black', 'dark', 'color', 'light', 'white'] if getattr(self, f'_{attr}') is not None]
    @colors.setter
    def colors(self, value) -> float :
        self._colors = [color(c) for c in value]
    @property
    def ncolors(self) :
        return len(self.colors)

    _nodes = None #nodes corresponding to colors
    @prop()
    def nodes(self) -> str :
        if self._colors is not None :
            nodes = np.linspace(0.,1.,self.ncolors)
        else :
            nodes = np.asarray([0.25 * pos for pos, attr in enumerate(['black', 'dark', 'color', 'light', 'white']) if getattr(self, f'_{attr}') is not None])
        return self.get_node(nodes)
    nodebase = 0 #Base defining distribution of colors around center based on erf function, when approching 0 the function tends towards linear distribution
    def get_node(self,node) :
        if self.nodebase == 0 : return node
        node = node * 2 * erf(self.nodebase) - erf(self.nodebase)
        node = (erfinv(node)/self.nodebase + 1) / 2
        return (np.round(node * 1000)).astype(int)/1000



cmaps = {

    'cmapLP' : Cmap(name='cmapLP', colors=['black', 'blueLP', 'coldLP', 'greenLP', 'yellowLP', 'warmLP', 'redLP', 'white']),
    'coldLP' : Cmap(name='coldLP', nodebase=2, dark='blueLP', light='greenLP'),
    'warmLP' : Cmap(name='warmLP', nodebase=2, dark='redLP', light='yellowLP'),
    'gradientLP' : Cmap(name='gradientLP', colors=['black', 'darkblueLP', 'darkcoldLP', 'darkgreenLP', 'darkyellowLP', 'lightwarmLP', 'xxlightredLP', 'white']),
    'convergingLP' : Cmap(name='convergingLP', colors=['black', 'blueLP', 'greenLP', 'white', 'yellowLP', 'redLP', 'black']),
    'divergingLP' : Cmap(name='divergingLP', colors=['white', 'greenLP', 'blueLP', 'black', 'redLP', 'yellowLP', 'white']),
    'rainbowLP' : Cmap(name='rainbowLP', colors=[color(wl=wl) for wl in np.linspace(380,750,100)]),

    }



# Register cmaps
for name, cmap2register in cmaps.items() :
    version = matplotlib.__version__.split('.')
    major, minor = int(version[0]), int(version[1])

    # Newer matplotlib ≥3.7
    if major > 3 or (major == 3 and minor >= 7):
        plt.colormaps.register(cmap2register, name=name)
    # Older matplotlib 3.4–3.6
    elif major == 3 and minor >= 4:
        cm.register_cmap(name=name, cmap=cmap2register)
    # Really old matplotlib <3.4
    else:
        cm.cmap_d[name] = cmap2register



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)