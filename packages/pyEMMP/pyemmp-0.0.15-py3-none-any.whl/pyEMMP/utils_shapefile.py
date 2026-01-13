from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional, Tuple, Union
import os
from pathlib import Path
import numpy as np
import geopandas as gpd
import matplotlib.axes as maxes
from shapely.geometry import Polygon, MultiPolygon, box
from shapely.ops import unary_union

from .utils_crs import CRSHelper

@dataclass
class ShapefileLayer:
    """
    Minimal shapefile wrapper with explicit styling and a single layer-wide label.

    Robust bounds():
      1) Use projected GDF total_bounds if available and finite.
      2) Try geometry repair (buffer(0), explode, drop empties) and recompute.
      3) Fallback: compute raw bounds in source CRS and reproject that bbox to project CRS.
    """
    # required
    path: str
    kind: str                    # 'point' | 'line' | 'polygon'
    crs_helper: "CRSHelper"

    # style
    point_color: Optional[str] = None
    point_marker: Optional[str] = None
    point_markersize: Optional[float] = None
    line_color: Optional[str] = None
    line_width: Optional[float] = None
    poly_edgecolor: Optional[str] = None
    poly_linewidth: Optional[float] = None
    poly_facecolor: Optional[str] = None
    alpha: Optional[float] = None
    zorder: Optional[int] = None

    # label
    label_text: Optional[str] = None
    label_fontsize: Optional[float] = None
    label_color: Optional[str] = None
    label_ha: Optional[str] = None
    label_va: Optional[str] = None
    label_zorder: Optional[int] = None
    label_offset_pts: Optional[Tuple[float, float]] = None
    label_offset_data: Optional[Tuple[float, float]] = None

    # behavior
    keep_invalid: bool = True
    try_repair_for_bounds: bool = True

    # internals
    error: Optional[str] = field(default=None, init=False, repr=False)
    _gdf_raw: Optional[gpd.GeoDataFrame] = field(default=None, init=False, repr=False)
    _gdf_proj: Optional[gpd.GeoDataFrame] = field(default=None, init=False, repr=False)

    def __post_init__(self) -> None:
        p = str(Path(self.path))
        if p.startswith("//"):
            p = "\\\\" + p.lstrip("/")
        p = p.replace("/", "\\")
        self.path = p

        kd = str(self.kind).lower().strip()
        if kd not in {"point", "line", "polygon"}:
            self.error = "kind must be 'point', 'line', or 'polygon'."
            return

        if not os.path.exists(self.path):
            self.error = f"Vector file not found: {self.path}"
            return

        try:
            gdf = gpd.read_file(self.path)
        except Exception as e:
            self.error = f"Failed to read vector file: {self.path} :: {e}"
            return

        if getattr(gdf, "crs", None) is None:
            self.error = f"Input dataset has no CRS: {self.path}"
            return

        self._gdf_raw = gdf

        try:
            self._gdf_proj = self.crs_helper.to_project_gdf(gdf)
        except Exception:
            try:
                self._gdf_proj = gdf.to_crs(self.crs_helper.project_crs)
            except Exception as e:
                self.error = f"Reprojection failed to {self.crs_helper.project_crs}: {e}"

    def is_ok(self) -> bool:
        return self._gdf_raw is not None

    def as_gdf(self) -> Union[gpd.GeoDataFrame, str]:
        if self._gdf_proj is not None:
            return self._gdf_proj
        if self.error:
            return self.error
        return "Layer not loaded."

    def bounds(self) -> Union[Tuple[float, float, float, float], str]:
        """Return (xmin, xmax, ymin, ymax) in project CRS with fallbacks."""
        if self._gdf_proj is not None and not self._gdf_proj.empty:
            b = self._gdf_proj.total_bounds  # (minx, miny, maxx, maxy)
            if _finite_bounds(b):
                return float(b[0]), float(b[2]), float(b[1]), float(b[3])

        if self.try_repair_for_bounds and self._gdf_proj is not None:
            gp = self._gdf_proj.copy()
            try:
                gp["geometry"] = gp.geometry.buffer(0)
                gp = gp.explode(index_parts=False, ignore_index=True)
                gp = gp[gp.geometry.notnull() & (~gp.geometry.is_empty)]
                if not gp.empty:
                    b = gp.total_bounds
                    if _finite_bounds(b):
                        return float(b[0]), float(b[2]), float(b[1]), float(b[3])
            except Exception:
                pass

        if self._gdf_raw is not None and not self._gdf_raw.empty:
            try:
                rb = self._gdf_raw.total_bounds
                if _finite_bounds(rb):
                    bbox_poly_raw = gpd.GeoDataFrame(
                        geometry=[box(rb[0], rb[1], rb[2], rb[3])],
                        crs=self._gdf_raw.crs
                    )
                    try:
                        bbox_proj = self.crs_helper.to_project_gdf(bbox_poly_raw)
                    except Exception:
                        bbox_proj = bbox_poly_raw.to_crs(self.crs_helper.project_crs)
                    b = bbox_proj.total_bounds
                    if _finite_bounds(b):
                        return float(b[0]), float(b[2]), float(b[1]), float(b[3])
            except Exception:
                pass

        return "Unable to compute bounds for layer."

    def plot(self, ax: maxes.Axes) -> Union[None, str]:
        g = self.as_gdf()
        if isinstance(g, str):
            return g
        if g.empty:
            return "Layer is empty."

        kd = self.kind.lower()

        if kd == "polygon":
            edgecolor = self.poly_edgecolor or "k"
            linewidth = self.poly_linewidth or 0.8
            facecolor = self.poly_facecolor or "none"
            alpha = self.alpha if self.alpha is not None else 1.0
            zorder = self.zorder if self.zorder is not None else 10
            g.plot(ax=ax, edgecolor=edgecolor, linewidth=linewidth,
                   facecolor=facecolor, alpha=alpha, zorder=zorder)

        elif kd == "line":
            color = self.line_color or "k"
            linewidth = self.line_width or 1.0
            alpha = self.alpha if self.alpha is not None else 1.0
            zorder = self.zorder if self.zorder is not None else 12
            g.plot(ax=ax, color=color, linewidth=linewidth, alpha=alpha, zorder=zorder)

        else:  # point
            color = self.point_color or "k"
            marker = self.point_marker or "o"
            markersize = self.point_markersize or 12
            alpha = self.alpha if self.alpha is not None else 1.0
            zorder = self.zorder if self.zorder is not None else 14
            g.plot(ax=ax, color=color, marker=marker, markersize=markersize,
                   alpha=alpha, zorder=zorder)

        if self.label_text:
            fontsize = self.label_fontsize or 8
            color = self.label_color or "k"
            ha = self.label_ha or "left"
            va = self.label_va or "center"
            lz = self.label_zorder or ((self.zorder or 15) + 1)

            use_pts = self.label_offset_pts is not None
            dx_pts, dy_pts = (self.label_offset_pts or (0, 0))
            dx_dat, dy_dat = (self.label_offset_data or (0.0, 0.0))

            for _, row in g.iterrows():
                geom = row.geometry
                if geom is None or geom.is_empty:
                    continue
                if kd == "point" and getattr(geom, "geom_type", "") == "Point":
                    x, y = geom.x, geom.y
                else:
                    x, y = geom.representative_point().coords[0]

                if use_pts:
                    ax.annotate(
                        self.label_text, xy=(x, y), xytext=(dx_pts, dy_pts),
                        textcoords="offset points", ha=ha, va=va,
                        fontsize=fontsize, color=color, zorder=lz
                    )
                else:
                    ax.text(
                        x + dx_dat, y + dy_dat, self.label_text,
                        fontsize=fontsize, color=color, ha=ha, va=va, zorder=lz
                    )
        return None

    def polygon_mask(self) -> Union[Polygon, MultiPolygon, None, str]:
        g = self.as_gdf()
        if isinstance(g, str) or g.empty or self.kind.lower() != "polygon":
            return None if not isinstance(g, str) else g
        try:
            return unary_union(g.geometry)
        except Exception:
            return None

