from __future__ import annotations

from typing import Optional, Tuple, List, Dict, Any, Union
import numpy as np
from scipy.spatial import cKDTree
from pyproj import CRS, Transformer
from mikecore.DfsuFile import DfsuFile

from .utils_crs import CRSHelper


# ---------------- helpers ----------------
def _has_geo_origin_and_orientation(P) -> bool:
    return all(hasattr(P, a) for a in ("Longitude", "Latitude", "Orientation"))

def _crs_from_token_or_wkt(s: str) -> CRS:
    """
    Accepts real WKT, 'EPSG:xxxx', common MIKE tokens like 'LONG/LAT', 'WGS84',
    and 'UTM-<zone>' (north hemisphere by default).
    """
    t = str(s).strip()
    up = t.upper()

    if up.startswith("EPSG:"):
        return CRS.from_user_input(t)

    if up in ("LONG/LAT", "LAT/LONG", "GEOGRAPHIC", "WGS84"):
        return CRS.from_epsg(4326)

    if up.startswith("UTM-"):
        try:
            zone = int(up.split("-")[1])
        except Exception:
            # fall back to WKT parse attempt
            return CRS.from_wkt(t)
        # default to north; callers that need south should replace here if known
        return CRS.from_epsg(32600 + zone)

    # assume it is genuine WKT
    return CRS.from_wkt(t)


def _is_rect_grid_cloud(x: np.ndarray, y: np.ndarray, tol: float = 1e-9) -> bool:
    """
    Heuristic: node cloud looks like a rectilinear lattice if:
      (#unique x) * (#unique y) == n_nodes  (after coarse rounding).
    """
    if x.size != y.size or x.size == 0:
        return False

    def _uniq(v: np.ndarray) -> np.ndarray:
        if v.size < 2:
            return np.unique(v)
        s = np.sort(v)
        d = np.diff(s)
        d = d[np.isfinite(d) & (np.abs(d) > 0)]
        if d.size == 0:
            q = 1.0
        else:
            q = float(np.quantile(d, 0.1))
            if not np.isfinite(q) or q <= 0:
                q = float(np.median(d[d > 0])) if np.any(d > 0) else 1.0
        r = np.round(v / max(q, tol))
        return np.unique(r)

    ux = _uniq(x)
    uy = _uniq(y)
    return int(ux.size) * int(uy.size) == int(x.size)


def _rotate_translate_local_to_EN(
    x_local: np.ndarray,
    y_local: np.ndarray,
    lon0: float,
    lat0: float,
    orientation_deg: float,
    crs_proj: CRS,
) -> Tuple[np.ndarray, np.ndarray]:
    """
    Treat (x_local,y_local) as raw grid coordinates (no absolute meaning).
    Rotate by 'orientation_deg' around the grid-min corner, then translate so
    that the grid-min corner coincides with projected (lon0,lat0).
    """
    tr = Transformer.from_crs(CRS.from_epsg(4326), crs_proj, always_xy=True)
    E0, N0 = tr.transform(float(lon0), float(lat0))

    x0 = float(np.min(x_local))
    y0 = float(np.min(y_local))
    dX = x_local.astype(float) - x0
    dY = y_local.astype(float) - y0

    th = np.deg2rad(float(-orientation_deg))
    ct = np.cos(th)
    st = np.sin(th)

    E = E0 + ct * dX - st * dY
    N = N0 + st * dX + ct * dY
    return E, N


