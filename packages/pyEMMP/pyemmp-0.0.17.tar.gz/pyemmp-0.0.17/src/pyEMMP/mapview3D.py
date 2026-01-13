# -*- coding: utf-8 -*-
"""
TransectViewer3D (refactored + shapefile-fix)
---------------------------------------------
3D Plotly viewer for ADCP curtain transects with ShapefileLayer overlays.

Highlights
- Accepts pre-built ADCP objects + CRSHelper and a list of ShapefileLayer objects.
- XY in meters (local frame), axes labeled in degrees.
- Graticule at z=0; optional z exaggeration.
- Shapefiles rendered as Scatter3d lines/points at a safe z within the scene.
- Clean code sections & comments for troubleshooting.

Fix in this version
- Shapefile overlays were not visible because they were drawn at z above the
  scene’s z-range. Now we render at z_elev = zmax_scaled - eps (inside range),
  with a tiny epsilon to avoid z-fighting.

Dependencies
- plotly, numpy
- Your codebase: adcp.ADCP (ADCPDataset), utils_crs.CRSHelper,
                 utils_shapefile.ShapefileLayer, utils_xml.XMLUtils (example only)
"""

from __future__ import annotations

# ============================== IMPORTS ==============================
from typing import Any, Dict, List, Optional, Tuple
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio

from .adcp import ADCP as ADCPDataset
from .utils_crs import CRSHelper
from .utils_shapefile import ShapefileLayer
from .utils_xml import XMLUtils  # example call only

pio.renderers.default = "browser"

