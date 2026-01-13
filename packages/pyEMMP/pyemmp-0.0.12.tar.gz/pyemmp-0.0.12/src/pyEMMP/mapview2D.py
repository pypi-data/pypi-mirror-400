# -*- coding: utf-8 -*-
"""
TransectViewer2D — injected dependencies version

- Pass in: adcps (list[ADCPDataset]) and crs_helper (CRSHelper)
- Optional survey name lookup via survey_map={adcp.name: "Survey XYZ"}
- Everything else stays the same (cmap, field_name, vmin/vmax, shp_layers, etc.)
"""

from __future__ import annotations
from typing import Any, Dict, List, Tuple
import numpy as np
import plotly.graph_objects as go
import plotly.io as pio
from plotly.colors import sample_colorscale


from .adcp import ADCP as ADCPDataset
from .utils_crs import CRSHelper
from .utils_shapefile import ShapefileLayer
from .utils_xml import XMLUtils  # only for example construction
from .adcp import ADCP as ADCPDataset
pio.renderers.default = "browser"


class TransectViewer2D:
    """2D ADCP transect viewer (dependencies injected)."""

    def __init__(
        self,
        adcps: List[ADCPDataset],
        crs_helper: CRSHelper,
        inputs: Dict[str, Any],
    ) -> None:
        # ---- injected deps ----
        self.adcps = list(adcps)
        if not self.adcps:
            raise ValueError("adcps must be a non-empty list of ADCPDataset objects.")
        self.crs_helper = crs_helper

        # ---- config ----
        self.cfg = dict(inputs)
        # optional: mapping from adcp.name -> survey name (for hover)
        self.survey_by_name: Dict[str, str] = dict(self.cfg.get("survey_map", {}))

        # overlays (prefer explicit ShapefileLayer objects)
        self.shp_layers: List[ShapefileLayer] = list(self.cfg.get("shp_layers", []))

        # runtime state
        self.frame: Dict[str, float] = {}
        self.fig: go.Figure | None = None
        self.cmin: float = 0.0
        self.cmax: float = 1.0

    # ---------- helpers ----------
    @staticmethod
    def _meters_per_degree(lat_deg: float) -> Tuple[float, float]:
        lat = np.deg2rad(lat_deg)
        m_per_deg_lat = 111_132.92 - 559.82*np.cos(2*lat) + 1.175*np.cos(4*lat)
        m_per_deg_lon = 111_412.84*np.cos(lat) - 93.5*np.cos(3*lat)
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
            "suspended_solids_concentration": "Suspended Solids (mg/L)",
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

    # ---------- series ----------
    def _series_for(self, adcp: ADCPDataset, field: str, vcfg: Dict[str, Any]) -> np.ndarray:
        method = str(vcfg.get("method", "mean")).lower()
        beam = vcfg.get("beam", "mean")

        if method == "mean":
            out, _ = adcp.get_beam_series(field_name=field, mode="bin", target="mean", beam=beam)
            return np.asarray(out, float)

        if method in {"bin", "range", "hab"}:
            if "target" not in vcfg:
                raise ValueError(f"vertical_agg.target required for method='{method}'.")
            out, _ = adcp.get_beam_series(field_name=field, mode=method, target=vcfg["target"], beam=beam)
            return np.asarray(out, float)

        if isinstance(vcfg.get("target", None), str):  # e.g., 'p90'
            out, _ = adcp.get_beam_series(field_name=field, mode="bin", target=vcfg["target"], beam=beam)
            return np.asarray(out, float)

        raise ValueError(f"Unsupported vertical_agg.method: {method}")

    @staticmethod
    def _color_for(value: float, cmin: float, cmax: float, cmap: str) -> str:
        if not np.isfinite(value):
            return "rgba(0,0,0,0)"
        t = 0.5 if cmax <= cmin else (value - cmin) / (cmax - cmin)
        t = float(np.clip(t, 0.0, 1.0))
        return sample_colorscale(cmap, [t])[0]

    # ---------- shapefiles via ShapefileLayer ----------
    def _add_shapefiles(self, fig: go.Figure) -> go.Figure:
        if not self.shp_layers:
            return fig

        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]

        def add_line_xy(xs, ys, color, width, alpha) -> None:
            xs = np.asarray(xs, float); ys = np.asarray(ys, float)
            fig.add_trace(go.Scatter(
                x=(xs - lon0) * m_per_deg_lon,
                y=(ys - lat0) * m_per_deg_lat,
                mode="lines",
                line=dict(color=color or "#00FFAA", width=float(width or 1.0)),
                opacity=float(alpha if alpha is not None else 1.0),
                showlegend=False, hoverinfo="skip"
            ))

        def add_points_xy(xs, ys, color, size, texts, tcolor, tsize, alpha) -> None:
            xs = np.asarray(xs, float); ys = np.asarray(ys, float)
            kwargs = dict(
                x=(xs - lon0) * m_per_deg_lon,
                y=(ys - lat0) * m_per_deg_lat,
                mode="markers+text" if texts is not None else "markers",
                marker=dict(size=float(size or 6.0), color=color or "#00FFAA"),
                opacity=float(alpha if alpha is not None else 1.0),
                showlegend=False, hoverinfo="skip"
            )
            if texts is not None:
                kwargs["text"] = texts
                kwargs["textfont"] = dict(size=int(tsize or 11), color=tcolor or "#ffffff")
                kwargs["textposition"] = "top center"
            fig.add_trace(go.Scatter(**kwargs))

        for layer in self.shp_layers:
            g = layer.as_gdf()
            if isinstance(g, str):
                fig.add_annotation(text=f"Layer error: {layer.path}", showarrow=False,
                                   xref="paper", yref="paper", x=0.01, y=0.01,
                                   xanchor="left", yanchor="bottom",
                                   font=dict(size=10, color="#f66"))
                continue

            kind = layer.kind.lower()
            alpha = layer.alpha
            if kind in {"line", "polygon"}:
                for geom in g.geometry:
                    if geom is None or geom.is_empty:
                        continue
                    gt = getattr(geom, "geom_type", "").lower()
                    if gt == "linestring":
                        xs, ys = geom.xy
                        add_line_xy(xs, ys, layer.line_color or layer.poly_edgecolor, layer.line_width or layer.poly_linewidth, alpha)
                    elif gt == "multilinestring":
                        for part in geom.geoms:
                            xs, ys = part.xy
                            add_line_xy(xs, ys, layer.line_color or layer.poly_edgecolor, layer.line_width or layer.poly_linewidth, alpha)
                    elif gt == "polygon":
                        xs, ys = geom.exterior.xy
                        add_line_xy(xs, ys, layer.poly_edgecolor, layer.poly_linewidth, alpha)
                    elif gt == "multipolygon":
                        for pg in geom.geoms:
                            xs, ys = pg.exterior.xy
                            add_line_xy(xs, ys, layer.poly_edgecolor, layer.poly_linewidth, alpha)
                if layer.label_text:
                    xmin, ymin, xmax, ymax = g.total_bounds
                    add_points_xy([0.5*(xmin+xmax)], [0.5*(ymin+ymax)],
                                  color=layer.poly_edgecolor, size=0,
                                  texts=[layer.label_text],
                                  tcolor=layer.label_color, tsize=layer.label_fontsize, alpha=alpha)
            elif kind == "point":
                xs = []; ys = []
                for geom in g.geometry:
                    if geom is None or geom.is_empty:
                        continue
                    gt = getattr(geom, "geom_type", "").lower()
                    if gt == "point":
                        xs.append(geom.x); ys.append(geom.y)
                    elif gt == "multipoint":
                        for p in geom.geoms:
                            xs.append(p.x); ys.append(p.y)
                texts = [layer.label_text]*len(xs) if layer.label_text else None
                add_points_xy(xs, ys, layer.point_color, layer.point_markersize,
                              texts, layer.label_color, layer.label_fontsize, alpha)
        return fig

    # ---------- graticule ----------
    def _add_graticule_equal(self, fig: go.Figure,
                             lon_min_deg: float, lon_max_deg: float,
                             lat_min_deg: float, lat_max_deg: float,
                             xr_m: Tuple[float, float], yr_m: Tuple[float, float]) -> go.Figure:
        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]

        color = self.cfg.get("grid_color", "#333")
        width = int(self.cfg.get("grid_width", 1))
        opacity = float(self.cfg.get("grid_opacity", 0.35))
        n_lines = int(self.cfg.get("grid_lines", 9))

        lon_vals = np.linspace(lon_min_deg, lon_max_deg, n_lines)
        lat_vals = np.linspace(lat_min_deg, lat_max_deg, n_lines)

        y0_m, y1_m = yr_m
        for LON in lon_vals:
            x_m = (LON - lon0) * m_per_deg_lon
            fig.add_trace(go.Scatter(
                x=[x_m, x_m], y=[y0_m, y1_m], mode="lines",
                line=dict(color=color, width=width), opacity=opacity,
                showlegend=False, hoverinfo="skip"
            ))

        x0_m, x1_m = xr_m
        for LAT in lat_vals:
            y_m = (LAT - lat0) * m_per_deg_lat
            fig.add_trace(go.Scatter(
                x=[x0_m, x1_m], y=[y_m, y_m], mode="lines",
                line=dict(color=color, width=width), opacity=opacity,
                showlegend=False, hoverinfo="skip"
            ))
        return fig

    # ---------- build transects ----------
    def _build_transect_lines(self, fig: go.Figure) -> Tuple[go.Figure, float, float]:
        field = self.cfg.get("field_name", "absolute_backscatter")
        cmap = self.cfg.get("cmap", "jet")
        vmin = self.cfg.get("vmin", None)
        vmax = self.cfg.get("vmax", None)
        lw = float(self.cfg.get("transect_line_width", 3.0))
        vcfg = dict(self.cfg.get("vertical_agg", {"method": "mean"}))

        lon0, lat0, m_per_deg_lon, m_per_deg_lat = self._global_frame_from_adcps()
        self.frame = dict(lon0=lon0, lat0=lat0, m_per_deg_lon=m_per_deg_lon, m_per_deg_lat=m_per_deg_lat)

        # global color limits if not provided
        all_vals: List[np.ndarray] = []
        for adcp in self.adcps:
            try:
                series = self._series_for(adcp, field, vcfg)
                all_vals.append(series[np.isfinite(series)])
            except Exception:
                continue

        if vmin is None or vmax is None:
            if all_vals:
                pool = np.concatenate(all_vals)
                cmin = float(np.nanmin(pool)); cmax = float(np.nanmax(pool))
                if not np.isfinite(cmin) or not np.isfinite(cmax) or cmax == cmin:
                    cmin, cmax = 0.0, 1.0
            else:
                cmin, cmax = 0.0, 1.0
        else:
            cmin, cmax = float(vmin), float(vmax)
        self.cmin, self.cmax = cmin, cmax

        for adcp in self.adcps:
            lon = np.asarray(adcp.position.x, float).ravel()
            lat = np.asarray(adcp.position.y, float).ravel()
            n_pos = min(lon.size, lat.size)
            if n_pos < 2:
                continue
            try:
                series = self._series_for(adcp, field, vcfg).ravel()
            except Exception:
                continue
            n = min(n_pos, series.size)
            lon = lon[:n]; lat = lat[:n]; series = series[:n]

            x_m = (lon - lon0) * m_per_deg_lon
            y_m = (lat - lat0) * m_per_deg_lat

            start_str, end_str = self._time_bounds(adcp)
            tr_name = str(getattr(adcp, "name", "transect"))
            svy_name = str(self.survey_by_name.get(tr_name, "n/a"))

            for i in range(n - 1):
                if not (np.isfinite(series[i]) and np.isfinite(series[i+1])): 
                    continue
                if not (np.isfinite(x_m[i]) and np.isfinite(x_m[i+1]) and
                        np.isfinite(y_m[i]) and np.isfinite(y_m[i+1])): 
                    continue

                cval_mid = 0.5 * (series[i] + series[i+1])
                color = self._color_for(cval_mid, cmin, cmax, cmap)

                lon_mid = 0.5 * (lon[i] + lon[i+1])
                lat_mid = 0.5 * (lat[i] + lat[i+1])
                custom = np.array([[lon_mid, lat_mid, cval_mid], [lon_mid, lat_mid, cval_mid]])

                fig.add_trace(go.Scatter(
                    x=[x_m[i], x_m[i+1]],
                    y=[y_m[i], y_m[i+1]],
                    mode="lines",
                    line=dict(color=color, width=lw),
                    showlegend=False,
                    name=tr_name,
                    customdata=custom,
                    meta=dict(transect=tr_name, start=start_str, end=end_str, survey=svy_name),
                    hovertemplate=(
                        "<b>%{meta.transect}</b><br>"
                        "survey: %{meta.survey}<br>"
                        "start: %{meta.start}<br>"
                        "end: %{meta.end}<br>"
                        "lon = %{customdata[0]:.5f}°<br>"
                        "lat = %{customdata[1]:.5f}°<br>"
                        "value = %{customdata[2]:.3f}"
                        "<extra></extra>"
                    )
                ))

        # Colorbar proxy
        font_col = self._font_color_for_bg(self.cfg.get("bgcolor", "black"))
        fig.add_trace(go.Scatter(
            x=[None], y=[None], mode="markers",
            marker=dict(
                colorscale=cmap,
                cmin=cmin, cmax=cmax, color=[cmin], showscale=True,
                colorbar=dict(
                    title=dict(text=self._format_field_label(field), side="right",
                               font=dict(color=font_col)),
                    thickness=15, len=0.33, x=1.02, xanchor="left", y=0.02, yanchor="bottom",
                    bgcolor=self.cfg.get("bgcolor", "black"),
                    outlinecolor="#777", tickcolor=font_col, tickfont=dict(color=font_col),
                    ticklen=4, tickwidth=1
                )
            ),
            hoverinfo="skip", showlegend=False
        ))
        return fig, cmin, cmax

    # ---------- axes ----------
    def _apply_axes_and_grids(self, fig: go.Figure) -> go.Figure:
        pad_deg = float(self.cfg.get("pad_deg", 0.05))
        bgcolor = self.cfg.get("bgcolor", "black")
        font_col = self._font_color_for_bg(bgcolor)
        axis_label_color = self.cfg.get("axis_label_color", font_col)
        axis_label_fontsize = int(self.cfg.get("axis_label_fontsize", 12))
        tick_fontsize = int(self.cfg.get("tick_fontsize", 10))
        nt = max(2, int(self.cfg.get("axis_ticks", 7)))
        decimals = int(self.cfg.get("tick_decimals", 4))

        lon_all = np.concatenate([np.asarray(a.position.x, float).ravel() for a in self.adcps if np.size(a.position.x)])
        lat_all = np.concatenate([np.asarray(a.position.y, float).ravel() for a in self.adcps if np.size(a.position.y)])
        lon_min_deg = float(np.nanmin(lon_all)) - pad_deg
        lon_max_deg = float(np.nanmax(lon_all)) + pad_deg
        lat_min_deg = float(np.nanmin(lat_all)) - pad_deg
        lat_max_deg = float(np.nanmax(lat_all)) + pad_deg

        lon0 = self.frame["lon0"]; lat0 = self.frame["lat0"]
        m_per_deg_lon = self.frame["m_per_deg_lon"]; m_per_deg_lat = self.frame["m_per_deg_lat"]
        xr = np.array([(lon_min_deg - lon0) * m_per_deg_lon,
                       (lon_max_deg - lon0) * m_per_deg_lon], dtype=float)
        yr = np.array([(lat_min_deg - lat0) * m_per_deg_lat,
                       (lat_max_deg - lat0) * m_per_deg_lat], dtype=float)

        x_tickvals = np.linspace(xr[0], xr[1], nt)
        y_tickvals = np.linspace(yr[0], yr[1], nt)
        x_ticktext = [f"{lon_min_deg + (lon_max_deg - lon_min_deg)*i/(nt-1):.{decimals}f}" for i in range(nt)]
        y_ticktext = [f"{lat_min_deg + (lat_max_deg - lat_min_deg)*i/(nt-1):.{decimals}f}" for i in range(nt)]

        hover_fontsize = int(self.cfg.get("hover_fontsize", max(7, int(tick_fontsize * 0.9))))
        hover_bg = "rgba(0,0,0,0.7)" if font_col == "#ffffff" else "rgba(255,255,255,0.9)"

        margins = self.cfg.get("margins", {"l": 80, "r": 120, "t": 40, "b": 70})
        fig.update_layout(
            xaxis=dict(
                range=[xr[0], xr[1]],
                tickmode="array", tickvals=x_tickvals.tolist(), ticktext=x_ticktext,
                title=dict(text="Longitude (°)", font=dict(color=axis_label_color, size=axis_label_fontsize)),
                tickfont=dict(color=font_col, size=tick_fontsize),
                automargin=True, showgrid=False, zeroline=False,
                scaleanchor="y", scaleratio=1
            ),
            yaxis=dict(
                range=[yr[0], yr[1]],
                tickmode="array", tickvals=y_tickvals.tolist(), ticktext=y_ticktext,
                title=dict(text="Latitude (°)", font=dict(color=axis_label_color, size=axis_label_fontsize)),
                tickfont=dict(color=font_col, size=tick_fontsize),
                automargin=True, showgrid=False, zeroline=False,
            ),
            dragmode="pan",
            paper_bgcolor=bgcolor,
            plot_bgcolor=bgcolor,
            hoverlabel=dict(font=dict(size=hover_fontsize, color=font_col), bgcolor=hover_bg),
            margin=margins,
            template=None,
            showlegend=False
        )

        fig = self._add_graticule_equal(fig,
                                        lon_min_deg, lon_max_deg, lat_min_deg, lat_max_deg,
                                        xr_m=(xr[0], xr[1]), yr_m=(yr[0], yr[1]))
        return fig

    # ---------- public ----------
    def render(self) -> go.Figure:
        fig = go.Figure()
        fig, _, _ = self._build_transect_lines(fig)
        fig = self._add_shapefiles(fig)
        fig = self._apply_axes_and_grids(fig)
        self.fig = fig
        return fig

    def save_html(self, path: str, auto_open: bool = False) -> str:
        if self.fig is None:
            raise RuntimeError("Call render() before save_html().")
        config = self.cfg.get("plotly_config", {
            "scrollZoom": True, "doubleClick": "reset", "displaylogo": False, "responsive": True
        })
        html = self.fig.to_html(include_plotlyjs="cdn", full_html=True, div_id="plotly-div", config=config)
        html = html.replace("</body>", self._north_arrow_js_2d() + "\n</body>")
        with open(path, "w", encoding="utf-8") as f:
            f.write(html)
        if auto_open:
            import webbrowser, pathlib
            webbrowser.open(pathlib.Path(path).absolute().as_uri())
        return path

    @staticmethod
    def _north_arrow_js_2d() -> str:
        return r"""
<script>
(function(){
  const pad = 24;
  const wrap = document.createElement('div');
  wrap.style.position='fixed';
  wrap.style.top= pad + 'px';
  wrap.style.right= pad + 'px';
  wrap.style.width='56px';
  wrap.style.height='56px';
  wrap.style.zIndex=10000;
  wrap.style.pointerEvents='none';
  wrap.innerHTML = `
    <svg viewBox="0 0 100 100" width="56" height="56" style="opacity:0.95">
      <g transform="translate(50,50)">
        <polygon points="0,-30 9,10 0,5 -9,10" fill="#ffffff"/>
        <text x="0" y="-34" text-anchor="middle" fill="#ffffff" font-size="14" font-family="Arial">N</text>
      </g>
    </svg>`;
  document.body.appendChild(wrap);
})();
</script>
"""

def create_temp_html(out_fname: str):
    content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Survey Viewer</title>
  <style>
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: white;
    }
    .message {
      font-size: 20px;
      color: black;
    }
  </style>
</head>
<body>
  <div class="message">Select surveys in the Map Settings to activate the viewer</div>
</body>
</html>"""
    with open(out_fname, "w") as f:
        f.write(content)

def create_load_data_html(out_fname: str):
    content = """<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <title>Survey Viewer</title>
  <style>
    body {
      display: flex;
      justify-content: center;
      align-items: center;
      height: 100vh;
      margin: 0;
      font-family: Arial, sans-serif;
      background-color: white;
    }
    .message {
      font-size: 20px;
      color: black;
    }
  </style>
</head>
<body>
  <div class="message">Load survey data to activate the viewer</div>
</body>
</html>"""
    with open(out_fname, "w") as f:
        f.write(content)