# ---------------- main class ----------------
class DfsuUtils2D:
    """
    DFSU 2D utilities (tri/quad/mixed).

    - Detects DFSU made from grid-local coordinates (from DFS2). If so, rebuilds absolute
      Easting/Northing using projection geo-origin + orientation, then converts to project CRS.
    - Otherwise, assumes stored nodes are already in the mesh CRS and converts to project CRS.
    - All public coordinates are returned in the PROJECT CRS (from CRSHelper).
    - Values are auto-converted to SI on read; DeleteValueFloat is masked to NaN.
    """

    def __init__(self, fname: str, crs_helper: CRSHelper) -> None:
        self.fname = fname
        self._crs = crs_helper
        self.dfsu = DfsuFile.Open(self.fname)

        # delete value cache
        self._DeleteValueFloat = float(self.dfsu.DeleteValueFloat)

        # nodes as stored (may be grid-local if converted from DFS2 without applying rotation)
        x_raw = np.asarray(self.dfsu.X, float)
        y_raw = np.asarray(self.dfsu.Y, float)

        # element connectivity (0-based)
        self._elt_nodes = [np.asarray(e, int) - 1 for e in self.dfsu.ElementTable]
        self._nverts = np.fromiter((len(e) for e in self._elt_nodes), dtype=int)

        # time axis
        self._mt = np.asarray(self.dfsu.GetDateTimes()).astype("datetime64[ns]")

        # mesh CRS (accept WKT / tokens)
        P = self.dfsu.FileInfo.Projection
        self._mesh_wkt = str(P.WKTString)
        self._mesh_crs = _crs_from_token_or_wkt(self._mesh_wkt)

        # detect grid-local & reconstruct absolute if possible
        self._is_grid_local = _has_geo_origin_and_orientation(P) and _is_rect_grid_cloud(x_raw, y_raw)

        if self._is_grid_local:
            E, N = _rotate_translate_local_to_EN(
                x_local=x_raw,
                y_local=y_raw,
                lon0=float(P.Longitude),
                lat0=float(P.Latitude),
                orientation_deg=float(P.Orientation),
                crs_proj=self._mesh_crs,
            )
            Xp, Yp = self._crs.to_project(E, N, from_crs=self._mesh_crs)
        else:
            Xp, Yp = self._crs.to_project(x_raw, y_raw, from_crs=self._mesh_crs)

        # cache nodes and centroids in PROJECT CRS
        self._nodes_proj = np.column_stack([Xp, Yp])

        ne = len(self._elt_nodes)
        cx = np.empty(ne, float)
        cy = np.empty(ne, float)
        emin_x = np.empty(ne, float)
        emax_x = np.empty(ne, float)
        emin_y = np.empty(ne, float)
        emax_y = np.empty(ne, float)
        for i, en in enumerate(self._elt_nodes):
            xi = Xp[en]
            yi = Yp[en]
            cx[i] = xi.mean()
            cy[i] = yi.mean()
            emin_x[i] = xi.min()
            emax_x[i] = xi.max()
            emin_y[i] = yi.min()
            emax_y[i] = yi.max()
        self._centroids_proj = np.column_stack([cx, cy])
        self._emin_x, self._emax_x = emin_x, emax_x
        self._emin_y, self._emax_y = emin_y, emax_y

        self._cent_tree_proj = cKDTree(self._centroids_proj)

        self._items_si = self._build_items_si_summary()

    # ---------- properties ----------
    @property
    def n_items(self) -> int:
        return len(self.dfsu.ItemInfo)

    @property
    def n_timesteps(self) -> int:
        return int(self.dfsu.NumberOfTimeSteps)

    @property
    def n_elements(self) -> int:
        return int(self.dfsu.NumberOfElements)

    @property
    def model_times(self) -> np.ndarray:
        return self._mt

    @property
    def project_crs(self):
        return self._crs.project_crs

    # ---------- geometry ----------
    def get_centroids(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._centroids_proj[:, 0].copy(), self._centroids_proj[:, 1].copy()

    def get_nodes(self) -> Tuple[np.ndarray, np.ndarray]:
        return self._nodes_proj[:, 0].copy(), self._nodes_proj[:, 1].copy()

    def elements_nodes(self):
        return self._elt_nodes, self._nverts

    # ---------- units (auto-SI) ----------
    def _unit_code_to_si(self, u_code: int) -> Tuple[str, float, float]:
        # length
        if u_code == 1000:   # m
            return "m", 1.0, 0.0
        if u_code == 1002:   # mm
            return "m", 0.001, 0.0
        # velocity
        if u_code in (1600, 2000):  # m/s
            return "m/s", 1.0, 0.0
        if u_code == 1602:   # cm/s
            return "m/s", 0.01, 0.0
        # discharge per width
        if u_code == 4700:   # m^3/s/m
            return "m^2/s", 1.0, 0.0
        # concentration
        if u_code == 2205:   # mg/L
            return "kg/m^3", 1e-3, 0.0
        # direction
        if u_code == 2400:   # degrees
            return "deg", 1.0, 0.0
        # areal mass
        if u_code == 4400:   # g/m^2
            return "kg/m^2", 1e-3, 0.0
        return "unknown", 1.0, 0.0

    def _build_items_si_summary(self) -> List[Dict[str, Any]]:
        out: List[Dict[str, Any]] = []
        for i in range(self.n_items):
            info = self.dfsu.ItemInfo[i]
            name = str(getattr(info, "Name", f"item{i+1}"))
            u_code = int(info.Quantity.Unit)
            si_name, _, _ = self._unit_code_to_si(u_code)
            out.append(
                {
                    "index": i + 1,
                    "name": name,
                    "native_unit": str(u_code),
                    "native_code": u_code,
                    "si_target": si_name,
                }
            )
        return out

    def items_summary(self) -> List[Dict[str, Any]]:
        return [dict(d) for d in self._items_si]

    # ---------- time helper ----------
    def _bracket_times(self, t):
        mt = self._mt
        t = np.asarray(t, dtype="datetime64[ns]").ravel()
        a = np.searchsorted(mt, t, side="right")
        b = np.clip(a - 1, 0, mt.size - 1)
        a = np.clip(a, 0, mt.size - 1)
        return b, a

    # ---------- common ----------
    def _mask_delete(self, arr: np.ndarray) -> np.ndarray:
        dv = self._DeleteValueFloat
        if np.isfinite(dv):
            m = (arr == dv)
            if np.any(m):
                arr = arr.astype(float, copy=True)
                arr[m] = np.nan
        return arr

    # ---------- queries ----------
    def locate_elements(self, xq, yq, *, input_crs: Optional[Union[str, int, CRS]] = None):
        if input_crs is None:
            Xp = np.asarray(xq, float).ravel()
            Yp = np.asarray(yq, float).ravel()
        else:
            Xp, Yp = self._crs.to_project(xq, yq, from_crs=input_crs)
        j = self._cent_tree_proj.query(np.column_stack([Xp, Yp]), k=1, workers=-1)[1]
        return np.asarray(j, dtype=int)

    def extract_transect(self, xq, yq, t, item_number: int, *, input_crs=None):
        if not (1 <= item_number <= self.n_items):
            return "Invalid item_number"

        if input_crs is None:
            Xp = np.asarray(xq, float).ravel()
            Yp = np.asarray(yq, float).ravel()
        else:
            Xp, Yp = self._crs.to_project(xq, yq, from_crs=input_crs)
        t = np.asarray(t, dtype="datetime64[ns]").ravel()
        if not (Xp.size == Yp.size == t.size):
            return "xq, yq, t must have equal length."

        j = self._cent_tree_proj.query(np.column_stack([Xp, Yp]), k=1, workers=-1)[1]
        elem_idx = np.asarray(j, int)

        before, after = self._bracket_times(t)
        need_t = np.unique(np.concatenate([before, after]))
        uniq_elems, inv_e = np.unique(elem_idx, return_inverse=True)

        slab = np.empty((need_t.size, uniq_elems.size), float)
        for k, it in enumerate(need_t):
            vals = np.asarray(self.dfsu.ReadItemTimeStep(item_number, int(it)).Data, float)
            vals = self._mask_delete(vals)
            slab[k, :] = vals[uniq_elems]

        kb = np.searchsorted(need_t, before)
        ka = np.searchsorted(need_t, after)
        v0 = slab[kb, inv_e]
        v1 = slab[ka, inv_e]

        mt = self._mt
        dt = (mt[after] - mt[before]) / np.timedelta64(1, "s")
        dt = np.where(dt == 0, 1.0, dt)
        w1 = (t - mt[before]) / np.timedelta64(1, "s") / dt
        data_native = (1.0 - w1) * v0 + w1 * v1

        u_code = int(self.dfsu.ItemInfo[item_number - 1].Quantity.Unit)
        _, a, b = self._unit_code_to_si(u_code)
        data_si = a * data_native + b
        return data_si, t, elem_idx

    def extract_transect_idw(self, xq, yq, t, item_number: int, k: int = 6, p: float = 2.0, *, input_crs=None):
        if not (1 <= item_number <= self.n_items):
            return "Invalid item_number"

        if input_crs is None:
            Xp = np.asarray(xq, float).ravel()
            Yp = np.asarray(yq, float).ravel()
        else:
            Xp, Yp = self._crs.to_project(xq, yq, from_crs=input_crs)
        t = np.asarray(t, dtype="datetime64[ns]").ravel()
        if not (Xp.size == Yp.size == t.size):
            return "xq, yq, t must have equal length."

        k_eff = min(int(k), self._centroids_proj.shape[0])
        d, j = self._cent_tree_proj.query(np.column_stack([Xp, Yp]), k=k_eff, workers=-1)
        if k_eff == 1:
            d = d[:, None]; j = j[:, None]
        elem_nn = np.asarray(j, int)

        with np.errstate(divide="ignore", invalid="ignore"):
            w = 1.0 / np.maximum(d, 1e-12) ** float(p)
        zero = d <= 1e-12
        if np.any(zero):
            w[zero] = 0.0
            rr, cc = np.where(zero)
            w[rr, cc] = 1.0
        wsum = w.sum(axis=1, keepdims=True)
        w = np.divide(w, wsum, out=np.zeros_like(w), where=wsum > 0)

        mt = self._mt
        after = np.searchsorted(mt, t, side="right")
        before = np.clip(after - 1, 0, mt.size - 1)
        after = np.clip(after, 0, mt.size - 1)
        need_t = np.unique(np.concatenate([before, after]))

        uniq_elems, _ = np.unique(elem_nn.ravel(), return_inverse=True)
        slab = np.empty((need_t.size, uniq_elems.size), float)
        for r, it in enumerate(need_t):
            vals = np.asarray(self.dfsu.ReadItemTimeStep(item_number, int(it)).Data, float)
            vals = self._mask_delete(vals)
            slab[r, :] = vals[uniq_elems]
        col_map = {e: i for i, e in enumerate(uniq_elems)}
        col_idx = np.vectorize(col_map.get, otypes=[int])(elem_nn)

        kb = np.searchsorted(need_t, before)
        ka = np.searchsorted(need_t, after)
        v0 = slab[kb[:, None], col_idx]
        v1 = slab[ka[:, None], col_idx]

        dt = (mt[after] - mt[before]) / np.timedelta64(1, "s")
        dt = np.where(dt == 0, 1.0, dt)
        w1t = (t - mt[before]) / np.timedelta64(1, "s") / dt
        vt = (1.0 - w1t)[:, None] * v0 + w1t[:, None] * v1

        data_native = np.sum(w * vt, axis=1)

        u_code = int(self.dfsu.ItemInfo[item_number - 1].Quantity.Unit)
        _, a, b = self._unit_code_to_si(u_code)
        data_si = a * data_native + b
        return data_si, t, elem_nn, w

    def rasterize_idw_bbox(
        self,
        item_number: int,
        bbox: Tuple[float, float, float, float],  # (xmin, xmax, ymin, ymax) in input_crs if given
        t,
        pixel_size_m: float = 10.0,
        k: int = 8,
        p: float = 2.0,
        *,
        input_crs: Optional[Union[str, int, CRS]] = None,
    ):
        if not (1 <= item_number <= self.n_items):
            return "Invalid item_number"

        xmin, xmax, ymin, ymax = map(float, bbox)
        if input_crs is not None:
            xmin, ymin, xmax, ymax = self._crs.bbox_to_project((xmin, ymin, xmax, ymax), from_crs=input_crs)

        if not (np.isfinite([xmin, xmax, ymin, ymax]).all() and xmax > xmin and ymax > ymin):
            return "Invalid bbox"

        width = xmax - xmin
        height = ymax - ymin

        if self._crs.is_geographic:
            lat0 = 0.5 * (ymin + ymax)
            phi = np.deg2rad(lat0)
            m_per_deg_lat = 111132.92 - 559.82*np.cos(2*phi) + 1.175*np.cos(4*phi) - 0.0023*np.cos(6*phi)
            m_per_deg_lon = 111412.84*np.cos(phi) - 93.5*np.cos(3*phi) + 0.118*np.cos(5*phi)
            dx_deg = pixel_size_m / max(m_per_deg_lon, 1e-9)
            dy_deg = pixel_size_m / max(m_per_deg_lat, 1e-9)
            nx = max(2, int(np.ceil(width / max(dx_deg, 1e-12))))
            ny = max(2, int(np.ceil(height / max(dy_deg, 1e-12))))
        else:
            nx = max(2, int(np.ceil(width / max(pixel_size_m, 1e-12))))
            ny = max(2, int(np.ceil(height / max(pixel_size_m, 1e-12))))

        dx = width / nx
        dy = height / ny
        gx = xmin + (np.arange(nx) + 0.5) * dx
        gy = ymin + (np.arange(ny) + 0.5) * dy
        Xg, Yg = np.meshgrid(gx, gy)

        C = self._centroids_proj
        tree = self._cent_tree_proj
        k_eff = min(int(k), C.shape[0])
        d, j = tree.query(np.column_stack([Xg.ravel(), Yg.ravel()]), k=k_eff, workers=-1)
        if k_eff == 1:
            d = d[:, None]; j = j[:, None]

        with np.errstate(divide="ignore", invalid="ignore"):
            w = 1.0 / np.maximum(d, 1e-12) ** float(p)
        zero = d <= 1e-12
        if np.any(zero):
            w[zero] = 0.0
            rr, cc = np.where(zero)
            w[rr, cc] = 1.0
        wsum = w.sum(axis=1, keepdims=True)
        w = np.divide(w, wsum, out=np.zeros_like(w), where=wsum > 0)

        # time window
        mt = self._mt
        t = np.asarray(t, dtype="datetime64[ns]").ravel()
        if t.size == 0:
            return "t must be non-empty."
        tmin, tmax = t.min(), t.max()
        tidx = np.where((mt >= tmin) & (mt <= tmax))[0]
        if tidx.size == 0:
            before, after = self._bracket_times(t)
            tidx = np.unique(np.concatenate([before, after]))
            if tidx.size == 0:
                return "No model timesteps intersect the provided time range."

        elems_needed = np.unique(j.ravel())
        vals = np.empty((tidx.size, elems_needed.size), dtype=float)
        for r, it in enumerate(tidx):
            all_e = np.asarray(self.dfsu.ReadItemTimeStep(item_number, int(it)).Data, float)
            all_e = self._mask_delete(all_e)
            vals[r, :] = all_e[elems_needed]
        elem_mean = np.nanmean(vals, axis=0)

        col_map = np.empty(C.shape[0], dtype=int)
        col_map.fill(-1)
        col_map[elems_needed] = np.arange(elems_needed.size)
        col_idx = col_map[j]

        Z_native = np.sum(w * elem_mean[col_idx], axis=1).reshape(ny, nx)

        u_code = int(self.dfsu.ItemInfo[item_number - 1].Quantity.Unit)
        _, a, b = self._unit_code_to_si(u_code)
        Z_si = a * Z_native + b

        extent = (xmin, xmax, ymin, ymax)
        return (Z_si, extent)


if __name__ == "__main__":
    
    
    crs_helper = CRSHelper(project_crs = 4326)

    model_fpath = r'//usden1-stor.dhi.dk/Projects/61803553-05/Models/F3/2024/10. October/MT/test2.dfsu'
    mt_model = DfsuUtils2D(model_fpath, crs_helper)  
    mt_model.items_summary()