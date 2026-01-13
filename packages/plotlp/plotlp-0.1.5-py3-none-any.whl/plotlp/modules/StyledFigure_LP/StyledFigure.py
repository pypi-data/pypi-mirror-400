#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Date          : 2025-12-11
# Author        : Lancelot PINCET
# GitHub        : https://github.com/LancelotPincet
# Library       : plotLP
# Module        : StyledFigure

"""
A class defining figures with custom styles included inside.
"""



# %% Libraries
from matplotlib.figure import Figure
from matplotlib import pyplot as plt
import numpy as np
from plotlp import style as get_style
from plotlp import StyledAxes # do not remove even if unused
from mpl_toolkits.axes_grid1 import make_axes_locatable
from corelp import selfkwargs, prop
import gc
from io import BytesIO
from pathlib import Path
from PIL import Image
import string



# %% Class
class StyledFigure(Figure) :
    f'''
    A class defining figures with custom styles included inside.
    
    Parameters
    ----------
    figsize : tuple
        figure size [inch] (x, y).
    dpi : int
        Dots Per Inch resolution.
    style : str or dict
        Name of style or corresponding dict.
    lightmode : bool
        True to use lightLP style.
    darkmode : bool
        True to use darkLP style.
    kwargs : dict
        Keyword arguments corresponding to attributes to change.

    Attributes
    ----------
    axis : property
        set as an index, when gotten returns corresponding axis.
    plot_axes : list
        list of plotting axes.
    naxes : int
        Number of plotting axes.
    figsize_default : tuple
        Default figure size (x, y) in inch.
    figsize_ratio : float
        x/y figure size ratio, while keeping the same area as default figsize.
    figsize_fact : tuple
        (x, y) figure size growing factors.
    title : property
        suptitle applied and to apply when set.
    tight : bool
        True to apply tight layout when polishing.

    Examples
    --------
    >>> from plotlp import figure, plt
    ...
    >>> fig = figure() # Savefigure output
    >>> plt.imshow(image, barname='My colorbar') # Apply barname to auto createe colorbar
    >>> fig.polish() # Applies StyledAxes automatic polishing on each axis
    >>> fig.arrayfig(close=False) # Saves figure into an numpy array (calls fig.savefig, close=False to not close figure)
    >>> plt.savefig(png_path=png_path, close=False, **savefig_kwargs) # saving png only
    >>> plt.savefig(pdf_path=pdf_path, close=False, **savefig_kwargs) # saving pdf only
    >>> plt.savefig(path, **savefig_kwargs) # saving png and pdf automatically, close=True by default so no more figure after
    '''

    def __init__(self, figsize=None, dpi=None, *, style=None, darkmode=False, lightmode=False, **kwargs):

        # Style
        if style is not None :
            self.style = style
        elif lightmode : self.lightmode()
        elif darkmode : self.darkmode()
        else :
            self.style

        # Init
        with plt.style.context(self.style) :
            super().__init__(figsize, dpi)
            selfkwargs(self, kwargs)
        self.figresize()



    #Style
    style_name = 'lightLP'
    _style = None #style dict
    style_kwargs = {}
    @property
    def style(self) :
        if self._style is None :
            self.style = self.style_name
        return self._style
    @style.setter
    def style(self,value) :
        if isinstance(value,str) :
            self.style_name = value
            self._style = get_style(value)
        else :
            self.style_name = None
            self._style = value
        self._style.update(self.style_kwargs)
    def lightmode(self) : #to auto call lightmode
        self.style = 'lightLP'
    def darkmode(self) : #to auto call darkmode
        self.style = 'darkLP'



    #Axe
    axis_num = 0 #index of axes

    @property
    def axis(self) :
        return self.plot_axes[self.axis_num]
    @axis.setter
    def axis(self,value) :
        self.axis_num = value
        plt.sca(self.plot_axes[self.axis_num])

    @property
    def naxes(self) :
        return len(self.plot_axes)

    @property
    def plot_axes(self) :
        return [ax for ax in self.axes if not getattr(ax, "is_cbar", False)]

    def add_subplot(self, *args, **kwargs):
        with plt.style.context(self.style) :
            kwargs["projection"] = "styled"   # force the Axes type
            return super().add_subplot(*args, **kwargs)
    def add_axes(self, *args, **kwargs):
        with plt.style.context(self.style) :
            return super().add_axes(*args, **kwargs)



    # Paper index
    paper_index_kwargs = {'size': 20, 'weight': 'bold'}
    def paper_index(self, axes=None, **kwargs) :
        with plt.style.context(self.style) :
            if axes is None :
                axes = self.plot_axes
            kw = self.paper_index_kwargs.copy()
            kw.update(kwargs)
            for n, ax in enumerate(axes):
                ax.text(-0.1, 1.1, string.ascii_lowercase[n], transform=ax.transAxes, **kw)



    # Colorbar
    barname = {'rotation':270,'labelpad':10}
    cax = {'size':"5%", 'pad':0.05}
    def colorbar(self, mappable, cax=None, ax=None, barname=None, **kwargs) :
        with plt.style.context(self.style) :
            if cax is None :
                if ax is None :
                    ax = mappable.axes
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", **self.cax)
                cax.is_cbar = True
            cbar = super().colorbar(mappable=mappable, cax=cax, ax=None, **kwargs)
            if barname is not None :
                cbar.ax.set_ylabel(barname, **self.barname)
            return cbar



    #figure size parameter
    @prop()
    def figsize_default(self) :
        return self.get_size_inches()

    @prop()
    def figsize_ratio(self) :
        x, y = self.figsize_default
        return x / y

    @prop()
    def figsize_fact(self) :
        return 1., 1.

    def figresize(self) :
        default = self.figsize_default
        ratio = self.figsize_ratio
        fact = self.figsize_fact
        area = default[0] * default[1]
        y = np.sqrt(area/ratio)
        x = ratio * y
        self.set_size_inches(x * fact[0], y * fact[1])
        self._figsize_default = None
        self._figsize_ratio = None
        self._figsize_fact = None



    # Title
    @property
    def title(self) :
        if getattr(self, '_title', None) is None :
            return None
        return self._title.get_text()
    @title.setter
    def title(self, value) :
        with plt.style.context(self.style) :
            self._title = self.suptitle(value)



    # Polish
    tight = True
    polish_figure = True
    def polish(self) :
        with plt.style.context(self.style) :
            for axis_num in range(self.naxes) :
                self.axis = axis_num
                self.axis.polish()
            if self.tight :
                self.tight_layout()



    # Savefig
    def savefig(self, path=None, *, polish=None, path_png=None, path_pdf=None, close=True, **kwargs) :
        if polish is True or polish is None and self.polish_figure :
            self.polish()

        with plt.style.context(self.style) :

            # Saving in array
            if isinstance(path, BytesIO) :
                super().savefig(path, **kwargs)
        
            # Saving in file
            else :
                path_png = Path(path_png) if path_png is not None else Path(path) if path is not None and path.suffix != '.pdf' else None
                path_pdf = Path(path_pdf) if path_pdf is not None else Path(path) if path is not None and path.suffix != '.png'  else None
        
                if path_png is not None :
                    super().savefig(path_png.with_suffix('.png'), **kwargs)
                if path_pdf is not None :
                    super().savefig(path_pdf.with_suffix('.pdf'), **kwargs)
        
            # Close figure
            if close :
                plt.close(self)
                gc.collect()



    #Arrayfig
    def arrayfig(self, *args, **kwargs) :
        '''
        Converts figure into a numpy array
        '''
        with plt.style.context(self.style) :
            with BytesIO() as buf:
                self.savefig(buf, *args, **kwargs)
                buf.seek(0)
                image = Image.open(buf)
                image_np = np.array(image)
            return image_np



    #Show
    def show(self, *args, **kwargs) :
        with plt.style.context(self.style) :
            super().show(*args,**kwargs)



# %% Test function run
if __name__ == "__main__":
    from corelp import test
    test(__file__)