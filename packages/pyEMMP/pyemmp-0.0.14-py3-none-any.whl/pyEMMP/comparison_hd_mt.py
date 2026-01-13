# ===== Imports =====
from typing import Tuple, List, Optional, Sequence
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import ticker as mticker
from matplotlib.colors import LogNorm, Normalize
from matplotlib.collections import LineCollection
from matplotlib.patches import FancyArrowPatch
from matplotlib.legend_handler import HandlerPatch
from matplotlib.lines import Line2D
import matplotlib.patheffects as pe
import cmocean as cmo  # optional colormaps
from matplotlib import ticker as mticker
from matplotlib.ticker import FixedLocator

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

def plot_mixed_mt_hd_transect(
    mt_model: DfsuUtils2D,
    hd_model: DfsuUtils2D,
    adcp: ADCPDataset,
    crs_helper: CRSHelper,
    shapefile_layers: Optional[Sequence[ShapefileLayer]] = None,
    
    # --- ADCP ---
    adcp_transect_lw: float = 1.8,
    adcp_series_mode: str = "bin",                    # "bin" | "range" | "hab"
    adcp_series_target="mean",                        # numeric or "mean"/"pXX"
    adcp_quiver_every_n: int = 20,                         # along-track thinning
    adcp_quiver_width: float = 0.002,
    adcp_quiver_headwidth: float = 2,
    adcp_quiver_headlength: float = 2.5,
    adcp_quiver_scale: float = 3,                          # both layers
    
    # --- SSC ---
    ssc_item_number: int = 1,
    ssc_scale: str = "log",                               # "log" | "normal"
    ssc_levels: Tuple[float, ...] = (0.01, 0.1, 1, 10, 100),
    ssc_vmin: Optional[float] = None,
    ssc_vmax: Optional[float] = None,                     # mg/L; None → auto
    ssc_cmap_name="turbo",                                # or a Colormap object
    ssc_bottom_thresh: float = 0.01,                      # mg/L; transparent below
    ssc_pixel_size_m: int = 10,                           # Raster resolution
    
    # --- Currents (field) ---
    u_item_number: int = 4,
    v_item_number: int = 5,
    model_field_pixel_size_m: int = 100,                    # coarse field res (field mode)
    model_field_quiver_stride_n: int = 3,                   # stride for field vectors
    model_quiver_scale: float = 3,                        
    model_quiver_width: float = 0.002,
    model_quiver_headwidth: float = 2,
    model_quiver_headlength: float = 2.5,
    model_quiver_color: str = "black",
    
    model_quiver_mode: str = "field",                 # "transect" | "field"
    
    # ----- Layout: figure + colorbar + metadata -----
    cbar_tick_decimals: int = 2,                           # colorbar tick precision
    axis_tick_decimals: int = 3,                  # map axis tick precision
    pad_m: float = 2000,                              # bbox padding
    
):
    """
    Mixed MT-HD transect plot.

    Top:
        MT SSC raster over bbox, ADCP track colored by SSC, ADCP quivers colored by SSC,
        Model quivers single color (or coarse field vectors).
    Bottom:
        Metadata block.

    Returns
    -------
    fig : matplotlib.figure.Figure
    (ax0, ax2) : tuple[Axes, Axes]
    """
    FIG_W: float = 6.5
    FIG_H: float = 9.0
    LEFT: float = 0.06
    RIGHT: float = 0.96 
    TOP: float = 0.98
    BOTTOM: float = 0.05
    HSPACE: float = 0.22
    CB_WIDTH: float = 0.012
    CB_GAP: float = 0.008
    META_TOP_Y: float = 0.95
    META_SECTION_GAP: float = 0.10
    META_LINE_GAP: float = 0.10
    META_LEFT_OVERSHOOT: float = 0.0
    META_COL_START: float = 0.02 
    META_COL_END: float = 0.70
    META_COLS: int = 3
    if shapefile_layers is None:
        shapefile_layers = []

    # ----- Aliases -----
    xq = np.asarray(adcp.position.x).ravel()
    yq = np.asarray(adcp.position.y).ravel()
    t = adcp.time.ensemble_datetimes

    # ============================== DERIVED / HELPERS ==============================
    def _fmt_num(v: float, nd: int) -> str:
        return f"{v:.{nd}f}"

    x_label, y_label = crs_helper.axis_labels()
    bbox = crs_helper.bbox_from_coords(xq, yq, pad_m=pad_m, from_crs=adcp.position.epsg)
    META_COL_X = list(np.linspace(META_COL_START, META_COL_END, META_COLS))
    # ============================== FIGURE SHELL ==============================
    fig, ax = PlottingShell.subplots(
        figheight=FIG_H, figwidth=FIG_W, nrow=2, ncol=1, height_ratios=[1.00, 0.28]
    )
    fig.subplots_adjust(left=LEFT, right=RIGHT, top=TOP, bottom=BOTTOM, hspace=HSPACE)
    ax0, ax2 = ax

    # ====================================================================== TOP — MT SSC raster + ADCP/Model vectors
    ssc_img, extent = mt_model.rasterize_idw_bbox(
        item_number=ssc_item_number, bbox=bbox, t=t, pixel_size_m=ssc_pixel_size_m
    )
    ssc_img = np.asarray(ssc_img, float) * 1000.0  # mg/L
    finite = np.isfinite(ssc_img)
    if not finite.any():
        raise ValueError("No finite SSC values in model raster.")

    auto_min = float(np.nanmin(ssc_img[finite]))
    auto_max = float(np.nanmax(ssc_img[finite]))
    cbar_min = ssc_vmin if ssc_vmin is not None else (min(ssc_levels) if ssc_levels else max(ssc_bottom_thresh, auto_min))
    cbar_max = ssc_vmax if ssc_vmax is not None else (max(ssc_levels) if ssc_levels else auto_max)
    cbar_min = max(ssc_bottom_thresh, cbar_min)
    if (not np.isfinite(cbar_min)) or (not np.isfinite(cbar_max)) or (cbar_min >= cbar_max):
        cbar_min, cbar_max = max(ssc_bottom_thresh, 0.01), max(ssc_bottom_thresh * 100.0, 100.0)

    norm = LogNorm(vmin=cbar_min, vmax=cbar_max, clip=True) if str(ssc_scale).lower() == "log" \
        else Normalize(vmin=cbar_min, vmax=cbar_max, clip=True)
    cmap = plt.get_cmap(ssc_cmap_name) if isinstance(ssc_cmap_name, str) else ssc_cmap_name
    cmap = cmap.copy()
    cmap.set_under(alpha=0.0)

    # ADCP SSC for coloring track + ADCP vectors
    adcp_ssc_ts, _ = adcp.get_beam_series(
        field_name="suspended_solids_concentration", mode=adcp_series_mode, target=adcp_series_target
    )
    adcp_ssc_ts = np.asarray(adcp_ssc_ts, float)

    # Draw base SSC raster + shapefiles
    im = ax0.imshow(ssc_img, extent=extent, origin="lower", cmap=cmap, norm=norm, interpolation="nearest")
    for layer in shapefile_layers:
        layer.plot(ax0)

    # ADCP track colored by SSC
    pts = np.column_stack([xq, yq])
    if pts.shape[0] >= 2:
        segs = np.stack([pts[:-1], pts[1:]], axis=1)  # (n-1, 2, 2)
        n_seg = segs.shape[0]
        ssc_line = np.asarray(adcp_ssc_ts[:n_seg], float)
        lc = LineCollection(segs, cmap=cmap, norm=norm, linewidths=adcp_transect_lw, alpha=0.95, zorder=12)
        lc.set_array(np.clip(ssc_line, cbar_min, cbar_max))
        ax0.add_collection(lc)
    else:
        ax0.plot(xq, yq, color="k", lw=adcp_transect_lw, alpha=0.9, zorder=12)

    # ADCP quivers colored by SSC
    adcp_u_ts, _ = adcp.get_velocity_series(component="u", mode=adcp_series_mode, target=adcp_series_target)
    adcp_v_ts, _ = adcp.get_velocity_series(component="v", mode=adcp_series_mode, target=adcp_series_target)
    adcp_u_ts = np.asarray(adcp_u_ts, float)
    adcp_v_ts = np.asarray(adcp_v_ts, float)
    idx = np.arange(0, xq.size, max(1, int(adcp_quiver_every_n)))
    C_adcp = np.clip(adcp_ssc_ts[:xq.size][idx], cbar_min, cbar_max)
    ax0.quiver(
        xq[idx], yq[idx], adcp_u_ts[idx], adcp_v_ts[idx],
        C_adcp, cmap=cmap, norm=norm,
        scale=adcp_quiver_scale, width=adcp_quiver_width, headwidth=adcp_quiver_headwidth, headlength=adcp_quiver_headlength,
        pivot="tail", alpha=0.95, zorder=14
    )

    # MODEL quivers: transect or coarse field
    if model_quiver_mode.lower() == "transect":
        mu = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=u_item_number)[0], float)
        mv = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=v_item_number)[0], float)
        ax0.quiver(
            xq[idx], yq[idx], mu[idx], mv[idx],
            color=model_quiver_color, scale=model_quiver_scale, width=model_quiver_width,
            headwidth=model_quiver_headwidth, headlength=model_quiver_headlength, pivot="tail", alpha=0.9, zorder=13
        )
    elif model_quiver_mode.lower() == "field":
        Uc, ext_u = hd_model.rasterize_idw_bbox(item_number=u_item_number, bbox=bbox, t=t, pixel_size_m=model_field_pixel_size_m)
        Vc, ext_v = hd_model.rasterize_idw_bbox(item_number=v_item_number, bbox=bbox, t=t, pixel_size_m=model_field_pixel_size_m)
        if ext_u != ext_v:
            raise RuntimeError("Field-mode U and V raster extents differ.")
        xmin, xmax, ymin, ymax = ext_u
        ny, nx = np.asarray(Uc).shape
        dx = (xmax - xmin) / nx
        dy = (ymax - ymin) / ny
        xs = np.linspace(xmin + dx * 0.5, xmax - dx * 0.5, nx)
        ys = np.linspace(ymin + dy * 0.5, ymax - dy * 0.5, ny)
        XX, YY = np.meshgrid(xs, ys)
        stride = max(1, int(model_field_quiver_stride_n))
        ax0.quiver(
            XX[::stride, ::stride], YY[::stride, ::stride],
            Uc[::stride, ::stride], Vc[::stride, ::stride],
            color=model_quiver_color, scale=model_quiver_scale, width=model_quiver_width,
            headwidth=model_quiver_headwidth, headlength=model_quiver_headlength, pivot="tail", alpha=0.85, zorder=13
        )
    else:
        raise ValueError("model_quiver_mode must be 'transect' or 'field'.")

    # Axes, limits, labels
    ax0.set_xlabel(x_label)
    ax0.set_ylabel(y_label)
    xmin, xmax, ymin, ymax = bbox
    ax0.set_xlim(xmin, xmax)
    ax0.set_ylim(ymin, ymax)
    ax0.set_aspect("equal", adjustable="box")
    ax0.set_title(f"SSC Field + Currents — {adcp.name}", fontsize=8)
    xy_fmt = mticker.FuncFormatter(lambda v, pos: f"{v:.{axis_tick_decimals}f}")
    ax0.xaxis.set_major_formatter(xy_fmt)
    ax0.yaxis.set_major_formatter(xy_fmt)

    # ----- Colorbar (robust, no clipping) -----
    from mpl_toolkits.axes_grid1 import make_axes_locatable
    
    fig.canvas.draw()
    divider = make_axes_locatable(ax0)
    
    # convert your figure-fraction widths to axes-relative percent and inch pad
    fig_w_in = fig.get_size_inches()[0]
    axw_fig  = ax0.get_position().width
    cb_pct   = (CB_WIDTH / axw_fig) * 100.0                 # e.g., "1.2%"
    pad_in   = max(0.02, CB_GAP * fig_w_in)                 # gap in inches
    
    cax = divider.append_axes("right", size=f"{cb_pct:.3f}%", pad=pad_in)
    cb  = fig.colorbar(im, cax=cax)
    cb.ax.set_ylabel("Mean SSC During Transect (mg/L)", fontsize=7)
    cb.ax.tick_params(labelsize=6)

    
    # choose ticks: prefer your `ssc_levels`, fall back if empty
    _ticks = [v for v in (ssc_levels or []) if cbar_min <= v <= cbar_max]
    if not _ticks:
        _ticks = (np.geomspace(cbar_min, cbar_max, 6)
                  if ssc_scale.lower() == "log" else
                  np.linspace(cbar_min, cbar_max, 6))
    
    # force numeric labels, no sci notation
    cb.locator   = FixedLocator(_ticks)      # lock tick positions
    cb.set_ticks(_ticks)
    cb.formatter = mticker.FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}f}")
    cb.update_ticks()

    
    # Legend with arrow patches
    EDGE_LW = 0.05
    TAIL_W = 0.1
    HEAD_W = 0.5
    HEAD_L = 0.5

    if np.isfinite(C_adcp).any():
        _mean_ssc_leg = float(np.nanmean(C_adcp))
    else:
        _mean_ssc_leg = 0.5 * (cbar_min + cbar_max)
    adcp_mean_rgba = cmap(norm(_mean_ssc_leg))

    # Thin overlay of ADCP track in the same mean color
    ax0.plot(xq, yq, color=adcp_mean_rgba, lw=adcp_transect_lw * 0.75, alpha=0.9, zorder=12.5)

    def _legend_arrow(legend, orig_handle, xdescent, ydescent, width, height, fontsize):
        y = ydescent + 0.5 * height
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
            joinstyle="miter", capstyle="projecting",
        )
        arr.set_path_effects([
            pe.Stroke(linewidth=max(EDGE_LW + 0.2, 0.3), foreground=orig_handle.get_edgecolor()),
            pe.Normal()
        ])
        return arr

    h_model = FancyArrowPatch((0, 0), (1, 0),
                              facecolor=model_quiver_color, edgecolor="black", linewidth=EDGE_LW)
    h_adcp = FancyArrowPatch((0, 0), (1, 0),
                             facecolor=adcp_mean_rgba, edgecolor="black", linewidth=EDGE_LW)
    h_trk = Line2D([0], [0], color=adcp_mean_rgba, lw=adcp_transect_lw)

    leg = ax0.legend(
        [h_model, h_adcp, h_trk],
        ["Model vectors", "ADCP vectors (mean SSC color)", "ADCP track (mean SSC color)"],
        handler_map={FancyArrowPatch: HandlerPatch(patch_func=_legend_arrow)},
        loc="upper left", frameon=True, fontsize=7, framealpha=1.0, fancybox=False,
    )
    leg.get_frame().set_edgecolor("black")

    # ====================================================================== BOTTOM — metadata
    u_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=u_item_number)[0], float)
    v_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=v_item_number)[0], float)
    spd_ts = np.hypot(u_ts, v_ts)
    model_ssc_ts = np.asarray(
        mt_model.rasterize_idw_bbox(item_number=ssc_item_number, bbox=bbox, t=t, pixel_size_m=ssc_pixel_size_m)[0],
        float
    ).ravel() * 1000.0

    n = min(adcp_ssc_ts.size, model_ssc_ts.size, spd_ts.size)
    valid = np.isfinite(adcp_ssc_ts[:n]) & np.isfinite(model_ssc_ts[:n]) & np.isfinite(spd_ts[:n])
    adcp_ssc_ts = adcp_ssc_ts[:n][valid]
    model_ssc_ts = model_ssc_ts[:n][valid]
    spd_ts = spd_ts[:n][valid]
    t_arr = np.asarray(t)[:n][valid]

    t0 = pd.to_datetime(t_arr.min())
    t1 = pd.to_datetime(t_arr.max())
    dur_min = (t1 - t0).total_seconds() / 60.0
    # mean_ssc_model = float(np.nanmean(model_ssc_ts))
    # mean_ssc_obs = float(np.nanmean(adcp_ssc_ts))
    # mean_ssc_err = float(np.nanmean(model_ssc_ts - adcp_ssc_ts))
    # mean_spd = float(np.nanmean(spd_ts))

    MAE_ssc = float(np.nanmean(np.abs(model_ssc_ts - adcp_ssc_ts)))
    RMSE_ssc = float(np.sqrt(np.nanmean((model_ssc_ts - adcp_ssc_ts) ** 2)))
    IOA_ssc = index_of_agreement(model_ssc_ts, adcp_ssc_ts, version="original")

    # Model transect series
    model_u_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=u_item_number)[0], dtype=float)
    model_v_ts = np.asarray(hd_model.extract_transect_idw(xq, yq, t, item_number=v_item_number)[0], dtype=float)    
    model_speed_ts = np.hypot(model_u_ts, model_v_ts)
    adcp_speed_ts  = adcp.get_velocity_series(component="speed", mode=adcp_series_mode, target=adcp_series_target)[0]
    MAE_speed        = float(np.nanmean(np.abs(model_speed_ts - adcp_speed_ts)))
    RMSE_speed       = float(np.sqrt(np.nanmean((model_speed_ts - adcp_speed_ts)**2)))
    IOA_speed        = index_of_agreement(model_speed_ts, adcp_speed_ts, version='original')

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

    MAE_dir          = dir_mae(model_dir_ts, adcp_dir_ts)
    MAE_dir          = np.degrees(2 * np.arcsin(MAE_dir / 2))
    RMSE_dir         = dir_rmse(model_dir_ts, adcp_dir_ts)
    RMSE_dir         = np.degrees(2 * np.arcsin(RMSE_dir / 2))
    IOA_dir          = dir_ioa(model_dir_ts, adcp_dir_ts)

    ax2.clear()
    ax2.set_axis_off()
    fmt_time = lambda dt: dt.strftime("%d %b. %Y %H:%M")

    def H(x, y, text):
        ax2.text(x, y, text, ha="left", va="top", fontsize=8, fontweight="bold", family="monospace")

    def I(x, y, k, v):
        ax2.text(x, y, f"{k}: {v}", ha="left", va="top", fontsize=7, family="monospace")

    fig.canvas.draw()
    p2 = ax2.get_position()
    ax2.set_aspect("auto")
    ax2.set_anchor("W")
    try:
        ax2.set_box_aspect(None)
    except Exception:
        pass
    new_x0 = ax0.get_position().x0 - META_LEFT_OVERSHOOT
    new_w = min(ax0.get_position().width + META_LEFT_OVERSHOOT, 1.0 - new_x0)
    ax2.set_position([new_x0, p2.y0, new_w, p2.height])

    y0 = META_TOP_Y
    sec = META_SECTION_GAP
    line = META_LINE_GAP
    cols_x = META_COL_X

    # Column 1
    x = cols_x[0]
    y = y0
    H(x, y, "Observation Aggregation")
    y -= sec
    I(x, y, "SSC mode", adcp_series_mode)
    y -= line
    I(x, y, "SSC target", adcp_series_target)
    y -= line
    I(x, y, "Vector mode", model_quiver_mode)
    y -= sec
    y -= sec
    H(x, y, "Statistics\n(SSC)")
    y -= sec
    y -= (line/2)
    I(x, y, "MAE", f"{MAE_ssc:.{cbar_tick_decimals}f} mg/L")
    y -= line
    I(x, y, "RMSE", f"{RMSE_ssc:.{cbar_tick_decimals}f} mg/L")
    y -= line
    I(x, y, "IOA", f"{IOA_ssc:.{cbar_tick_decimals}f}")
    y -= line

    # Column 2
    x = cols_x[1]
    y = y0
    H(x, y, "Transect Timing")
    y -= sec
    I(x, y, "Start", fmt_time(t0))
    y -= line
    I(x, y, "End", fmt_time(t1))
    y -= line
    I(x, y, "Duration", f"{dur_min:.1f} min")
    y -= sec
    y -= sec
    H(x, y, "Statistics\n(Current Speed)")
    y -= sec
    y -= (line/2)
    I(x, y, "MAE", f"{MAE_speed:.{cbar_tick_decimals}f} m/s")
    y -= line
    I(x, y, "RMSE", f"{RMSE_speed:.{cbar_tick_decimals}f} m/s")
    y -= line
    I(x, y, "IOA", f"{IOA_speed:.{cbar_tick_decimals}f}")

    x = cols_x[2]
    y = y0
    y -= sec
    y -= line
    y -= line
    y -= sec
    y -= sec
    H(x, y, "Statistics\n(Current Direction)")
    y -= sec
    y -= (line/2)
    I(x, y, "MAE", f"{MAE_dir:.{cbar_tick_decimals}f}°")
    y -= line
    I(x, y, "RMSE", f"{RMSE_dir:.{cbar_tick_decimals}f}°")
    y -= line
    I(x, y, "IOA", f"{IOA_dir:.{cbar_tick_decimals}f}")


    return fig, (ax0, ax2)