def _finite_bounds(b) -> bool:
    if b is None or len(b) != 4:
        return False
    return all(np.isfinite(bi) for bi in b)

# ---------------- test for the bbox shapefile ----------------
if __name__ == "__main__":
    import matplotlib.pyplot as plt

    epsg = 4326
    helper = CRSHelper(project_crs=epsg)

    bbox_layer = ShapefileLayer(
        path=r"//usden1-stor.dhi.dk/Projects/61803553-05/GIS/F3/example point layer/extract_model_results.shp",
        kind="polygon",
        crs_helper=helper,
        poly_edgecolor="black",
        poly_linewidth=0.6,
        poly_facecolor="none",
        alpha=1.0,
        zorder=8,
        label_text="Extraction AOI",
        label_fontsize=8,
        label_color="black",
        label_offset_pts=(6, 6),
    )

    b = bbox_layer.bounds()
    print("bounds:", b)

    fig, ax = plt.subplots(figsize=(6, 4))
    err = bbox_layer.plot(ax)
    if isinstance(err, str):
        print("plot error:", err)
    if isinstance(b, tuple):
        xmin, xmax, ymin, ymax = b
        ax.set_xlim(xmin, xmax)
        ax.set_ylim(ymin, ymax)
    ax.set_aspect("equal")
    xlab, ylab = helper.axis_labels()
    ax.set_xlabel(xlab)
    ax.set_ylabel(ylab)
    ax.set_title("BBox Shapefile sanity check")
    plt.tight_layout()
    plt.show()
