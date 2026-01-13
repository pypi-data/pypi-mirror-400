# -*- coding: utf-8 -*-
"""
Created on Mon Sep  8 21:19:26 2025

@author: anba
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker as mticker
from matplotlib.colors import Normalize
from matplotlib.ticker import FixedLocator
from matplotlib.patches import FancyArrowPatch
from matplotlib.legend_handler import HandlerPatch
import cmocean as cmo
from typing import Tuple, List, Optional, Sequence

from .utils_dfsu2d import DfsuUtils2D
from .utils_xml import XMLUtils
from .adcp import ADCP as ADCPDataset
from .utils_crs import CRSHelper
from .plotting import PlottingShell
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

def plot_hd_vs_adcp_transect(
    hd_model: DfsuUtils2D,
    adcp: ADCPDataset,
    crs_helper: CRSHelper,
    shapefile_layers: Optional[Sequence[ShapefileLayer]] = None,
    
    # --- ADCP ---
    adcp_series_mode: str = "bin",          # 'bin' | 'range' | 'hab'
    adcp_series_target: str | float = "mean",
    adcp_transect_color: str = PlottingShell.red1,
    adcp_quiver_scale: float = 3,
    adcp_quiver_width: float = 0.002,
    adcp_quiver_headwidth: float = 2,
    adcp_quiver_headlength: float = 2.5,
    adcp_quiver_color: str = PlottingShell.red1,
    
    
    # --- Currents (field) ---
    u_item_number: int = 4,
    v_item_number: int = 5,
    model_field_pixel_size_m: float = 100,
    model_field_quiver_stride_n: int = 3,
    model_quiver_scale: float = 3,
    model_quiver_width: float = 0.002,
    model_quiver_headwidth: float = 2,
    model_quiver_headlength: float = 2.5,
    model_quiver_color: str = "black",
    
    model_quiver_mode: str = "field",       # 'transect' | 'field'
    
    model_levels = [0.0, .1, .2, .3, .4, .5],
    model_vmin: float | None = None,
    model_vmax: float | None = None,
    model_cmap_name = cmo.cm.speed,
    model_bottom_thresh: float = 0.001,
    
    pixel_size_m: float = 20,
    quiver_every_n: int = 5,
    
    # --- Layout ---
    cbar_tick_decimals: int = 2,
    axis_tick_decimals: int = 3,
    pad_m: float = 2000,
    distance_bin_m: float = 50,
    bar_width_scale: float = 0.15,
    
    
):
    """
    Packaged HD vs ADCP transect plot (map + distance bins + metadata).
    """
    import numpy as np
    import pandas as pd
    import matplotlib.pyplot as plt
    import matplotlib.ticker as mticker
    from matplotlib.colors import Normalize
    from matplotlib.ticker import FixedLocator
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.legend_handler import HandlerPatch
    FIG_W: float = 6.5
    FIG_H: float = 9.0
    LEFT: float = 0.06
    RIGHT: float = 0.9
    TOP: float = 0.98
    BOTTOM: float = 0.05
    HSPACE: float = 0.22
    CB_WIDTH: float = 0.012
    CB_GAP: float = 0.008
    META_TOP_Y: float = 0.95
    META_SECTION_GAP: float = 0.20
    META_LINE_GAP: float = 0.16
    META_COL_X = (0.02, 0.43, 0.84)
    META_LEFT_OVERSHOOT: float = 0.10
    # Transect coordinates and times from ADCP
    xq = np.asarray(adcp.position.x).ravel()
    yq = np.asarray(adcp.position.y).ravel()
    t  = adcp.time.ensemble_datetimes

    if shapefile_layers is None:
        x_label, y_label = crs_helper.axis_labels()
        shapefile_layers = [ShapefileLayer(
            path=r"\\usden1-stor.dhi.dk\Projects\61803553-05\GIS\SG Coastline\RD7550_CEx_SG_v20250509.shp",
            kind="polygon", crs_helper=crs_helper,
            poly_edgecolor="black", poly_linewidth=0.6,
            poly_facecolor="none", alpha=1.0, zorder=10)]
    else:
        x_label, y_label = crs_helper.axis_labels()

    # Figure shell
    fig, ax = PlottingShell.subplots(
        figheight=FIG_H, figwidth=FIG_W, nrow=3, ncol=1,
        height_ratios=[1.00, 0.30, 0.22]
    )
    fig.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM, hspace=HSPACE)
    ax0, ax1, ax2 = ax

    # -------------------- TOP MAP: speed raster + quivers
    bbox = crs_helper.bbox_from_coords(xq, yq, pad_m=pad_m, from_crs=adcp.position.epsg)

    U_img, extent_u  = hd_model.rasterize_idw_bbox(item_number=u_item_number, bbox=bbox, t=t, pixel_size_m=pixel_size_m)
    V_img, extent_v  = hd_model.rasterize_idw_bbox(item_number=v_item_number, bbox=bbox, t=t, pixel_size_m=pixel_size_m)
    if extent_u != extent_v:
        raise RuntimeError("U and V raster extents differ. Verify rasterization inputs.")
    speed_img    = np.hypot(U_img, V_img)
    model_extent = extent_u

    data   = np.asarray(speed_img, dtype=float)
    finite = np.isfinite(data)
    if not finite.any():
        raise ValueError("No finite speed values in model raster.")

    auto_min = float(np.nanmin(data[finite]))
    auto_max = float(np.nanmax(data[finite]))
    cbar_min = model_vmin if model_vmin is not None else (min(model_levels) if model_levels else max(model_bottom_thresh, auto_min))
    cbar_max = model_vmax if model_vmax is not None else (max(model_levels) if model_levels else auto_max)
    cbar_min = max(model_bottom_thresh, cbar_min)
    if (not np.isfinite(cbar_min)) or (not np.isfinite(cbar_max)) or (cbar_min >= cbar_max):
        cbar_min, cbar_max = max(model_bottom_thresh, 0.001), max(1.0, auto_max)

    cmap = plt.get_cmap(model_cmap_name) if isinstance(model_cmap_name, str) else model_cmap_name
    cmap = cmap.copy()
    cmap.set_under(alpha=0.0)
    norm = Normalize(vmin=cbar_min, vmax=cbar_max, clip=True)

    im = ax0.imshow(data, extent=model_extent, origin="lower", cmap=cmap, norm=norm, interpolation="nearest")
    for layer in shapefile_layers:
        layer.plot(ax0)

    # ADCP series
    adcp_u_ts, _ = adcp.get_velocity_series(component="u", mode=adcp_series_mode, target=adcp_series_target)
    adcp_v_ts, _ = adcp.get_velocity_series(component="v", mode=adcp_series_mode, target=adcp_series_target)

    # Model transect series
    model_u_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=u_item_number)[0], dtype=float)
    model_v_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=v_item_number)[0], dtype=float)

    # Model quivers
    if model_quiver_mode.lower() == "transect":
        idx = np.arange(0, xq.size, max(1, int(quiver_every_n)))
        ax0.quiver(xq[idx], yq[idx], model_u_ts[idx], model_v_ts[idx],
                   color=model_quiver_color, scale=model_quiver_scale, width=model_quiver_width, headwidth=model_quiver_headwidth, headlength=model_quiver_headlength,
                   alpha=0.9, zorder=20, label="Model")
    elif model_quiver_mode.lower() == "field":
        Uc, extent_c  = hd_model.rasterize_idw_bbox(item_number=u_item_number, bbox=bbox, t=t, pixel_size_m=model_field_pixel_size_m)
        Vc, extent_cv = hd_model.rasterize_idw_bbox(item_number=v_item_number, bbox=bbox, t=t, pixel_size_m=model_field_pixel_size_m)
        if extent_c != extent_cv:
            raise RuntimeError("Coarse U and V raster extents differ in field mode.")
        xmin, xmax, ymin, ymax = extent_c
        ny, nx = Uc.shape
        dx = (xmax - xmin) / nx
        dy = (ymax - ymin) / ny
        xs = np.linspace(xmin + dx * 0.5, xmax - dx * 0.5, nx)
        ys = np.linspace(ymin + dy * 0.5, ymax - dy * 0.5, ny)
        XX, YY = np.meshgrid(xs, ys)
        stride = max(1, int(model_field_quiver_stride_n))
        ax0.quiver(XX[::stride, ::stride], YY[::stride, ::stride],
                   Uc[::stride, ::stride], Vc[::stride, ::stride],
                   color=model_quiver_color, scale=model_quiver_scale, width=model_quiver_width, headwidth=model_quiver_headwidth, headlength=model_quiver_headlength,
                   alpha=0.85, zorder=19, label="Model (field)")
    else:
        raise ValueError("model_quiver_mode must be 'transect' or 'field'.")

    # ADCP quivers
    idx = np.arange(0, xq.size, max(1, int(quiver_every_n)))
    ax0.quiver(xq[idx], yq[idx], adcp_u_ts[idx], adcp_v_ts[idx],
               color=adcp_quiver_color, scale=adcp_quiver_scale, width=adcp_quiver_width, headwidth=adcp_quiver_headwidth, headlength=adcp_quiver_headlength,
               alpha=0.9, zorder=21, label="ADCP")

    # Track
    ax0.plot(xq, yq, color=adcp_transect_color, lw=0.7, alpha=0.5, zorder=9)

    # Axes
    ax0.set_xlabel(x_label)
    ax0.set_ylabel(y_label)
    xmin, xmax, ymin, ymax = bbox
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(ymin, ymax)
    ax0.set_aspect("equal", adjustable="box")
    ax0.set_title(f"HD Current Speed vs ADCP Transect {adcp.name}", fontsize=8)
    xy_fmt = mticker.FuncFormatter(lambda v, pos: f"{v:.{axis_tick_decimals}f}")
    ax0.xaxis.set_major_formatter(xy_fmt)
    ax0.yaxis.set_major_formatter(xy_fmt)

    # Colorbar
    fig.canvas.draw()
    pos0 = ax0.get_position()
    ax0.set_position([pos0.x0, pos0.y0, pos0.width - (CB_WIDTH + CB_GAP), pos0.height])
    fig.canvas.draw()
    pos = ax0.get_position()
    cb_ax = fig.add_axes([pos.x1 + CB_GAP, pos.y0, CB_WIDTH, pos.height])
    cb = plt.colorbar(im, cax=cb_ax)
    cb.ax.set_ylabel("Mean Current Speed During Transect (m/s)", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    def _fmt_num(v: float, nd: int) -> str:
        return f"{v:.{nd}f}"

    _ticks = sorted(set((model_levels or []) + [cbar_min]))
    _ticks = [v for v in _ticks if cbar_min <= v <= cbar_max]
    if _ticks:
        cb.set_ticks(_ticks)
        cb.set_ticklabels([_fmt_num(v, cbar_tick_decimals) for v in _ticks])
    else:
        _cb_ticks = np.linspace(cbar_min, cbar_max, 5)
        cb.set_ticks(_cb_ticks)
        cb.set_ticklabels([_fmt_num(v, cbar_tick_decimals) for v in _cb_ticks])

    # Legend proxies with solid white background on top
    def _legend_arrow(color, edge="black", lw=0.8, scale=14):
        return FancyArrowPatch((0.05, 0.5), (0.95, 0.5),
                               arrowstyle='-|>', mutation_scale=scale,
                               facecolor=color, edgecolor=edge, linewidth=lw)

    h_adcp  = _legend_arrow(adcp_quiver_color,  edge="black")
    h_model = _legend_arrow(model_quiver_color, edge="black")

    leg = ax0.legend([h_adcp, h_model], ["ADCP", "Model"],
                     handler_map={FancyArrowPatch: HandlerPatch()},
                     loc="upper left", frameon=True, fontsize=7,
                     framealpha=1.0, fancybox=False)
    frame = leg.get_frame()
    frame.set_facecolor("white"); frame.set_alpha(1.0); frame.set_edgecolor("black")
    leg.set_zorder(1000); frame.set_zorder(1001)

    # -------------------- MIDDLE: distance-binned bars
    model_speed_ts = np.hypot(model_u_ts, model_v_ts)
    adcp_speed_ts  = adcp.get_velocity_series(component="speed", mode=adcp_series_mode, target=adcp_series_target)[0]
    dist_m = np.asarray(adcp.position.distance, dtype=float).ravel()

    n = min(dist_m.size, model_speed_ts.size, adcp_speed_ts.size)
    dist_m, model_speed_ts, adcp_speed_ts = dist_m[:n], model_speed_ts[:n], adcp_speed_ts[:n]
    valid = np.isfinite(dist_m) & np.isfinite(model_speed_ts) & np.isfinite(adcp_speed_ts)
    dist_m, model_speed_ts, adcp_speed_ts = dist_m[valid], model_speed_ts[valid], adcp_speed_ts[valid]
    if dist_m.size == 0:
        raise ValueError("No valid samples for distance binning.")

    dmax  = float(np.nanmax(dist_m))
    edges = np.arange(0.0, dmax + distance_bin_m, distance_bin_m)
    if edges.size < 2:
        edges = np.array([0.0, max(distance_bin_m, dmax if np.isfinite(dmax) else distance_bin_m)], dtype=float)
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
    nbins   = edges.size - 1
    bin_idx = np.clip(np.digitize(dist_m, edges) - 1, 0, nbins - 1)

    def binned_mean(values: np.ndarray, idx: np.ndarray, nb: int) -> np.ndarray:
        sums = np.bincount(idx, weights=values, minlength=nb).astype(float)
        cnts = np.bincount(idx, minlength=nb).astype(float)
        out  = np.full(nb, np.nan, dtype=float)
        ok   = cnts > 0
        out[ok] = sums[ok] / cnts[ok]
        return out

    model_bin_mean = binned_mean(model_speed_ts, bin_idx, nbins)
    adcp_bin_mean  = binned_mean(adcp_speed_ts,  bin_idx, nbins)

    bar_w  = max(0.5, distance_bin_m * bar_width_scale)
    offset = bar_w / 2.0
    ax1.bar(centers - offset, model_bin_mean, width=bar_w,
            color=PlottingShell.blue1, alpha=0.9, label="Model", align="center")
    ax1.bar(centers + offset, adcp_bin_mean,  width=bar_w,
            color=PlottingShell.red1,  alpha=0.9, label="ADCP",  align="center")

    ax1.set_xticks(labels)
    ax1.set_xticklabels([f"{c:.1f}" for c in labels])
    ax1.set_xlim(edges[0], edges[-1])
    ax1.set_xlabel("Distance along transect (m)")
    ax1.set_ylabel("Speed (m/s)")
    ax1.grid(alpha=0.3)
    
    # ===== Legend (true arrows) =====
    from matplotlib.patches import FancyArrowPatch
    from matplotlib.legend_handler import HandlerPatch
    from matplotlib.lines import Line2D
    import matplotlib.patheffects as pe
    
    # match your chosen thin look
    EDGE_LW = 0.05
    TAIL_W  = 0.1
    HEAD_W  = 0.5
    HEAD_L  = 0.5
    
    def _legend_arrow(legend, orig_handle, xdescent, ydescent, width, height, fontsize):
        y  = ydescent + 0.5 * height
        x0 = xdescent + 0.12 * width
        x1 = xdescent + 0.88 * width
        ms = 0.95 * height
        arr = FancyArrowPatch(
            (x0, y), (x1, y),
            arrowstyle=f"Simple,tail_width={TAIL_W},head_width={HEAD_W},head_length={HEAD_L}",
            mutation_scale=ms,
            facecolor=orig_handle.get_facecolor(),
            edgecolor=orig_handle.get_edgecolor(),
            linewidth=EDGE_LW,
            joinstyle="miter", capstyle="projecting"
        )
        # subtle visibility boost without looking chunky
        arr.set_path_effects([pe.Stroke(linewidth=max(EDGE_LW+0.2, 0.3), foreground=orig_handle.get_edgecolor()),
                              pe.Normal()])
        return arr

    # proxies using your plot colors
    h_model = FancyArrowPatch((0, 0), (1, 0),
                              facecolor=model_quiver_color, edgecolor="black", linewidth=EDGE_LW)
    h_adcp  = FancyArrowPatch((0, 0), (1, 0),
                              facecolor=adcp_quiver_color, edgecolor="black", linewidth=EDGE_LW)
    h_trk   = Line2D([0], [0], color=adcp_quiver_color, lw=.5)

    leg = ax0.legend(
        [h_model, h_adcp, h_trk],
        ["Model vectors", "ADCP vectors", "ADCP track"],
        handler_map={FancyArrowPatch: HandlerPatch(patch_func=_legend_arrow)},
        loc="upper left", frameon=True, fontsize=7, framealpha=1.0, fancybox=False
    )
    leg.get_frame().set_edgecolor("black")


    ax1.xaxis.set_major_formatter(mticker.FuncFormatter(lambda v, pos: f"{v:.1f}"))
    _y_ticks = [v for v in model_levels if (v >= cbar_min) and (v <= cbar_max)]
    if not _y_ticks:
        _y_ticks = np.linspace(cbar_min, cbar_max, 5).tolist()
    ax1.yaxis.set_major_locator(FixedLocator(_y_ticks))
    ax1.yaxis.set_minor_locator(FixedLocator([]))
    ax1.yaxis.set_major_formatter(mticker.FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}f}"))

    fig.canvas.draw()
    p0 = ax0.get_position()
    p1 = ax1.get_position()
    ax1.set_aspect("auto"); ax1.set_anchor("W")
    try: ax1.set_box_aspect(None)
    except Exception: pass
    ax1.set_position([p0.x0, p1.y0, p0.width, p1.height])
    ax1.set_ylim(cbar_min, cbar_max)
    ax1.legend(frameon=False, fontsize=7, ncol=2)

    # -------------------- BOTTOM: metadata panel
    t_arr   = np.asarray(t)[:n]
    t_valid = t_arr[valid]
    t0 = pd.to_datetime(t_valid.min()); t1 = pd.to_datetime(t_valid.max())
    dur_min = (t1 - t0).total_seconds() / 60.0

    # mean_speed_model = float(np.nanmean(model_speed_ts))
    # mean_speed_obs   = float(np.nanmean(adcp_speed_ts))
    # mean_speed_err   = float(np.nanmean(model_speed_ts - adcp_speed_ts))
    MAE_speed        = float(np.nanmean(np.abs(model_speed_ts - adcp_speed_ts)))
    RMSE_speed       = float(np.sqrt(np.nanmean((model_speed_ts - adcp_speed_ts)**2)))
    IOA_speed        = index_of_agreement(model_speed_ts, adcp_speed_ts, version='original')

    # def circmean_deg(a_deg: np.ndarray) -> float:
    #     a = np.deg2rad(a_deg); c = np.nanmean(np.cos(a)); s = np.nanmean(np.sin(a))
    #     return float((np.degrees(np.arctan2(s, c)) + 360.0) % 360.0)

    # def circdiff_deg(a_deg: np.ndarray, b_deg: np.ndarray) -> np.ndarray:
    #     return (a_deg - b_deg + 180.0) % 360.0 - 180.0

    adcp_dir_ts  = adcp.get_velocity_series(component="direction", mode=adcp_series_mode, target=adcp_series_target)[0]
    model_dir_ts = (np.degrees(np.arctan2(model_u_ts, model_v_ts)) + 360.0) % 360.0
    adcp_dir_ts  = adcp_dir_ts[:n][valid]
    model_dir_ts = model_dir_ts[:n][valid]


    def get_unit_vectors(degrees):
        """Helper to convert degrees to (x, y) unit vectors."""
        radians = np.radians(degrees)
        return np.stack([np.cos(radians), np.sin(radians)], axis=-1)

    def dir_mae(p_deg, o_deg):
        """Calculates Mean Absolute Error for direction"""
        p_vec = get_unit_vectors(p_deg)
        o_vec = get_unit_vectors(o_deg)
        # Magnitude of vector difference |dj| = |pj - oj|
        d_mag = np.linalg.norm(p_vec - o_vec, axis=1)
        return np.nanmean(d_mag)

    def dir_rmse(p_deg, o_deg):
        """Calculates Root Mean Square Error for direction"""
        p_vec = get_unit_vectors(p_deg)
        o_vec = get_unit_vectors(o_deg)
        # Mean of squared magnitudes
        d_mag_sq = np.nansum(np.square(p_vec - o_vec), axis=1)
        return np.sqrt(np.nanmean(d_mag_sq))

    def dir_ioa(p_deg, o_deg):
        """Calculates Index of Agreement (d2) for vectors"""
        p_vec = get_unit_vectors(p_deg)
        o_vec = get_unit_vectors(o_deg)
        
        # Calculate weighted mean vector of observations (o_bar) [5]
        o_bar = np.nanmean(o_vec, axis=0)
        
        # Numerator: Sum of squared vector differences
        numerator = np.nansum(np.linalg.norm(p_vec - o_vec, axis=1)**2)
        
        # Denominator: Potential Error (PE) [5, 6]
        # Sum of (|pj - o_bar| + |oj - o_bar|)^2
        p_dev = np.linalg.norm(p_vec - o_bar, axis=1)
        o_dev = np.linalg.norm(o_vec - o_bar, axis=1)
        denominator = np.nansum((p_dev + o_dev)**2)
        
        return 1 - (numerator / denominator)

    # mean_dir_model = circmean_deg(model_dir_ts)
    # mean_dir_obs   = circmean_deg(adcp_dir_ts)
    # dir_err_series = circdiff_deg(model_dir_ts, adcp_dir_ts)
    # mean_dir_err   = float(np.nanmean(dir_err_series))    
    MAE_dir          = dir_mae(model_dir_ts, adcp_dir_ts)
    MAE_dir          = np.degrees(2 * np.arcsin(MAE_dir / 2))
    RMSE_dir         = dir_rmse(model_dir_ts, adcp_dir_ts)
    RMSE_dir         = np.degrees(2 * np.arcsin(RMSE_dir / 2))
    IOA_dir          = dir_ioa(model_dir_ts, adcp_dir_ts)

    ax2.clear(); ax2.set_axis_off()
    fmt_time = lambda dt: dt.strftime("%d %b. %Y %H:%M")

    def H(x, y, text):
        ax2.text(x, y, text, ha="left", va="top", fontsize=8, fontweight="bold", family="monospace")

    def I(x, y, k, v):
        ax2.text(x, y, f"{k}: {v}", ha="left", va="top", fontsize=7, family="monospace")

    fig.canvas.draw()
    p2 = ax2.get_position()
    ax2.set_aspect("auto"); ax2.set_anchor("W")
    try: ax2.set_box_aspect(None)
    except Exception: pass
    new_x0 = p0.x0 - META_LEFT_OVERSHOOT
    new_w  = min(p0.width + META_LEFT_OVERSHOOT, 1.0 - new_x0)
    ax2.set_position([new_x0, p2.y0, new_w, p2.height])

    y0 = META_TOP_Y; sec = META_SECTION_GAP; line = META_LINE_GAP; cols_x = META_COL_X

    # Col 1
    x = cols_x[0]; y = y0
    H(x, y, "Observation Aggregation"); y -= sec
    I(x, y, "Mode", adcp_series_mode); y -= line
    I(x, y, "Target", adcp_series_target)

    # Col 2
    x = cols_x[1]; y = y0
    H(x, y, "Transect Timing"); y -= sec
    I(x, y, "Start", fmt_time(t0)); y -= line
    I(x, y, "End", fmt_time(t1));  y -= line
    I(x, y, "Duration", f"{dur_min:.1f} min")

    # Col 3
    x = cols_x[2]; y = y0
    H(x, y, "Model vs ADCP (Velocity)"); y -= sec
    # I(x, y, "Mean speed error",  f"{mean_speed_err:.{cbar_tick_decimals}f} m/s"); y -= line
    # I(x, y, "Mean speed (obs)",  f"{mean_speed_obs:.{cbar_tick_decimals}f} m/s"); y -= line
    # I(x, y, "Mean speed (model)", f"{mean_speed_model:.{cbar_tick_decimals}f} m/s"); y -= line
    # I(x, y, "Mean direction error", f"{mean_dir_err:.{cbar_tick_decimals}f}°"); y -= line
    # I(x, y, "Mean direction (obs)",  f"{mean_dir_obs:.{cbar_tick_decimals}f}°"); y -= line
    # I(x, y, "Mean direction (model)", f"{mean_dir_model:.{cbar_tick_decimals}f}°")
    I(x, y, "MAE Speed",  f"{MAE_speed:.{cbar_tick_decimals}f} m/s"); y -= line
    I(x, y, "RMSE Speed", f"{RMSE_speed:.{cbar_tick_decimals}f} m/s"); y -= line
    I(x, y, "IOA Speed",  f"{IOA_speed:.{cbar_tick_decimals}f}"); y -= line
    I(x, y, "MAE Direction",  f"{MAE_dir:.{cbar_tick_decimals}f}"); y -= line
    I(x, y, "RMSE Direction", f"{RMSE_dir:.{cbar_tick_decimals}f}"); y -= line
    I(x, y, "IOA Direction",  f"{IOA_dir:.{cbar_tick_decimals}f}")

    return fig, (ax0, ax1, ax2)