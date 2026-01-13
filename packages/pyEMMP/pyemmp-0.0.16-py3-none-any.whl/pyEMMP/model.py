from pathlib import Path
from typing import Union
import numpy as np
import os
import pandas as pd

from .utils import Utils, Constants
from .utils_dfsu import DfsuUtils
from .plotting import PlottingShell



class Model:
    def __init__(self, cfg: dict) -> None:
        self._cfg = cfg
        self.name: str = self._cfg.get("name", self._config_path.stem)
        self.fname: str = self._cfg.get("filename", None)
        self.dfsu = DfsuUtils(self.fname)
        self.plot = Plotting(self)


    # ------------------------------------------------------------------ #
    # Methods                                                            #
    # ------------------------------------------------------------------ #
    
    def extract_transect(self, x: np.ndarray, y: np.ndarray, t: np.ndarray, item_number: int) -> np.ndarray:
        """
        Extract a transect from the model data.
        Parameters
        ----------
        x : np.ndarray
            X coordinates of the transect points.
        y : np.ndarray
            Y coordinates of the transect points.
        t : np.ndarray
            Time values for the transect points.
        item_number : int
            Item number to extract from the model data.
        Returns
        -------
        np.ndarray
            Extracted transect data.
        """
        data, _, _ = self.dfsu.extract_transect(x=x, y=y, t=t, item_number=item_number)
        return data

    
    
from matplotlib.axes import Axes
import matplotlib.dates as mdates
import matplotlib.pyplot as plt

class Plotting:
    def __init__(self, model: Model) -> None:
        self.model = model


    def contourf(self, item_number: int, ax: Axes=None, cmap: str=None, cbar_label: str=None) -> Axes:
        """
        Plot a filled contour map from the model data.
        Parameters
        ----------
        item_number : int
            Item number to extract from the model data.
        ax : Axes, optional
            Matplotlib Axes object to plot on. If None, a new figure and axes will be created.
        cmap : str, optional
            Colormap to use for the plot. Defaults to 'turbo'.
        cbar_label : str, optional
            Label for the colorbar. If None, the item name will be used.
        Returns
        -------
        Axes
            The Axes object with the plot.
        """
        pass

    def transect(self, x: np.ndarray, y: np.ndarray, t: np.ndarray, item_number: int, ax: Axes=None, cmap: str=None, cbar_label: str=None) -> Axes:
        """
        Plot a transect from the model data.
        Parameters
        ----------
        x : np.ndarray
            X coordinates of the transect points.
        y : np.ndarray
            Y coordinates of the transect points.
        t : np.ndarray
            Time values for the transect points.
        item_number : int
            Item number to extract from the model data.
        """
        data, t, vertical_columns = self.model.dfsu.extract_transect(x=x, y=y, t=t, item_number=item_number)
        vert = vertical_columns[:, [0, -1]]
        ec = np.stack(self.model.dfsu.dfsu.CalculateElementCenterCoordinates()).T
        layer_fractions = self.model.dfsu.sigma_fractions
        Zs = ec[vert, 2]
        depth = Zs[:, 1] - Zs[:, 0]
        layer_bounds = np.concatenate(([0], np.cumsum(layer_fractions)))
        z_bounds = (Zs[:, 0] + depth * layer_bounds[:, None]).T
        t = t[:, np.newaxis].repeat(layer_fractions.shape[0]+1, axis=1)
        ylim = [np.min(Zs), np.max(Zs)]
        xlim = mdates.date2num(t)
        extent = [xlim[0], xlim[-1], ylim[0], ylim[-1]]
        vmin = np.nanmin(data)
        vmax = np.nanmax(data)
        origin = 'lower'
        cmap = cmap if cmap is not None else plt.cm.turbo
        cbar_label = cbar_label if cbar_label is not None else self.model.dfsu.dfsu.ItemInfo[item_number-1].Name
        if ax is None:
            fig, ax = PlottingShell.subplots(nrow=1, ncol=1, figheight=3, figwidth=10.5)
        else:
            fig = ax.figure
        
        ax = PlottingShell._mesh_plot(
            X=t,
            Y=z_bounds,
            C=data[1:, :],
            vmin=vmin,
            vmax=vmax,
            cmap=cmap,
            cbar_label=cbar_label,
            ax=ax,
        )

        return ax