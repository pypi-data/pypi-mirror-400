#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : StyledAxes

"""
A class using stored styles inside.
"""



# %% Libraries
from matplotlib.axes import Axes
from matplotlib import pyplot as plt
import matplotlib.projections as projections
import inspect
from corelp import prop
import numpy as np
from matplotlib.patches import Rectangle
from mpl_toolkits.axes_grid1.inset_locator import inset_axes



# %% Class
class StyledAxes(Axes) :
    f'''
    A class using stored styles inside.
    
    Attributes
    ----------
    style : dict
        associated figure style.
    polish_imscale : bool
        True to polish automatically imscale
    polish_grids : bool
        True to polish automatically grids
    polish_noborder : bool
        True to polish automatically no boders
    polish_equiscale : bool
        True to polish automatically equiscale

    Examples
    --------
    >>> from plotlp import subplots
    ...
    >>> fig, axes = subplots(nrows=2, ncols=2) # StyledFigure, StyledAxes
    >>> axis = fig.axis # StyledAxes, current axis of fig
    >>> axis.polish() # applies all the polish methods for all the "polish_attr" attributes
    >>> axis.grids() # applies the polish grids, adds major and minor grids
    >>> axis.imscale() # applies the polish imscale, sets x and y limits to images borders
    >>> axis.noborder() # applies the polish no border, removes axis borders
    >>> axis.equiscale() # applies the polish equiscale, x and y unit have same size on plot
    >>> axis.implot(image, x, y, w, h) # plots an image to the coordinates, deformes to fit the box defined
    '''

    name = "styled"
    @property
    def style(self) :
        return self.figure.style

    # Imshow
    def imshow(self, X, *args, barname=None, coordinates=None, **kwargs) :
        with plt.style.context(self.style):
            if coordinates is not None :
                x, y = coordinates
                dx, dy = (x[-1]-x[0]) / (len(x)-1) / 2, (y[-1]-y[0]) / (len(y)-1) / 2
                extent = [x[0]-dx, x[-1]+dx, y[0]-dy, y[-1]+dy]
                kwargs.update(dict(extent=extent, aspect='auto', origin='lower'))
            im = super().imshow(X, *args, **kwargs)
            if coordinates is not None :
                self.invert_yaxis()
                Ny, Nx = X.shape
                self.set_box_aspect(Ny / Nx)
                self.polish_axis = False
            if barname is not None :
                self.figure.colorbar(im, barname=barname)

            return im
    
    # Pcolormesh
    def pcolormesh(self, *args, cmap=None, **kwargs):
        with plt.style.context(self.style):
            if cmap is None:
                cmap = plt.get_cmap(plt.rcParams['image.cmap'])
            return super().pcolormesh(*args, cmap=cmap, **kwargs)

    # Implot
    def implot(self, img, x, y, w, h, zorder=3, **kwargs) :
        newaxe = inset_axes(self, [x, y, w, h], transform=self.transData, zorder=zorder, axes_class=StyledAxes)
        newaxe.set_axis_off()
        kw = {'aspect':'auto','extent':[x, x+w, y, y+h],'origin':'lower'}
        kw.update(kwargs)
        im = newaxe.imshow(img, **kw)
        clip_rect = Rectangle((0, 0), 1, 1, transform=self.transAxes, facecolor="none")
        im.set_clip_path(clip_rect)
        return im


### --- Polish functions ---



    polish_axis = True
    def polish(self) :
        if not self.polish_axis : return
        if self.polish_grids : self.grids()
        if self.polish_imscale : self.imscale()
        if self.polish_noborders : self.noborders()
        if self.polish_equiscale : self.equiscale()

    # grids
    @prop()
    def polish_grids(self) :
        return len(self.lines) > 0 or len(self.collections) > 0
    grid_major = {'linestyle':'-', 'alpha':1}
    grid_minor = {'linestyle':'--', 'alpha':0.5}
    def grids(self) :
        with plt.style.context(self.style) :
            if self.grid_major is not None and len(self.grid_major) > 0 :
                self.grid(which='major',**self.grid_major)
            if self.grid_minor is not None and len(self.grid_minor) > 0 :
                self.minorticks_on() # force enabling minor ticks
                self.grid(which='minor',**self.grid_minor)

    # imscale
    @prop()
    def polish_imscale(self) :
        return len(self.get_images()) > 0
    def imscale(self) :
        with plt.style.context(self.style) :
            xmax, ymax = 0, 0
            for image in self.get_images() : # Get maximum image coordinates
                y, x = np.shape(image.get_array())[0:2]
                ymax, xmax = max(y, ymax), max(x, xmax)
            if self.get_autoscalex_on() :
                self.set_xlim(-0.5, xmax - 0.5)
            if self.get_autoscaley_on() :
                self.set_ylim(ymax - 0.5, -0.5)

    # noborders
    @prop()
    def polish_noborders(self) :
        return not self.polish_grids
    def noborders(self) :
        with plt.style.context(self.style) :
            self.set_axis_off()

    # equiscale
    @prop()
    def polish_equiscale(self) :
        return False
    def equiscale(self) :
        with plt.style.context(self.style) :
            self.set_aspect(aspect='equal', adjustable='box')
    


### --- Regenerate parent class methods in the given style ---



def is_plottable(method_name, method_obj):
    """
    Returns True if this method should be wrapped automatically.
    """
    if hasattr(StyledAxes, method_name): # Already overriden
        return False
    if method_name.startswith("_"):      # private
        return False                # handled separately
    if not callable(method_obj):
        return False
    if not inspect.ismethoddescriptor(method_obj) and not inspect.isfunction(method_obj):
        return False
    # Heuristic: methods returning artists / sequences of artists
    # Usually are plotting methods; we accept them all here
    return True

def wrap_method(method_name):
    """
    Returns a wrapper method that applies the style context
    then calls the parent Axes method.
    """
    def wrapper(self, *args, **kwargs):
        with plt.style.context(self.style):
            method = getattr(super(StyledAxes, self), method_name)
            return method(*args, **kwargs)
    wrapper.__name__ = method_name
    return wrapper

# Dynamically inject each wrapper method into StyledAxes
for name, obj in Axes.__dict__.items():
    if is_plottable(name, obj):
        setattr(StyledAxes, name, wrap_method(name))

# Finally register projection
projections.register_projection(StyledAxes)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)