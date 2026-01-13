# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 19:42:45 2025

@author: anba
"""
import numpy as np
from matplotlib.ticker import LogLocator
from typing import Optional, Sequence

from .utils_dfsu2d import DfsuUtils2D
from .adcp import ADCP as ADCPDataset
from .utils_crs import CRSHelper
from .utils_shapefile import ShapefileLayer

def index_of_agreement(p, o, version='refined'):
    """
    Calculates the Index of Agreement (IOA) based on Willmott's formulations.
    
    Parameters:
    p (array): Model-predicted values
    o (array): Observed values
    version (str): 'original' (d), 'absolute' (d1), or 'refined' (dr)
    """
    p = np.array(p)
    o = np.array(o)
    o_bar = np.nanmean(o)
    
    if version == 'original':
        # Original squared version (d) [3-5]
        numerator = np.nansum((p - o)**2)
        denominator = np.nansum((np.abs(p - o_bar) + np.abs(o - o_bar))**2)
        return 1 - (numerator / denominator)

    elif version == 'absolute':
        # Absolute version (d1) [6, 7]
        numerator = np.nansum(np.abs(p - o))
        denominator = np.nansum(np.abs(p - o_bar) + np.abs(o - o_bar))
        return 1 - (numerator / denominator)

    elif version == 'refined':
        # Refined version (dr) from 2012 paper [8]
        # Uses a scaling factor of c = 2
        c = 2
        sum_abs_err = np.nansum(np.abs(p - o))
        sum_obs_dev = np.nansum(np.abs(o - o_bar))
        
        comparison_basis = c * sum_obs_dev
        
        if sum_abs_err <= comparison_basis:
            return 1 - (sum_abs_err / comparison_basis)
        else:
            return (comparison_basis / sum_abs_err) - 1

def mt_model_transect_comparison(
    mt_model: DfsuUtils2D,
    adcp: ADCPDataset,
    crs_helper: CRSHelper,
    shapefile_layers: Optional[Sequence[ShapefileLayer]] = None,

    # --- ADCP ---
    adcp_series_mode: str = "bin",                # "bin" | "depth" | "hab"
    adcp_series_target: str = "mean",             # "mean" | "pXX"
    adcp_transect_color: str = "magenta",
    

    # --- SSC ---
    ssc_item_number: int = 1,
    ssc_scale: str = "log",                           # "log" or "normal"
    ssc_levels: list[float] = (0.01, 0.1, 1.0, 10.0, 100.0),
    ssc_vmin: float | None = None,                    # mg/L
    ssc_vmax: float | None = None,                    # mg/L
    ssc_cmap_name: str = "turbo",
    ssc_bottom_thresh: float = 0.01,
    ssc_pixel_size_m: float = 10.0,                   # Raster resolution
    
    # --- Layout ---
    cbar_tick_decimals: int = 2,
    axis_tick_decimals: int = 3,
    pad_m: float = 2000.0,
    distance_bin_m: float = 50.0,
    bar_width_scale: float = 0.15,
    
):
    """
    Plot MT model vs. ADCP transect comparison with three stacked subplots:
      1) Top: Map of model SSC raster with ADCP track and optional shapefile overlays.
      2) Middle: Distance-binned bar chart (Model vs ADCP).
      3) Bottom: Metadata columns.

    Parameters
    ----------
    mt_model : DfsuUtils2D
        Preloaded model object. Must provide:
        - rasterize_idw_bbox(item_number, bbox, t, pixel_size_m) -> (array, extent)
        - extract_transect(xq, yq, t, item_number) -> (time_series, ...)
    adcp : ADCPDataset
        Preloaded ADCP object. Must provide:
        - position.x, position.y, position.distance, position.epsg
        - time.ensemble_datetimes
        - get_beam_series(field_name, mode, target) -> (series, meta)
        - name
    crs_helper : CRSHelper
        Must provide:
        - bbox_from_coords(x, y, pad_m, from_crs) -> [xmin, xmax, ymin, ymax]
        - axis_labels() -> (x_label, y_label)
    ssc_item_number : int, optional
        DFSU item number for SSC extraction.
    ssc_scale : {"log","normal"}, optional
        Color and y-axis scale for SSC.
    ssc_vmin, ssc_vmax : float | None, optional
        Colorbar min/max in mg/L. Defaults derive from `levels` or data.
    ssc_levels : list[float], optional
        Colorbar ticks in mg/L. Always includes the lower bound tick.
    ssc_cmap_name : str, optional
        Matplotlib colormap name.
    cbar_tick_decimals : int, optional
        Colorbar tick label precision.
    axis_tick_decimals : int, optional
        X/Y tick label precision for map and middle plot.
    pad_m : float, optional
        Padding in meters for the bbox around the transect.
    ssc_pixel_size_m : float, optional
        Rasterization resolution in meters.
    ssc_bottom_thresh : float, optional
        Values below this are transparent on the map. Also the lower bound for log plots.
    adcp_transect_color : str, optional
        Line color for the ADCP transect on the map.
    distance_bin_m : float, optional
        Bin width in meters for distance-binned bars.
    bar_width_scale : float, optional
        Relative bar width factor for middle plot (0–1).
    adcp_series_mode, adcp_series_target : str, optional
        ADCP aggregation configuration passed to `get_beam_series`.
    shapefile_layers : list[ShapefileLayer] | None, optional
        Optional overlays. Each layer must implement .plot(ax).

    Returns
    -------
    fig : matplotlib.figure.Figure
    axes : tuple[matplotlib.axes.Axes, matplotlib.axes.Axes, matplotlib.axes.Axes]
        (ax0, ax1, ax2)
    """
    # ============================= Internal constants (layout) =============================
    FIG_W, FIG_H = 6.5, 9.0
    LEFT, RIGHT = 0.06, 0.96
    TOP, BOTTOM = 0.98, 0.05
    HSPACE = 0.22
    CB_WIDTH = 0.012          # colorbar width (figure fraction)
    CB_GAP = 0.008            # gap between colorbar axis and figure edge

    # metadata spacing
    META_TOP_Y = 0.95
    META_SECTION_GAP = 0.20
    META_LINE_GAP = 0.16
    META_COL_X = [0.02, 0.43, 0.84]
    META_LEFT_OVERSHOOT = 0.10

    # ============================== Imports used inside ==============================
    import numpy as _np
    import pandas as _pd
    import matplotlib.pyplot as _plt
    from matplotlib import ticker as _mticker
    from matplotlib.colors import LogNorm as _LogNorm, Normalize as _Normalize
    from .plotting import PlottingShell as _PlottingShell

    # ============================== Data aliases ==============================
    xq = adcp.position.x
    yq = adcp.position.y
    t = adcp.time.ensemble_datetimes
    x_label, y_label = crs_helper.axis_labels()
    overlays = shapefile_layers or []

    # ============================== Figure shell ==============================
    fig, ax = _PlottingShell.subplots(
        figheight=FIG_H,
        figwidth=FIG_W,
        nrow=3,
        ncol=1,
        height_ratios=[1.00, 0.30, 0.22],
    )
    fig.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM, hspace=HSPACE)
    ax0, ax1, ax2 = ax

    # ======================================================================
    # TOP — Model SSC raster (mg/L)
    # ======================================================================
    bbox = crs_helper.bbox_from_coords(xq, yq, pad_m=pad_m, from_crs=adcp.position.epsg)
    model_img = mt_model.rasterize_idw_bbox(
        item_number=ssc_item_number, bbox=bbox, t=t, pixel_size_m=ssc_pixel_size_m
    )
    model_ssc_img = _np.asarray(model_img[0], dtype=float) * 1000.0  # mg/L
    model_extent = model_img[1]

    finite = _np.isfinite(model_ssc_img)
    if not finite.any():
        raise ValueError("No finite SSC values in model raster.")

    auto_min = float(_np.nanmin(model_ssc_img[finite]))
    auto_max = float(_np.nanmax(model_ssc_img[finite]))
    cbar_min = ssc_vmin if ssc_vmin is not None else (min(ssc_levels) if ssc_levels else max(ssc_bottom_thresh, auto_min))
    cbar_max = ssc_vmax if ssc_vmax is not None else (max(ssc_levels) if ssc_levels else auto_max)
    cbar_min = max(ssc_bottom_thresh, cbar_min)
    if (not _np.isfinite(cbar_min)) or (not _np.isfinite(cbar_max)) or (cbar_min >= cbar_max):
        cbar_min, cbar_max = max(ssc_bottom_thresh, 0.01), max(ssc_bottom_thresh * 100.0, 100.0)

    cmap = _plt.get_cmap(ssc_cmap_name).copy()
    cmap.set_under(alpha=0.0)
    norm = _LogNorm(vmin=cbar_min, vmax=cbar_max, clip=True) if ssc_scale.lower() == "log" \
        else _Normalize(vmin=cbar_min, vmax=cbar_max, clip=True)

    im = ax0.imshow(
        model_ssc_img,
        extent=model_extent,
        origin="lower",
        cmap=cmap,
        norm=norm,
        interpolation="nearest",
    )

    for layer in overlays:
        layer.plot(ax0)

    ax0.plot(xq, yq, color=adcp_transect_color, lw=1.0, alpha=0.9)
    ax0.set_xlabel(x_label)
    ax0.set_ylabel(y_label)

    xmin, xmax, ymin, ymax = bbox
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(ymin, ymax)
    ax0.set_aspect("equal", adjustable="box")
    ax0.set_title(f"Model Comparison to ADCP Transect {adcp.name}", fontsize=8)

    xy_fmt = _mticker.FuncFormatter(lambda v, pos: f"{v:.{axis_tick_decimals}f}")
    ax0.xaxis.set_major_formatter(xy_fmt)
    ax0.yaxis.set_major_formatter(xy_fmt)

    # --- Colorbar axis placed with a gap from the figure edge ---
    fig.canvas.draw()
    pos0 = ax0.get_position()
    ax0.set_position([pos0.x0, pos0.y0, pos0.width - (CB_WIDTH + CB_GAP), pos0.height])
    fig.canvas.draw()
    pos = ax0.get_position()

    cb_ax = fig.add_axes([pos.x1 + CB_GAP, pos.y0, CB_WIDTH, pos.height])
    cb = _plt.colorbar(im, cax=cb_ax)
    # ABJA Start
    # build tick list once
    tick_list = sorted(set(list(ssc_levels) + [cbar_min])) if ssc_levels else [cbar_min]    
    tick_list = [v for v in tick_list if cbar_min <= v <= cbar_max]                   
    if ssc_scale.lower() == "log":
        # log colorbar: use a LogLocator and plain numeric labels
        cb.locator = LogLocator(base=10.0, subs=(1.0,))  # decades only; tweak subs if needed
        if tick_list:
            cb.locator = _mticker.FixedLocator(tick_list)
        cb.formatter = _mticker.FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}f}")
        cb.update_ticks()
    else:
        # FORCE linear behavior explicitly
        cb.ax.set_yscale("linear")
        if tick_list:
            cb.locator = _mticker.FixedLocator(tick_list)
        else:
            cb.locator = _mticker.MaxNLocator(nbins=5)
        cb.formatter = _mticker.ScalarFormatter(useOffset=False, useMathText=False)
        cb.update_ticks()
    # ABJA End
    cb.ax.set_ylabel("Mean SSC During Transect (mg/L)", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    def _fmt_num(val: float, nd: int) -> str:
        return f"{val:.{nd}f}"

    tick_list = sorted(set(list(ssc_levels) + [cbar_min])) if ssc_levels else [cbar_min]
    tick_list = [v for v in tick_list if cbar_min <= v <= cbar_max]
    if tick_list:
        cb.set_ticks(tick_list)
        cb.set_ticklabels([_fmt_num(v, cbar_tick_decimals) for v in tick_list])
    else:
        cb_ticks = _np.linspace(cbar_min, cbar_max, 5)
        cb.set_ticks(cb_ticks)
        cb.set_ticklabels([_fmt_num(v, cbar_tick_decimals) for v in cb_ticks])

    # Legend for ADCP track (solid white background, on top)
    from matplotlib.lines import Line2D
    
    _track = Line2D([0], [0], color=adcp_transect_color, lw=1.2)
    leg = ax0.legend([_track], ["ADCP track"],
                     loc="upper left", frameon=True, fontsize=7,
                     framealpha=1.0, fancybox=False)
    
    frame = leg.get_frame()
    frame.set_facecolor("white"); frame.set_alpha(1.0); frame.set_edgecolor("black")
    leg.set_zorder(1000); frame.set_zorder(1001)


    # ======================================================================
    # MIDDLE — Distance-binned SSC (Model vs ADCP)
    # ======================================================================
    model_transect = mt_model.extract_transect(xq, yq, t, item_number=ssc_item_number)
    model_ssc_ts = _np.asarray(model_transect[0], dtype=float) * 1000.0  # mg/L

    adcp_series = adcp.get_beam_series(
        field_name="suspended_solids_concentration",
        mode=adcp_series_mode,
        target=adcp_series_target,
    )
    adcp_ssc_ts = _np.asarray(adcp_series[0], dtype=float)

    dist_m = _np.asarray(adcp.position.distance, dtype=float).ravel()

    n = min(dist_m.size, model_ssc_ts.size, adcp_ssc_ts.size)
    dist_m = dist_m[:n]
    model_ssc_ts = model_ssc_ts[:n]
    adcp_ssc_ts = adcp_ssc_ts[:n]

    valid = _np.isfinite(dist_m) & _np.isfinite(model_ssc_ts) & _np.isfinite(adcp_ssc_ts)
    dist_m = dist_m[valid]
    model_ssc_ts = model_ssc_ts[valid]
    adcp_ssc_ts = adcp_ssc_ts[valid]
    if dist_m.size == 0:
        raise ValueError("No valid samples for distance binning.")

    dmax = float(_np.nanmax(dist_m))
    edges = _np.arange(0.0, dmax + distance_bin_m, distance_bin_m)
    if edges.size < 2:
        end_right = max(distance_bin_m, dmax if _np.isfinite(dmax) else distance_bin_m)
        edges = _np.array([0.0, end_right], dtype=float)

    centers = 0.5 * (edges[:-1] + edges[1:])
    def _generate_labels(dmax):
        if dmax <= 0:
            return [0.0]

        # determine step size
        if dmax < 50:
            step = 10
        elif dmax < 100:
            step = 20
        elif dmax < 500:
            step = 50
        elif dmax < 1000:
            step = 100
        elif dmax < 5000:
            step = 500
        else:
            step = 1000

        # generate values
        values = [round(i * step, 1) for i in range(int(dmax // step) + 1)]

        # ensure dmax is included
        dmax_rounded = round(dmax, 1)
        if values[-1] != dmax_rounded:
            values.append(dmax_rounded)

        return values
    
    labels = _generate_labels(dmax)
    nbins = edges.size - 1
    bin_idx = _np.clip(_np.digitize(dist_m, edges) - 1, 0, nbins - 1)

    def _binned_mean(values: _np.ndarray, idx: _np.ndarray, nb: int) -> _np.ndarray:
        sums = _np.bincount(idx, weights=values, minlength=nb).astype(float)
        cnts = _np.bincount(idx, minlength=nb).astype(float)
        out = _np.full(nb, _np.nan, dtype=float)
        ok = cnts > 0
        out[ok] = sums[ok] / cnts[ok]
        return out

    model_bin_mean = _binned_mean(model_ssc_ts, bin_idx, nbins)
    adcp_bin_mean = _binned_mean(adcp_ssc_ts, bin_idx, nbins)

    bar_w = max(0.5, distance_bin_m * bar_width_scale)

    if ssc_scale.lower() == "log":
        m_plot = _np.where(_np.isfinite(model_bin_mean) & (model_bin_mean > 0.0), model_bin_mean, _np.nan)
        a_plot = _np.where(_np.isfinite(adcp_bin_mean) & (adcp_bin_mean > 0.0), adcp_bin_mean, _np.nan)
        m_plot = _np.where(m_plot < cbar_min, cbar_min, m_plot)
        a_plot = _np.where(a_plot < cbar_min, cbar_min, a_plot)
    else:
        m_plot = model_bin_mean
        a_plot = adcp_bin_mean

    ax1.bar(
        centers - bar_w / 2.0,
        m_plot,
        width=bar_w,
        color=_PlottingShell.blue1,
        alpha=0.9,
        label="Model",
        align="center",
    )
    ax1.bar(
        centers + bar_w / 2.0,
        a_plot,
        width=bar_w,
        color=_PlottingShell.red1,
        alpha=0.9,
        label="ADCP",
        align="center",
    )

    ax1.set_xlim(edges[0], edges[-1])
    ax1.set_xlabel("Distance along transect (m)")
    ax1.set_ylabel("SSC (mg/L)")
    ax1.grid(alpha=0.3)
    ax1.legend(frameon=False, fontsize=7, ncol=2)
    
    # ticks exactly at each bin center
    ax1.set_xticks(labels)
    ax1.set_xticklabels([f"{c:.1f}" for c in labels])  # or use your desired precision
    ax1.set_xlim(edges[0], edges[-1])
    ax1.xaxis.set_major_formatter(_mticker.FuncFormatter(lambda v, pos: f"{v:.1f}"))
    #ax1.yaxis.set_major_formatter(_mticker.FuncFormatter(lambda v, pos: f"{v:.{tick_decimal_precision}f}"))
    # ABJA Start: force y-scale and limits here
    # ensure we never carry over a previous log setting
    if ssc_scale.lower() == "log":
        ax1.set_yscale("log")
        ax1.set_ylim(cbar_min, cbar_max)
    else:
        ax1.set_yscale("linear")
        ax1.set_ylim(0.0, cbar_max)

    # y-ticks: derive from levels when provided; otherwise fallback by scale
    from matplotlib.ticker import FixedLocator, NullLocator

    _y_ticks = [v for v in ssc_levels if (v > 0) and (cbar_min <= v <= cbar_max)]
    if not _y_ticks:
        _y_ticks = _np.geomspace(cbar_min, cbar_max, 5) if ssc_scale.lower() == "log" else _np.linspace(0.0, cbar_max, 5)

    ax1.yaxis.set_major_locator(FixedLocator(_y_ticks))
    ax1.yaxis.set_minor_locator(NullLocator())  # no minor ticks
    ax1.yaxis.set_major_formatter(_mticker.FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}f}"))
    # ABJA End
        
        
    # Match middle width to top; ensure rectangular, not square
    fig.canvas.draw()
    p0 = ax0.get_position()
    p1 = ax1.get_position()
    ax1.set_aspect("auto")
    ax1.set_anchor("W")
    try:
        ax1.set_box_aspect(None)
    except Exception:
        pass
    ax1.set_position([p0.x0, p1.y0, p0.width, p1.height])

    # Middle y-limit matches colorbar max for comparability
    if ssc_scale.lower() == "log":
        ax1.set_yscale("log")
        ax1.set_ylim(cbar_min, cbar_max)
    else:
        ax1.set_ylim(0.0, cbar_max)
    # --- Force plain numeric y-ticks on the middle subplot (log or linear) ---
    from matplotlib.ticker import FixedLocator, FuncFormatter
    
    # choose ticks from your colorbar 'levels' and clip to [cbar_min, cbar_max]
    _y_ticks = [v for v in ssc_levels if (v > 0) and (cbar_min <= v <= cbar_max)]
    if not _y_ticks:
        _y_ticks = np.geomspace(cbar_min, cbar_max, 5) if ssc_scale.lower() == "log" else np.linspace(cbar_min, cbar_max, 5)
    
    # apply AFTER ax1.set_yscale(...) and ax1.set_ylim(...)
    ax1.yaxis.set_major_locator(FixedLocator(_y_ticks))
    ax1.yaxis.set_minor_locator(FixedLocator([]))  # no minor ticks
    ax1.yaxis.set_major_formatter(FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}f}"))
    
    
    # ======================================================================
    # BOTTOM — Metadata (three columns)
    # ======================================================================
    t_arr = _np.asarray(t)[:n]
    t_valid = t_arr[valid]
    t0 = _pd.to_datetime(t_valid.min())
    t1 = _pd.to_datetime(t_valid.max())
    dur_min = (t1 - t0).total_seconds() / 60.0

    # mean_model = float(_np.nanmean(model_ssc_ts))
    # mean_obs = float(_np.nanmean(adcp_ssc_ts))
    # mean_err = float(_np.nanmean(model_ssc_ts - adcp_ssc_ts))
    MAE = float(_np.nanmean(_np.abs(model_ssc_ts - adcp_ssc_ts)))
    RMSE = float(_np.sqrt(_np.nanmean((model_ssc_ts - adcp_ssc_ts) ** 2)))
    IOA = index_of_agreement(model_ssc_ts, adcp_ssc_ts, version="original")

    ax2.clear()
    ax2.set_axis_off()

    def _fmt_time(dt):
        return dt.strftime("%d %b. %Y %H:%M")

    def _H(x, y, text):
        ax2.text(x, y, text, ha="left", va="top", fontsize=8, fontweight="bold", family="monospace")

    def _I(x, y, k, v):
        ax2.text(x, y, f"{k}: {v}", ha="left", va="top", fontsize=7, family="monospace")

    # Match bottom width to top, then overshoot further left
    fig.canvas.draw()
    p2 = ax2.get_position()
    ax2.set_aspect("auto")
    ax2.set_anchor("W")
    try:
        ax2.set_box_aspect(None)
    except Exception:
        pass
    new_x0 = p0.x0 - META_LEFT_OVERSHOOT
    new_w = min(p0.width + META_LEFT_OVERSHOOT, 1.0 - new_x0)
    ax2.set_position([new_x0, p2.y0, new_w, p2.height])

    y0_ax = META_TOP_Y
    sec = META_SECTION_GAP
    line = META_LINE_GAP
    cols_x = META_COL_X

    # Column 1
    x = cols_x[0]
    y = y0_ax
    _H(x, y, "Observation Aggregation")
    y -= sec
    _I(x, y, "Mode", adcp_series_mode)
    y -= line
    _I(x, y, "Target", adcp_series_target)

    # Column 2
    x = cols_x[1]
    y = y0_ax
    _H(x, y, "Transect Timing")
    y -= sec
    _I(x, y, "Start", _fmt_time(t0))
    y -= line
    _I(x, y, "End", _fmt_time(t1))
    y -= line
    _I(x, y, "Duration", f"{dur_min:.1f} min")

    # Column 3
    x = cols_x[2]
    y = y0_ax
    _H(x, y, "Model vs ADCP (SSC)")
    y -= sec
    # _I(x, y, "Mean error", f"{mean_err:.{cbar_tick_decimals}f} mg/L")
    # y -= line
    # _I(x, y, "Mean observed", f"{mean_obs:.{cbar_tick_decimals}f} mg/L")
    # y -= line
    # _I(x, y, "Mean simulated", f"{mean_model:.{cbar_tick_decimals}f} mg/L")
    # y -= line
    _I(x, y, "MAE", f"{MAE:.{cbar_tick_decimals}f} mg/L")
    y -= line
    _I(x, y, "RMSE", f"{RMSE:.{cbar_tick_decimals}f} mg/L")
    y -= line
    _I(x, y, "IOA", f"{IOA:.{cbar_tick_decimals}f}")

    return fig, (ax0, ax1, ax2)