# ====================================================================
#                         TRANSECT VIEWER 3D
# ====================================================================
class TransectViewer3D:
    """
    Public API
    ----------
    viewer = TransectViewer3D(adcps, crs_helper, inputs, shapefile_layers=[...])
    fig = viewer.render()
    viewer.save_html(path, auto_open=False)
    """

    # --------------------------- INIT ---------------------------
    def __init__(
        self,
        adcps: List[ADCPDataset],
        crs_helper: CRSHelper,
        inputs: Dict[str, Any],
        shapefile_layers: Optional[List[ShapefileLayer]] = None,
        survey_lookup: Optional[Dict[str, Dict[str, Any]]] = None,  # optional meta for hover
    ) -> None:
        self.cfg = dict(inputs)
        self.adcps = list(adcps)
        self.crs_helper = crs_helper
        self.shapefile_layers: List[ShapefileLayer] = list(shapefile_layers or [])
        self.survey_lookup = survey_lookup or {}

        # Frame & ranges populated during build
        self.frame: Dict[str, float] = {}
        self.zmin_true = self.zmax_true = 0.0
        self.zmin_scaled = self.zmax_scaled = 0.0

        self.fig: go.Figure | None = None

    # --------------------- GEOMETRY HELPERS ---------------------
    @staticmethod
    def _meters_per_degree(lat_deg: float) -> Tuple[float, float]:
        lat = np.deg2rad(lat_deg)
        m_per_deg_lat = 111_132.92 - 559.82 * np.cos(2 * lat) + 1.175 * np.cos(4 * lat)
        m_per_deg_lon = 111_412.84 * np.cos(lat) - 93.5 * np.cos(3 * lat)
        return float(m_per_deg_lon), float(m_per_deg_lat)

    def _global_frame_from_adcps(self) -> Tuple[float, float, float, float]:
        lon = np.concatenate([np.asarray(a.position.x, float).ravel()
                              for a in self.adcps if np.size(a.position.x)])
        lat = np.concatenate([np.asarray(a.position.y, float).ravel()
                              for a in self.adcps if np.size(a.position.y)])
        if lon.size == 0 or lat.size == 0:
            raise ValueError("No positions found in ADCP datasets.")

        lon0 = float(np.nanmedian(lon))
        lat0 = float(np.nanmedian(lat))
        m_per_deg_lon, m_per_deg_lat = self._meters_per_degree(lat0)
        return lon0, lat0, m_per_deg_lon, m_per_deg_lat

    @staticmethod
    def _font_color_for_bg(bg_color: str) -> str:
        c = (bg_color or "").strip().lower().replace(" ", "")
        return "#ffffff" if c in ("black", "#000", "#000000", "rgb(0,0,0)") else "#000000"

    @staticmethod
    def _format_field_label(field: str) -> str:
        mapping = {
            "absolute_backscatter": "Absolute Backscatter (dB)",
            "echo_intensity": "Echo Intensity (Counts)",
            "correlation_magnitude": "Correlation Magnitude (Counts)",
            "suspended_solids_concentration": "Suspended Solids Concentration (mg/L)",
        }
        return mapping.get(field, field.replace("_", " ").title())

    @staticmethod
    def _time_bounds(adcp: ADCPDataset) -> Tuple[str, str]:
        try:
            dts = getattr(getattr(adcp, "time", None), "ensemble_datetimes", None)
        except Exception:
            dts = None
        if dts is None:
            return "n/a", "n/a"
        arr = np.array(list(dts), dtype=object).ravel()
        vals = [t for t in arr if t is not None]
        if not vals:
            return "n/a", "n/a"
        start, end = min(vals), max(vals)
        return start.strftime("%Y-%m-%d %H:%M:%S"), end.strftime("%Y-%m-%d %H:%M:%S")

    # ------------------ BUILD CURTAIN SURFACES ------------------
    def _build_curtain_surfaces(self) -> go.Figure:
        field = self.cfg.get("field_name", "absolute_backscatter")
        cmap = self.cfg.get("cmap", "jet")
        vmin = self.cfg.get("vmin", None)
        vmax = self.cfg.get("vmax", None)
        zscale = float(self.cfg.get("zscale", 1.0))
        bg_color = self.cfg.get("bgcolor", "black")
        hover_fontsize = self.cfg.get("hover_fontsize", None)

        lon0, lat0, m_per_deg_lon, m_per_deg_lat = self._global_frame_from_adcps()
        self.frame = dict(lon0=lon0, lat0=lat0,
                          m_per_deg_lon=m_per_deg_lon, m_per_deg_lat=m_per_deg_lat)

        traces: List[go.Surface] = []
        pool_vals: List[np.ndarray] = []
        z_true_all: List[np.ndarray] = []
        z_scaled_all: List[np.ndarray] = []

        for adcp in self.adcps:
            lon = np.asarray(adcp.position.x, float).ravel()
            lat = np.asarray(adcp.position.y, float).ravel()
            relz = np.asarray(adcp.geometry.relative_beam_midpoint_positions.z, float)  # (t,b,beam)
            vals = np.asarray(adcp.get_beam_data(field_name=field, mask=True), float)   # (t,b,beam)

            if relz.shape != vals.shape:
                raise ValueError(f"{getattr(adcp, 'name', 'ADCP')}: relz {relz.shape} != values {vals.shape}")

            n = min(lon.size, lat.size, vals.shape[0])
            lon, lat, relz, vals = lon[:n], lat[:n], relz[:n], vals[:n]

            v_mean = np.nanmean(vals, axis=2)  # (t,b)
            z_true = np.nanmean(relz, axis=2)  # (t,b), negative down
            z_plot = z_true * zscale           # scaled

            nb = v_mean.shape[1]
            x_m = (lon - lon0) * m_per_deg_lon
            y_m = (lat - lat0) * m_per_deg_lat

            X = np.tile(x_m, (nb, 1))            # (b,t)
            Y = np.tile(y_m, (nb, 1))            # (b,t)
            C = v_mean.T                          # (b,t)
            ZZ_plot = z_plot.T                    # (b,t)
            ZZ_true = z_true.T                    # (b,t)

            mask = ~np.isfinite(C)
            C[mask] = np.nan; ZZ_plot[mask] = np.nan; ZZ_true[mask] = np.nan

            Lon_deg = (X / m_per_deg_lon) + lon0
            Lat_deg = (Y / m_per_deg_lat) + lat0
            custom = np.stack([Lon_deg, Lat_deg], axis=-1)  # (b,t,2)

            start_str, end_str = self._time_bounds(adcp)
            tr_name = str(getattr(adcp, "name", "transect"))
            svy_meta = self.survey_lookup.get(tr_name, {})
            svy_name = str(svy_meta.get("survey", "n/a"))
            svy_id = svy_meta.get("survey_id", "n/a")

            traces.append(
                go.Surface(
                    x=X, y=Y, z=ZZ_plot,
                    surfacecolor=C, customdata=custom,
                    colorscale=cmap, opacity=0.95, showscale=False, name=tr_name,
                    meta=dict(transect=tr_name, start=start_str, end=end_str,
                              survey=svy_name, survey_id=svy_id),
                    hovertemplate=(
                        "<b>%{meta.transect}</b><br>"
                        "survey: %{meta.survey} (ID: %{meta.survey_id})<br>"
                        "start: %{meta.start}<br>"
                        "end: %{meta.end}<br>"
                        "lon = %{customdata[0]:.5f}°<br>"
                        "lat = %{customdata[1]:.5f}°"
                        "<extra></extra>"
                    ),
                )
            )

            valid = C[~np.isnan(C)]
            if valid.size:
                pool_vals.append(valid)
            z_true_all.append(ZZ_true[~np.isnan(ZZ_true)])
            z_scaled_all.append(ZZ_plot[~np.isnan(ZZ_plot)])

        # Color limits
        if vmin is None or vmax is None:
            if pool_vals:
                pool_flat = np.concatenate(pool_vals)
                cmin, cmax = float(np.nanmin(pool_flat)), float(np.nanmax(pool_flat))
            else:
                cmin, cmax = 0.0, 1.0
        else:
            cmin, cmax = float(vmin), float(vmax)

        label_text = self._format_field_label(field)
        font_col = self._font_color_for_bg(bg_color)

        for i, tr in enumerate(traces):
            tr.update(cmin=cmin, cmax=cmax, showscale=(i == 0))
            if i == 0:
                tr.update(colorbar=dict(
                    title=dict(text=label_text, side="right", font=dict(color=font_col)),
                    thickness=15, len=0.33, x=1.02, xanchor="left", y=0.02, yanchor="bottom",
                    bgcolor=bg_color, outlinecolor="#777",
                    tickcolor=font_col, tickfont=dict(color=font_col),
                    ticklen=4, tickwidth=1,
                ))

        # Z ranges
        z_true_all = np.concatenate(z_true_all) if z_true_all else np.array([0.0])
        z_scaled_all = np.concatenate(z_scaled_all) if z_scaled_all else np.array([0.0])
        self.zmin_true = min(float(np.nanmin(z_true_all)), 0.0)
        self.zmax_true = max(float(np.nanmax(z_true_all)), 0.0)
        self.zmin_scaled = min(float(np.nanmin(z_scaled_all)), 0.0)
        self.zmax_scaled = max(float(np.nanmax(z_scaled_all)), 0.0)

        # Figure shell
        if hover_fontsize is None:
            hover_fontsize = max(7, int(self.cfg.get("tick_fontsize", 10) * 0.9))
        hover_bg = "rgba(0,0,0,0.7)" if font_col == "#ffffff" else "rgba(255,255,255,0.9)"

        fig = go.Figure(data=traces)
        fig.update_layout(
            scene=dict(
                xaxis=dict(title=dict(text="Longitude (°)", font=dict(color=font_col)),
                           backgroundcolor=bg_color, showgrid=False, zeroline=False,
                           tickfont=dict(color=font_col)),
                yaxis=dict(title=dict(text="Latitude (°)", font=dict(color=font_col)),
                           backgroundcolor=bg_color, showgrid=False, zeroline=False,
                           tickfont=dict(color=font_col)),
                zaxis=dict(title=dict(text="Depth (m)", font=dict(color=font_col)),
                           backgroundcolor=bg_color, showgrid=False, zeroline=False,
                           showticklabels=False, tickfont=dict(color=font_col)),
            ),
            hoverlabel=dict(font=dict(size=hover_fontsize, color=font_col), bgcolor=hover_bg),
            paper_bgcolor=bg_color, plot_bgcolor=bg_color,
            margin=dict(l=0, r=0, t=30, b=0), template=None,
        )
        return fig

    # ------------------ SHAPEFILE OVERLAYS (FIXED) ------------------
    def _add_shapefiles(self, fig: go.Figure) -> go.Figure:
        """
        Draw ShapefileLayer overlays at a z-level guaranteed to be inside the
        current z-axis range (zmax_scaled - small_epsilon). This avoids both
        clipping (if z is above range) and z-fighting (if z equals a surface).
        """
        if not self.shapefile_layers:
            return fig

        # ---- local frame + safe Z (inside scene range) ----
        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]

        span_z = max(1e-9, float(self.zmax_scaled - self.zmin_scaled))
        # Put overlays just below the top of the visible range
        z_elev = float(self.zmax_scaled - 1e-6 * span_z)

        # ---- adders ----
        def add_line_xyz(xs, ys, color, width, alpha) -> None:
            xs = np.asarray(xs, float); ys = np.asarray(ys, float)
            fig.add_trace(go.Scatter3d(
                x=(xs - lon0) * m_per_deg_lon,
                y=(ys - lat0) * m_per_deg_lat,
                z=np.full_like(xs, z_elev, dtype=float),
                mode="lines",
                line=dict(color=(color or "#00FFAA"), width=float(width or 1.0)),
                opacity=float(alpha if alpha is not None else 1.0),
                showlegend=False, hoverinfo="skip",
            ))

        def add_points_xyz(xs, ys, color, size, texts, tcolor, tsize, alpha) -> None:
            xs = np.asarray(xs, float); ys = np.asarray(ys, float)
            kwargs = dict(
                x=(xs - lon0) * m_per_deg_lon,
                y=(ys - lat0) * m_per_deg_lat,
                z=np.full_like(xs, z_elev, dtype=float),
                mode="markers+text" if texts is not None else "markers",
                marker=dict(size=float(size or 6.0), color=color or "#00FFAA"),
                opacity=float(alpha if alpha is not None else 1.0),
                showlegend=False, hoverinfo="skip",
            )
            if texts is not None:
                kwargs["text"] = texts
                kwargs["textfont"] = dict(size=int(tsize or 11), color=tcolor or "#ffffff")
                kwargs["textposition"] = "top center"
            fig.add_trace(go.Scatter3d(**kwargs))

        # ---- iterate layers ----
        for layer in self.shapefile_layers:
            g = layer.as_gdf()
            if isinstance(g, str) or g is None or g.empty:
                # optional: annotate or print warning; we silently skip here
                continue

            kind = (layer.kind or "").lower().strip()
            alpha = layer.alpha
            # Best-effort geometry fallback if kind is off
            if kind not in {"line", "polygon", "point"}:
                gtypes = set(g.geom_type.str.lower())
                if any(t in gtypes for t in ("point", "multipoint")):
                    kind = "point"
                elif any(t in gtypes for t in ("polygon", "multipolygon")):
                    kind = "polygon"
                else:
                    kind = "line"

            if kind in {"line", "polygon"}:
                line_color = layer.line_color or layer.poly_edgecolor
                line_width = layer.line_width or layer.poly_linewidth

                for geom in g.geometry:
                    if geom is None or geom.is_empty:
                        continue
                    gt = getattr(geom, "geom_type", "").lower()
                    if gt == "linestring":
                        xs, ys = geom.xy
                        add_line_xyz(xs, ys, line_color, line_width, alpha)
                    elif gt == "multilinestring":
                        for part in geom.geoms:
                            xs, ys = part.xy
                            add_line_xyz(xs, ys, line_color, line_width, alpha)
                    elif gt == "polygon":
                        xs, ys = geom.exterior.xy
                        add_line_xyz(xs, ys, layer.poly_edgecolor, layer.poly_linewidth, alpha)
                    elif gt == "multipolygon":
                        for pg in geom.geoms:
                            xs, ys = pg.exterior.xy
                            add_line_xyz(xs, ys, layer.poly_edgecolor, layer.poly_linewidth, alpha)

                # optional label
                if layer.label_text:
                    xmin, ymin, xmax, ymax = g.total_bounds
                    add_points_xyz(
                        [0.5 * (xmin + xmax)], [0.5 * (ymin + ymax)],
                        color=line_color or layer.poly_edgecolor,
                        size=0,
                        texts=[layer.label_text],
                        tcolor=layer.label_color, tsize=layer.label_fontsize, alpha=alpha
                    )

            elif kind == "point":
                xs: List[float] = []; ys: List[float] = []
                for geom in g.geometry:
                    if geom is None or geom.is_empty:
                        continue
                    gt = getattr(geom, "geom_type", "").lower()
                    if gt == "point":
                        xs.append(geom.x); ys.append(geom.y)
                    elif gt == "multipoint":
                        for p in geom.geoms:
                            xs.append(p.x); ys.append(p.y)
                texts = [layer.label_text] * len(xs) if layer.label_text else None
                add_points_xyz(xs, ys, layer.point_color, layer.point_markersize,
                               texts, layer.label_color, layer.label_fontsize, alpha)

        return fig

    # ---------------- GRATICULE / AXES / CAMERA ----------------
    def _add_graticule_equal(
        self, fig: go.Figure,
        lon_min_deg: float, lon_max_deg: float,
        lat_min_deg: float, lat_max_deg: float,
        xr_m: Tuple[float, float], yr_m: Tuple[float, float],
        color: str = "#333", width: int = 1, opacity: float = 0.35, n_lines: int = 9,
    ) -> go.Figure:
        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]
        lon_vals = np.linspace(lon_min_deg, lon_max_deg, n_lines)
        lat_vals = np.linspace(lat_min_deg, lat_max_deg, n_lines)
        z0 = 0.0

        y0_m, y1_m = yr_m
        for LON in lon_vals:
            x_m = (LON - lon0) * m_per_deg_lon
            fig.add_trace(go.Scatter3d(
                x=[x_m, x_m], y=[y0_m, y1_m], z=[z0, z0],
                mode="lines", line=dict(color=color, width=int(width)),
                opacity=float(opacity), showlegend=False, hoverinfo="skip",
            ))
        x0_m, x1_m = xr_m
        for LAT in lat_vals:
            y_m = (LAT - lat0) * m_per_deg_lat
            fig.add_trace(go.Scatter3d(
                x=[x0_m, x1_m], y=[y_m, y_m], z=[z0, z0],
                mode="lines", line=dict(color=color, width=int(width)),
                opacity=float(opacity), showlegend=False, hoverinfo="skip",
            ))
        return fig

    def _apply_axes_camera_and_grids(self, fig: go.Figure) -> go.Figure:
        pad_deg = float(self.cfg.get("pad_deg", 0.05))
        bgcolor = self.cfg.get("bgcolor", "black")

        lon_all = np.concatenate([np.asarray(a.position.x, float).ravel()
                                  for a in self.adcps if np.size(a.position.x)])
        lat_all = np.concatenate([np.asarray(a.position.y, float).ravel()
                                  for a in self.adcps if np.size(a.position.y)])
        lon_min_deg = float(np.nanmin(lon_all)) - pad_deg
        lon_max_deg = float(np.nanmax(lon_all)) + pad_deg
        lat_min_deg = float(np.nanmin(lat_all)) - pad_deg
        lat_max_deg = float(np.nanmax(lat_all)) + pad_deg

        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]

        xr = np.array([(lon_min_deg - lon0) * m_per_deg_lon,
                       (lon_max_deg - lon0) * m_per_deg_lon], float)
        yr = np.array([(lat_min_deg - lat0) * m_per_deg_lat,
                       (lat_max_deg - lat0) * m_per_deg_lat], float)

        # Aspect ratio
        dx = float(xr[1] - xr[0]); dy = float(yr[1] - yr[0])
        span_xy = max(dx, dy) if max(dx, dy) > 0 else 1.0
        dz_scaled = float(self.zmax_scaled - self.zmin_scaled)
        z_ratio = dz_scaled / span_xy if span_xy > 0 else 1.0

        # Degree-axis ticks
        nt = max(2, int(self.cfg.get("axis_ticks", 7)))
        x_tickvals = np.linspace(xr[0], xr[1], nt)
        y_tickvals = np.linspace(yr[0], yr[1], nt)
        dec = int(self.cfg.get("tick_decimals", 4))
        x_ticktext = [f"{lon_min_deg + (lon_max_deg - lon_min_deg)*i/(nt-1):.{dec}f}" for i in range(nt)]
        y_ticktext = [f"{lat_min_deg + (lat_max_deg - lat_min_deg)*i/(nt-1):.{dec}f}" for i in range(nt)]

        font_col = self._font_color_for_bg(bgcolor)
        axis_label_color = self.cfg.get("axis_label_color", font_col)
        axis_label_fontsize = int(self.cfg.get("axis_label_fontsize", 12))
        tick_fontsize = int(self.cfg.get("tick_fontsize", 10))

        fig.update_layout(
            scene=dict(
                xaxis=dict(range=[xr[0], xr[1]], tickmode="array", tickvals=x_tickvals.tolist(), ticktext=x_ticktext,
                           title=dict(text="Longitude (°)", font=dict(color=axis_label_color, size=axis_label_fontsize)),
                           tickfont=dict(color=font_col, size=tick_fontsize),
                           backgroundcolor=bgcolor, showgrid=False, zeroline=False),
                yaxis=dict(range=[yr[0], yr[1]], tickmode="array", tickvals=y_tickvals.tolist(), ticktext=y_ticktext,
                           title=dict(text="Latitude (°)", font=dict(color=axis_label_color, size=axis_label_fontsize)),
                           tickfont=dict(color=font_col, size=tick_fontsize),
                           backgroundcolor=bgcolor, showgrid=False, zeroline=False),
                zaxis=dict(range=[self.zmin_scaled, self.zmax_scaled],
                           showgrid=False, zeroline=False, showticklabels=False,
                           title=dict(text="Depth (m)", font=dict(color=axis_label_color, size=axis_label_fontsize)),
                           tickfont=dict(color=font_col), backgroundcolor=bgcolor),
                aspectmode="manual", aspectratio=dict(x=1, y=1, z=z_ratio),
                camera=dict(up=dict(x=0, y=0, z=1),
                            center=dict(x=0, y=0, z=0),
                            eye=dict(x=0.0, y=-0.45, z=0.22)),
            ),
            paper_bgcolor=bgcolor, plot_bgcolor=bgcolor, uirevision="lock_ranges",
        )

        fig = self._add_graticule_equal(
            fig, lon_min_deg, lon_max_deg, lat_min_deg, lat_max_deg,
            xr_m=(xr[0], xr[1]), yr_m=(yr[0], yr[1]),
            color=self.cfg.get("grid_color", "#333"),
            width=int(self.cfg.get("grid_width", 1)),
            opacity=float(self.cfg.get("grid_opacity", 0.35)),
            n_lines=int(self.cfg.get("grid_lines", 9)),
        )
        return fig

    # --------------------------- PUBLIC ---------------------------
    def render(self) -> go.Figure:
        fig = self._build_curtain_surfaces()
        fig = self._add_shapefiles(fig)  # overlays rendered safely inside z-range
        fig = self._apply_axes_camera_and_grids(fig)
        self.fig = fig
        return fig

    def save_html(self, path: str | None = None, auto_open: bool = False) -> str:
        if self.fig is None:
            raise RuntimeError("Call render() before save_html().")
        out_path = path or self.cfg.get("out", None)
        if not out_path:
            raise ValueError("Provide `path` or set `out` in inputs.")

        html = self.fig.to_html(include_plotlyjs="cdn", full_html=True, div_id="plotly-div")
        inj = self._north_arrow_js()
        low = html.lower()
        if "</body>" in low:
            i = low.rfind("</body>")
            html = html[:i] + inj + html[i:]
        else:
            html = html + inj + "</body>"

        with open(out_path, "w", encoding="utf-8") as f:
            f.write(html)

        if auto_open:
            import webbrowser, pathlib
            webbrowser.open(pathlib.Path(out_path).absolute().as_uri())

        return out_path

    # --------------------- NORTH ARROW OVERLAY ---------------------
    @staticmethod
    def _north_arrow_js() -> str:
        return r"""
<script>
(function(){
  const pad = 75;
  const wrap = document.createElement('div');
  wrap.style.position='fixed';
  wrap.style.top= pad + 'px';
  wrap.style.right= pad + 'px';
  wrap.style.width='56px';
  wrap.style.height='56px';
  wrap.style.zIndex=10000;
  wrap.style.pointerEvents='none';
  wrap.innerHTML = `
    <svg id="northArrow" viewBox="0 0 100 100" width="56" height="56" style="opacity:0.95">
      <g id="arrow" transform="translate(50,50)">
        <polygon points="0,-30 9,10 0,5 -9,10" fill="#ffffff"/>
        <text x="0" y="-34" text-anchor="middle" fill="#ffffff" font-size="14" font-family="Arial">N</text>
      </g>
    </svg>`;
  document.body.appendChild(wrap);

  function norm(v){ const n=Math.hypot(v.x||0,v.y||0,v.z||0); return n?{x:(v.x||0)/n,y:(v.y||0)/n,z:(v.z||0)/n}:{x:0,y:0,z:0}; }
  function cross(a,b){ return {x:a.y*b.z-a.z*b.y, y:a.z*b.x-a.x*b.z, z:a.x*b.y-a.y*b.x}; }
  function dot(a,b){ return (a.x*b.x + a.y*b.y + a.z*b.z); }

  function updateArrow(cam){
    if(!cam || !cam.eye) return;
    const eye = cam.eye, up = cam.up || {x:0,y:0,z:1};
    const v = norm({x:-eye.x, y:-eye.y, z:-eye.z});
    const r = norm(cross(v, up));
    const u = norm(cross(r, v));
    const Y = {x:0,y:1,z:0}; // world north
    const px = dot(Y, r);
    const py = dot(Y, u);
    const deg = Math.atan2(px, py) * 180/Math.PI;
    const g = document.getElementById('arrow');
    if (g) g.setAttribute('transform', `translate(50,50) rotate(${deg})`);
  }

  const gd = document.getElementById('plotly-div');
  function currentCam(){
    const L = gd && gd.layout && gd.layout.scene && gd.layout.scene.camera ? gd.layout.scene.camera : {};
    const eye = L.eye || {x:0.0,y:-0.45,z:0.22};
    const up  = L.up  || {x:0,y:0,z:1};
    return {eye:eye, up:up};
  }

  if (gd) {
    updateArrow(currentCam());
    gd.on('plotly_relayout', (ev) => {
      const eye = {
        x: (ev['scene.camera.eye.x'] ?? ev?.['scene.camera']?.eye?.x ?? currentCam().eye.x),
        y: (ev['scene.camera.eye.y'] ?? ev?.['scene.camera']?.eye?.y ?? currentCam().eye.y),
        z: (ev['scene.camera.eye.z'] ?? ev?.['scene.camera']?.eye?.z ?? currentCam().eye.z)
      };
      const up = {
        x: (ev['scene.camera.up.x'] ?? ev?.['scene.camera']?.up?.x ?? 0),
        y: (ev['scene.camera.up.y'] ?? ev?.['scene.camera']?.up?.y ?? 0),
        z: (ev['scene.camera.up.z'] ?? ev?.['scene.camera']?.up?.z ?? 1)
      };
      updateArrow({eye:eye, up:up});
    });
  }
})();
</script>
"""