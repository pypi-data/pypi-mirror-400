# -*- coding: utf-8 -*-
"""
SSC map + HD currents animation (function + Qt progress UI)

Updates in this version
- Progress dialog shows ALL stages and stays on top.
- Uses label "Loading frames" (instead of "Preloading frames").
- Explicitly indicates whether a GIF/MP4 will be saved or not.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Sequence, Tuple, Union

import numpy as np
import pandas as pd
import matplotlib
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.colors import LogNorm, Normalize
from matplotlib import ticker as mticker
from matplotlib.ticker import FixedLocator
import cmocean as cmo
# Optional imageio for progress-aware saving
try:
    import imageio.v2 as imageio
    _HAS_IMAGEIO = True
except Exception:
    _HAS_IMAGEIO = False

# Qt
from PyQt5.QtWidgets import QApplication, QProgressDialog
from PyQt5.QtCore import Qt

# Pro.ject utils
from .utils_dfsu2d import DfsuUtils2D
from .utils_crs import CRSHelper
from .utils_shapefile import ShapefileLayer
from .plotting import PlottingShell


def make_ssc_currents_animation(
    mt_model: DfsuUtils2D,
    hd_model: DfsuUtils2D,
    crs_helper: CRSHelper,
    
    bbox_layer: ShapefileLayer,     #TODO: To be checked against other functions
    shapefile_layers: Optional[Sequence[ShapefileLayer]] = None,
    

    # --- SSC ---
    ssc_item_number: int = 1,                 # kg/m³ → ×100 to mg/L
    ssc_scale: str = "log",                   # "log" | "normal"
    ssc_levels: Optional[Sequence[float]] = (0.001, 0.01, 0.1, 1.0, 10.0),  # mg/L
    ssc_vmin: Optional[float] = None,
    ssc_vmax: Optional[float] = None,
    ssc_cmap_name: str = "turbo",
    ssc_bottom_thresh: float = 0.01,         # mg/L; lower = WHITE
    ssc_pixel_size_m: float = 10.0,           # Raster resolution
    
    # --- Currents (field) ---
    u_item_number: int = 4,
    v_item_number: int = 5,
    model_field_pixel_size_m: float = 100.0,
    model_field_quiver_stride_n: int = 3,
    model_quiver_scale: float = 10.0,
    model_quiver_width: float = 0.002,
    model_quiver_headwidth: float = 2.0,
    model_quiver_headlength: float = 2.5,
    model_quiver_color: str = "white",

    # --- Time / animation ---
    animation_time_start_idx: int = 0,
    animation_time_end_idx: Optional[int] = None,
    animation_time_step: int = 1,
    animation_interval_ms: int = 1,
    save_output: bool = True,
    animation_out_path: Union[str, Path] = "ssc_currents.gif",
    writer_kind: str = "gif",                 # "gif" | "mp4"

    # --- Layout ---
    axis_tick_decimals: int = 3,
    cbar_tick_decimals: int = 3,

    # --- UI ---
    use_qt_progress: bool = True,
) -> Tuple[plt.Figure, FuncAnimation]:
    """Build and optionally save SSC (mg/L) + HD currents animation."""

    # ---------- Progress UI ----------
    app = QApplication.instance() or (QApplication([]) if use_qt_progress else None)

    class _Progress:
        def __init__(self, enabled: bool) -> None:
            self.enabled = bool(enabled and app is not None)
            self.dlg: Optional[QProgressDialog] = None
            if self.enabled:
                self.dlg = QProgressDialog("Initializing…", "Cancel", 0, 100)
                self.dlg.setWindowTitle("Building Animation")
                # keep on top
                self.dlg.setWindowFlags(self.dlg.windowFlags() | Qt.WindowStaysOnTopHint)
                self.dlg.setWindowModality(Qt.WindowModal)
                self.dlg.setAutoClose(False)
                self.dlg.setAutoReset(False)
                self.dlg.setMinimumWidth(440)
                self.set(0, "Initializing…")
                self.raise_()

        def raise_(self):
            if self.enabled:
                self.dlg.raise_()
                self.dlg.activateWindow()
                app.processEvents()

        def set(self, val: int, text: str) -> None:
            if not self.enabled:
                return
            self.dlg.setValue(max(0, min(100, int(val))))
            self.dlg.setLabelText(text)
            app.processEvents()

        def inc(self, dv: float, text: Optional[str] = None) -> None:
            if not self.enabled:
                return
            v = int(self.dlg.value() + dv)
            if text:
                self.set(v, text)
            else:
                self.dlg.setValue(v)
                app.processEvents()

        def canceled(self) -> bool:
            return bool(self.enabled and self.dlg.wasCanceled())

        def close(self) -> None:
            if self.enabled:
                self.set(100, "Done.")
                app.processEvents()
                self.dlg.close()

    PROG = _Progress(use_qt_progress)
    fig_width: float = 4.0
    fig_height: float = 4.0
    left: float = 0.08
    right: float = 0.90
    top: float = 0.97
    bottom: float = 0.10
    cb_width: float = 0.012
    cb_gap: float = 0.008
    dpi: int = 150
    # ---------- Stage: Bbox ----------
    PROG.set(3, "Reading bbox from shapefile…")
    b = bbox_layer.bounds()
    if isinstance(b, str):
        PROG.close()
        raise RuntimeError(f"bbox_layer error: {b}")
    xmin, xmax, ymin, ymax = b
    bbox = [xmin, xmax, ymin, ymax]

    # ---------- Stage: Times ----------
    PROG.set(6, "Selecting model times…")
    times_all = np.asarray(mt_model.model_times)
    if animation_time_end_idx is None:
        animation_time_end_idx = times_all.size
    sel_idx = np.arange(animation_time_start_idx, animation_time_end_idx, max(1, int(animation_time_step)))
    times = times_all[sel_idx]
    n_frames = times.size
    if n_frames == 0:
        PROG.close()
        raise ValueError("No frames selected. Adjust time indices/step.")

    # ---------- Stage: First frame (scales) ----------
    PROG.set(10, "Rasterizing first SSC/UV frames…")
    t0 = times[0]
    ssc_img0, ssc_extent = mt_model.rasterize_idw_bbox(
        item_number=ssc_item_number, bbox=bbox, t=t0, pixel_size_m=ssc_pixel_size_m
    )
    ssc_img0 = np.asarray(ssc_img0, float) * 100.0  # kg/m³ → mg/L

    finite0 = np.isfinite(ssc_img0)
    if not finite0.any():
        PROG.close()
        raise ValueError("No finite SSC values in initial raster.")
    auto_min = float(np.nanmin(ssc_img0[finite0]))
    auto_max = float(np.nanmax(ssc_img0[finite0]))
    cbar_min = ssc_vmin if ssc_vmin is not None else (
        min(ssc_levels) if ssc_levels else max(ssc_bottom_thresh, auto_min)
    )
    cbar_max = ssc_vmax if ssc_vmax is not None else (
        max(ssc_levels) if ssc_levels else auto_max
    )
    cbar_min = max(ssc_bottom_thresh, cbar_min)
    if not np.isfinite(cbar_min) or not np.isfinite(cbar_max) or cbar_min >= cbar_max:
        cbar_min, cbar_max = max(ssc_bottom_thresh, 0.01), max(ssc_bottom_thresh * 100.0, 100.0)

    cmap = matplotlib.colormaps.get_cmap(ssc_cmap_name).copy()
    cmap.set_under((1.0, 1.0, 1.0, 1.0))  # WHITE underflow
    cmap.set_bad((1.0, 1.0, 1.0, 0.0))    # transparent NaN
    norm = LogNorm(vmin=cbar_min, vmax=cbar_max, clip=False) if ssc_scale.lower() == "log" else Normalize(vmin=cbar_min, vmax=cbar_max, clip=False)

    # Precompute U/V extent
    U0, ext_u = hd_model.rasterize_idw_bbox(item_number=u_item_number, bbox=bbox, t=t0, pixel_size_m=model_field_pixel_size_m)
    V0, ext_v = hd_model.rasterize_idw_bbox(item_number=v_item_number, bbox=bbox, t=t0, pixel_size_m=model_field_pixel_size_m)
    if ext_u != ext_v:
        PROG.close()
        raise RuntimeError("U and V raster extents differ.")
    uxmin, uxmax, uymin, uymax = ext_u

    # ---------- Stage: Loading frames ----------
    PROG.set(14, f"Loading frames… (0/{n_frames})")
    ssc_cache: List[np.ndarray] = []
    U_cache: List[np.ndarray] = []
    V_cache: List[np.ndarray] = []

    per_frame = 60.0 / max(1, n_frames)  # map 14 → 74
    for ii, ti in enumerate(times):
        if PROG.canceled():
            PROG.close()
            print("Cancelled: Loading frames.")
            return None, None  # type: ignore

        ssc_frame, _ = mt_model.rasterize_idw_bbox(
            item_number=ssc_item_number, bbox=bbox, t=ti, pixel_size_m=ssc_pixel_size_m
        )
        U_frame, _ = hd_model.rasterize_idw_bbox(
            item_number=u_item_number, bbox=bbox, t=ti, pixel_size_m=model_field_pixel_size_m
        )
        V_frame, _ = hd_model.rasterize_idw_bbox(
            item_number=v_item_number, bbox=bbox, t=ti, pixel_size_m=model_field_pixel_size_m
        )

        ssc_cache.append(np.asarray(ssc_frame, float) * 100.0)
        U_cache.append(np.asarray(U_frame, float))
        V_cache.append(np.asarray(V_frame, float))

        PROG.inc(per_frame, f"Loading frames… ({ii+1}/{n_frames})")

    ssc_cache = np.asarray(ssc_cache, dtype=float)

    # ---------- Stage: Preparing grid & figure ----------
    PROG.set(76, "Preparing quiver grid…")
    ny, nx = np.asarray(U_cache[0]).shape
    dx = (uxmax - uxmin) / nx
    dy = (uymax - uymin) / ny
    xs = np.linspace(uxmin + 0.5 * dx, uxmax - 0.5 * dx, nx)
    ys = np.linspace(uymin + 0.5 * dy, uymax - 0.5 * dy, ny)
    XX, YY = np.meshgrid(xs, ys)
    stride = max(1, int(model_field_quiver_stride_n))

    PROG.set(80, "Building figure & artists…")
    fig, axes = PlottingShell.subplots(figheight=fig_height, figwidth=fig_width, nrow=1, ncol=1)
    ax = axes[0] if isinstance(axes, (list, tuple, np.ndarray)) else axes
    fig.subplots_adjust(left=left, right=right, top=top, bottom=bottom)

    ax.set_aspect("equal", adjustable="box")
    ax.set_xlim(xmin, xmax); ax.set_ylim(ymin, ymax)
    x_label, y_label = crs_helper.axis_labels()
    ax.set_xlabel(x_label); ax.set_ylabel(y_label)
    xy_fmt = mticker.FuncFormatter(lambda v, pos: f"{v:.{axis_tick_decimals}f}")
    ax.xaxis.set_major_formatter(xy_fmt); ax.yaxis.set_major_formatter(xy_fmt)
    ax.set_title("SSC (mg/L) with HD Currents", fontsize=8, pad=2)

    im = ax.imshow(ssc_cache[0], extent=ssc_extent, origin="lower",
                   cmap=cmap, norm=norm, interpolation="nearest", zorder=9)

    if shapefile_layers:
        PROG.set(84, "Drawing overlays…")
        for layer in shapefile_layers:
            layer.plot(ax)

    quiv = ax.quiver(
        XX[::stride, ::stride], YY[::stride, ::stride],
        U_cache[0][::stride, ::stride], V_cache[0][::stride, ::stride],
        color=model_quiver_color, scale=model_quiver_scale, width=model_quiver_width,
        headwidth=model_quiver_headwidth, headlength=model_quiver_headlength, pivot="tail",
        alpha=0.9, zorder=12
    )

    # Colorbar
    PROG.set(86, "Preparing colorbar…")
    fig.canvas.draw()
    sp = fig.subplotpars
    apos = ax.get_position()
    ax.set_position([apos.x0, apos.y0, (sp.right - (cb_gap + cb_width)) - apos.x0, apos.height])
    fig.canvas.draw()
    apos = ax.get_position()
    cax = fig.add_axes([sp.right - cb_width, apos.y0, cb_width, apos.height])
    cb = plt.colorbar(im, cax=cax)
    cb.ax.set_ylabel("SSC (mg/L)", fontsize=7)
    cb.ax.tick_params(labelsize=6)
    _ticks = [v for v in (ssc_levels or []) if cbar_min <= v <= cbar_max]
    if not _ticks:
        _ticks = (np.geomspace(cbar_min, cbar_max, 6) if ssc_scale.lower() == "log"
                  else np.linspace(cbar_min, cbar_max, 6))
    cb.locator = FixedLocator(_ticks)
    cb.set_ticks(_ticks)
    cb.formatter = mticker.FuncFormatter(lambda v, pos: f"{v:.{cbar_tick_decimals}}")
    cb.update_ticks()

    # Time overlay
    def _fmt_time(ts) -> str:
        dt = pd.to_datetime(ts)
        return dt.strftime("%d %b %Y %H:%M")

    t_start_dt = pd.to_datetime(times[0])
    time_text = ax.text(
        0.02, 0.98, _fmt_time(times[0]),
        transform=ax.transAxes, ha="left", va="top",
        fontsize=7, family="monospace",
        bbox=dict(boxstyle="round,pad=0.2", fc=(1, 1, 1, 0.85), ec="none"),
        zorder=20,
    )
    elapsed_text = ax.text(
        0.02, 0.93, "Elapsed: 0.0 min",
        transform=ax.transAxes, ha="left", va="top",
        fontsize=7, family="monospace",
        bbox=dict(boxstyle="round,pad=0.2", fc=(1, 1, 1, 0.85), ec="none"),
        zorder=20,
    )

    # Animator
    def _update(i):
        im.set_data(ssc_cache[i])
        quiv.set_UVC(U_cache[i][::stride, ::stride], V_cache[i][::stride, ::stride])
        time_text.set_text(_fmt_time(times[i]))
        dt_min = (pd.to_datetime(times[i]) - t_start_dt).total_seconds() / 60.0
        elapsed_text.set_text(f"Elapsed: {dt_min:.1f} min")
        return (im, quiv, time_text, elapsed_text)

    ani = FuncAnimation(fig, _update, frames=n_frames, interval=animation_interval_ms, blit=True)

    # ---------- Stage: Saving (or not) ----------
    if save_output:
        out_path = Path(animation_out_path)
        out_path.parent.mkdir(parents=True, exist_ok=True)

        if _HAS_IMAGEIO:
            PROG.set(90, f"Saving ({writer_kind}) with progress…")
            frames_rgba = []
            # capture frame 0
            fig.canvas.draw()
            w, h = fig.canvas.get_width_height()
            buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8).reshape((h, w, 4))
            frames_rgba.append(buf[:, :, [1, 2, 3, 0]].copy())

            remaining = max(1, n_frames - 1)
            per_save = 10.0 / remaining  # 90 → 100

            for i in range(1, n_frames):
                if PROG.canceled():
                    PROG.close()
                    print("Cancelled: Saving animation.")
                    return fig, ani
                _update(i)
                fig.canvas.draw()
                w, h = fig.canvas.get_width_height()
                buf = np.frombuffer(fig.canvas.tostring_argb(), dtype=np.uint8).reshape((h, w, 4))
                frames_rgba.append(buf[:, :, [1, 2, 3, 0]].copy())
                PROG.inc(per_save, f"Rendering frames for save… ({i+1}/{n_frames})")

            if writer_kind.lower() == "gif":
                imageio.mimsave(str(out_path), frames_rgba, duration=max(0.001, animation_interval_ms / 1000.0))
            elif writer_kind.lower() == "mp4":
                imageio.mimsave(str(out_path), frames_rgba, fps=max(1, int(1000 / max(1, int(animation_interval_ms)))))
            else:
                PROG.close()
                raise ValueError("writer_kind must be 'gif' or 'mp4'.")
            PROG.set(100, f"Saved: {out_path}")

        else:
            fps = max(1, int(1000 / max(1, int(animation_interval_ms))))
            kind = "PillowWriter" if writer_kind.lower() == "gif" else "ffmpeg"
            PROG.set(92, f"Saving via {kind} (no per-frame progress)…")
            if writer_kind.lower() == "gif":
                ani.save(str(out_path), writer=PillowWriter(fps=fps), dpi=dpi)
            elif writer_kind.lower() == "mp4":
                ani.save(str(out_path), writer="ffmpeg", dpi=dpi, fps=fps)
            else:
                PROG.close()
                raise ValueError("writer_kind must be 'gif' or 'mp4'.")
            PROG.set(100, f"Saved: {out_path}")
    else:
        PROG.set(100, "Not saving (preview only).")

    PROG.close()
    return fig, ani


# ============================== EXAMPLE ==============================
if __name__ == "__main__":
    # CRS
    project_crs_epsg = 4326
    crs_helper = CRSHelper(project_crs=project_crs_epsg)

    # Models
    mt_model_path = r'//usden1-stor.dhi.dk/Projects/61803553-05/Models/F3/2024/10. October/MT/MTD20241002_1.dfsu'
    hd_model_path = r'\\USDEN1-STOR.DHI.DK\\Projects\\61803553-05\\Models\\F3\\2024\\10. October\\HD\\HDD20241002.dfsu'
    mt_model = DfsuUtils2D(mt_model_path, crs_helper=crs_helper)
    hd_model = DfsuUtils2D(hd_model_path, crs_helper=crs_helper)

    # Bbox layer
    bbox_layer = ShapefileLayer(
        path=r'\\usden1-stor.dhi.dk\Projects\61803553-05\GIS\F3\example point layer\extract_model_results.shp',
        kind="polygon",
        crs_helper=crs_helper,
        poly_edgecolor="black", poly_linewidth=0.6, poly_facecolor="none",
        alpha=1.0, zorder=8,
    )

    # Overlays
    overlays = [
        ShapefileLayer(
            path=r"\\usden1-stor.dhi.dk\Projects\61803553-05\GIS\SG Coastline\RD7550_CEx_SG_v20250509.shp",
            kind="polygon",
            crs_helper=crs_helper,
            poly_edgecolor="black", poly_linewidth=0.6, poly_facecolor="none",
            alpha=1.0, zorder=10,
        )
    ]

    fig, ani = make_ssc_currents_animation(
        mt_model=mt_model,              # comboMTModel
        hd_model=hd_model,              # comboHDModel
        ssc_scale="log",                # comboScale
        ssc_cmap_name=cmo.cm.turbid,    # combocmap
        ssc_vmin=None,                  # txtvmin
        ssc_vmax=None,                  # txtvmax
        ssc_bottom_thresh=0.001,        # txtCMapBottomThreshold
        ssc_pixel_size_m=25,            # txtPixelSizeM
        axis_tick_decimals=3,           # numAxisTickDecimals
        model_field_pixel_size_m=200.0,       # txtFieldPixelSize
        model_field_quiver_stride_n=3,        # numFieldQuiverStrideN
        model_quiver_scale=12.0,              # txtQuiverScale
        model_quiver_color="white",           # pnlQuiverColor and btnQuiverColor
        animation_time_start_idx=0,               # numericAnimationStartIndex and checkAnimationStartIndex
        animation_time_end_idx=None,              # numericAnimationEndIndex and checkAnimationEndIndex
        animation_time_step=1,                    # numericAnimationTimeStep
        animation_interval_ms=.1,                 # numericAnimationInterval        
        animation_out_path="ssc_currents.gif",    # txtAnimationOutputFile and btnAnimationOutputFile
        
        
        bbox_layer=bbox_layer,
        shapefile_layers=overlays,
        ssc_levels=(0.001, 0.01, 0.1, 1.0, 10.0),
        

        crs_helper=crs_helper,
        ssc_item_number=1,
        u_item_number=4,
        v_item_number=5,
        save_output=True,               # set False to preview only
        writer_kind="gif",
        use_qt_progress=True,

        model_quiver_width=0.001,             # txtQuiverWidth
        model_quiver_headwidth=2.0,           # txtQuiverHeadWidth
        model_quiver_headlength=2.5,          # txtQuiverHeadLength
    )

    plt.show()

