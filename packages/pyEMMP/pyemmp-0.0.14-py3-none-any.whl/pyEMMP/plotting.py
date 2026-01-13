import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.patheffects as mpl_path_effects
import os
from matplotlib.figure import Figure
from matplotlib.axes import Axes
from typing import Tuple, Union
from datetime import datetime
import matplotlib as mpl
import cycler


mpl.rcParams['font.size'] = 7
mpl.rcParams['lines.linewidth'] = 0.75
mpl.rcParams['patch.edgecolor'] = 'white'
mpl.rcParams['axes.grid.which'] = 'major'
mpl.rcParams['lines.markersize'] = 1
mpl.rcParams['ytick.labelsize'] = 7
mpl.rcParams['xtick.labelsize'] = 7
mpl.rcParams['ytick.labelright'] = False
mpl.rcParams['xtick.labeltop'] = False
mpl.rcParams['ytick.right'] = True
mpl.rcParams['xtick.top'] = True
mpl.rcParams['ytick.major.right'] = True
mpl.rcParams['xtick.major.top'] = True
mpl.rcParams['axes.labelweight'] = 'normal'
mpl.rcParams['legend.fontsize'] = 7
mpl.rcParams['legend.framealpha'] = 0.5
mpl.rcParams['axes.titlesize'] = 9
mpl.rcParams['axes.titleweight'] = 'normal'
mpl.rcParams['font.family'] = 'monospace'
mpl.rcParams['axes.labelsize'] = 7
mpl.rcParams['axes.linewidth'] = 0.5
mpl.rcParams['xtick.major.size'] = 5.0
mpl.rcParams['xtick.minor.size'] = 3.0
mpl.rcParams['ytick.major.size'] = 5.0
mpl.rcParams['ytick.minor.size'] = 3.0
mpl.rcParams['xtick.direction'] = 'in'
mpl.rcParams['ytick.direction'] = 'in'
        
class PlottingShell:
    # ---- class-level palettes so PlottingShell.blue1 works ----
    blue1   = '#04426e'; blue2   = '#4d9ab3'; blue3   = '#0493b2'; blue4   = '#c3dde5'
    green1  = '#01be62'; green2  = '#00b591'; green3  = '#6ad6af'
    gray1   = '#c4c4c4'; gray2   = '#8b8b8c'; gray3   = '#686c6e'
    red1    = '#c81f00'; red2    = '#ac1817'
    yellow1 = '#ffbb3c'; yellow2 = '#ebd844'
    orange1 = '#ec8833'; orange2 = '#d3741c'

    # exposed formats as class attrs too
    DATETIME_FORMAT = '%d-%b-%y %H:%M'
    DATE_FORMAT = '%d-%b-%y'
    TIME_FORMAT = '%H:%M'

    def __init__(self):
        # rcParams
        # color + linestyle cycle with alpha preserved
        base_colors = 2 * ['#283747', '#0051a2', '#41ab5d', '#feb24c', '#93003a']  # 10
        line_styles = 5 * ['-'] + 5 * ['--']                                       # 10
        alpha = 0.7
        rgba_colors = [mpl.colors.to_rgba(c, alpha) for c in base_colors]
        mpl.rcParams['axes.prop_cycle'] = (
            cycler.cycler(color=rgba_colors) + cycler.cycler(linestyle=line_styles)
        )

    @staticmethod
    def subplots3d(figheight: float = None,
                   figwidth: float = None,
                   nrow: int = None,
                   ncol: int = None,
                   sharex: bool = None,
                   sharey: bool = None,
                   width_ratios: list = None,
                   height_ratios: list = None) -> Tuple[Figure, Union[Axes, np.ndarray]]:
        """Create a 3D subplot figure with light grids."""
        default_size = 4.25 * (1 + (5 ** 0.5)) / 2
        figheight = default_size if figheight is None else figheight
        figwidth = default_size if figwidth is None else figwidth
        nrow = 1 if nrow is None else max(1, nrow)
        ncol = 1 if ncol is None else max(1, ncol)
        sharex = False if sharex is None else sharex
        sharey = False if sharey is None else sharey
        width_ratios = [1] * ncol if width_ratios is None else width_ratios
        height_ratios = [1] * nrow if height_ratios is None else height_ratios

        fig, ax = plt.subplots(
            figsize=(figwidth, figheight),
            nrows=nrow,
            ncols=ncol,
            gridspec_kw={'width_ratios': width_ratios, 'height_ratios': height_ratios},
            sharex=sharex,
            sharey=sharey,
            subplot_kw={'projection': '3d'}
        )

        if nrow == 1 and ncol == 1:
            ax.grid(alpha=0.25)
        else:
            for a in np.ravel(ax):
                a.grid(alpha=0.25)

        return fig, ax

    @staticmethod
    def subplots(figheight: float = None,
                 figwidth: float = None,
                 nrow: int = None,
                 ncol: int = None,
                 sharex: bool = None,
                 sharey: bool = None,
                 width_ratios: list = None,
                 height_ratios: list = None) -> Tuple[Figure, Union[Axes, np.ndarray]]:
        """Create a 2D subplot figure with light grids."""
        default_size = 4.25 * (1 + (5 ** 0.5)) / 2
        figheight = default_size if figheight is None else figheight
        figwidth = default_size if figwidth is None else figwidth
        nrow = 1 if nrow is None else max(1, nrow)
        ncol = 1 if ncol is None else max(1, ncol)
        sharex = False if sharex is None else sharex
        sharey = False if sharey is None else sharey
        width_ratios = [1] * ncol if width_ratios is None else width_ratios
        height_ratios = [1] * nrow if height_ratios is None else height_ratios

        fig, ax = plt.subplots(
            figsize=(figwidth, figheight),
            nrows=nrow,
            ncols=ncol,
            gridspec_kw={'width_ratios': width_ratios, 'height_ratios': height_ratios},
            sharex=sharex,
            sharey=sharey
        )

        return fig, ax

    @staticmethod
    def add_watermark(ax: Union[Axes, np.ndarray],
                      watermark_text: str,
                      add_date: bool = True) -> Union[Axes, np.ndarray]:
        """Add a faint centered watermark to one or many axes."""
        stroke = [mpl_path_effects.Stroke(linewidth=2, foreground="black", alpha=0.035)]
        axes = np.ravel(ax) if isinstance(ax, np.ndarray) else [ax]

        # resolve username safely
        try:
            user_str = os.getlogin()
        except Exception:
            try:
                import getpass
                user_str = getpass.getuser()
            except Exception:
                user_str = "user"

        stamp = f"{user_str}\n{datetime.now().strftime('%d/%m/%y %H:%M')}"

        for a in axes:
            a.text(0.5, 0.5, watermark_text,
                   transform=a.transAxes, fontsize=15, color='gray', alpha=0.1,
                   ha='center', va='center', path_effects=stroke,
                   fontname='Arial', zorder=1)
            if add_date:
                a.text(0.985, 0.02, stamp,
                       transform=a.transAxes, fontsize=6, color='black', alpha=0.4,
                       ha='right', va='bottom', weight='bold',
                       fontname='Arial', zorder=1)

        return ax