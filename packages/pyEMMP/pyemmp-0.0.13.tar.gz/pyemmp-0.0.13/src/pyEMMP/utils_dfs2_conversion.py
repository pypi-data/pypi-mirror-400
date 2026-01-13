"""
DFS2 -> DFSU with derived U/V from P/Q and water depth.

Rules
-----
- MIKE HD fluxes: P = h*u (x-flux), Q = h*v (y-flux).
- Compute u = P / h, v = Q / h.
- Prefer "Water Depth" if present. Else derive h = max(0, WaterLevel - BedLevel).
- Mask where h <= h_min or inputs are delete/NaN.
- Write all original items, then U/V items.

Dependencies: DHI mikecore (MIKE SDK), NumPy, PyQt5 (for progress UI).
"""

from __future__ import annotations
from datetime import datetime
import os
import re
import numpy as np

from mikecore.DfsFileFactory import DfsFileFactory
from mikecore.DfsuBuilder import DfsuBuilder, DfsuFileType
from mikecore.DfsFactory import DfsFactory
from mikecore.eum import eumQuantity, eumItem, eumUnit


# -----------------------------
# Progress dialog (topmost, cancel)
# -----------------------------
class _QtProgress:
    """Minimal topmost progress with Cancel."""
    def __init__(self, title="DFS2 → DFSU"):
        from PyQt5 import QtWidgets, QtCore
        self.QtWidgets, self.QtCore = QtWidgets, QtCore
        self.app = QtWidgets.QApplication.instance() or QtWidgets.QApplication([])
        self.cancelled = False
        self.suffix = ""

        self.dlg = QtWidgets.QDialog()
        self.dlg.setWindowTitle(title)
        self.dlg.setModal(False)
        self.dlg.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint, True)
        self.dlg.setFixedWidth(560)

        lay = QtWidgets.QVBoxLayout(self.dlg)
        self.label = QtWidgets.QLabel("Starting…")
        self.detail = QtWidgets.QLabel("")
        self.detail.setStyleSheet("color:#555;")
        self.bar = QtWidgets.QProgressBar()
        self.bar.setRange(0, 100)
        self.bar.setFormat("%p%")

        btn_row = QtWidgets.QHBoxLayout()
        btn_row.addStretch(1)
        self.btn_cancel = QtWidgets.QPushButton("Cancel")
        self.btn_cancel.clicked.connect(self._on_cancel)
        btn_row.addWidget(self.btn_cancel)

        lay.addWidget(self.label)
        lay.addWidget(self.detail)
        lay.addWidget(self.bar)
        lay.addLayout(btn_row)

        self.dlg.show()
        self.dlg.raise_()
        self.dlg.activateWindow()
        self.app.processEvents(self.QtCore.QEventLoop.AllEvents)

    def set_suffix(self, text: str):
        self.suffix = f" {text}" if text else ""

    def _on_cancel(self):
        self.cancelled = True

    def update(self, pct: float, msg: str = "", detail: str = ""):
        p = max(0, min(100, int(round(float(pct)))))
        self.bar.setValue(p)

        fmt = "%p%"
        if msg:
            self.label.setText(str(msg))
            fmt = f"%p% — {msg}"
        if self.suffix:
            fmt = f"{fmt} {self.suffix}"
        self.bar.setFormat(fmt)

        if detail:
            self.detail.setText(str(detail))

        self.dlg.raise_()
        self.dlg.activateWindow()
        self.app.processEvents(self.QtCore.QEventLoop.AllEvents)

    def close(self):
        self.dlg.close()
        self.app.processEvents()


# -----------------------------
# Helpers
# -----------------------------
def _times_seconds(ta_obj) -> np.ndarray:
    """Return time vector [s] from TimeAxis."""
    dt_attr = getattr(ta_obj, "TimeStep", None)
    n_attr = getattr(ta_obj, "NumberOfTimeSteps", None) or getattr(ta_obj, "Count", None)
    if (dt_attr is not None) and (n_attr is not None):
        n = int(n_attr)
        dt_s = float(dt_attr)
        return np.arange(n, dtype=float) * dt_s
    times = getattr(ta_obj, "Times", None)
    return np.asarray(list(times), dtype=float) if times is not None else np.array([0.0], float)


def _build_projection_from_dfs2(dfs2):
    """Rebuild projection with geo-origin + orientation when available."""
    P = dfs2.FileInfo.Projection
    wkt = str(P.WKTString)
    has_lon = hasattr(P, "Longitude")
    has_lat = hasattr(P, "Latitude")
    has_ori = hasattr(P, "Orientation")
    if has_lon and has_lat and has_ori:
        lon = float(P.Longitude)
        lat = float(P.Latitude)
        ori = float(P.Orientation)
        return DfsFactory().CreateProjectionGeoOrigin(wkt, lon, lat, ori)
    return DfsFactory().CreateProjection(wkt)


def _grid_nodes_from_dfs2(dfs2):
    """Return node coords (Xn, Yn) and grid dims (nx, ny)."""
    ax = dfs2.SpatialAxis
    nx, ny = int(ax.XCount), int(ax.YCount)
    dx, dy = float(ax.Dx), float(ax.Dy)
    x0, y0 = float(ax.X0), float(ax.Y0)

    ii = np.arange(nx + 1, dtype=float)
    jj = np.arange(ny + 1, dtype=float)
    I, J = np.meshgrid(ii, jj, indexing="xy")

    Xn = (x0 + I * dx).ravel(order="C").astype(np.float64)
    Yn = (y0 + J * dy).ravel(order="C").astype(np.float64)
    return Xn, Yn, nx, ny


# ---- Item detection ----
_PAT = {
    "pflux": re.compile(r"\b(p[-\s_]?flux|flux[-\s_]?p)\b", re.I),
    "qflux": re.compile(r"\b(q[-\s_]?flux|flux[-\s_]?q)\b", re.I),
    "wdepth": re.compile(r"\b(water\s*depth|total\s*water\s*depth|depth)\b", re.I),
    "wlevel": re.compile(r"\b(water\s*level|surface\s*elev(ation)?)\b", re.I),
    "bed": re.compile(r"\b(bed\s*level|bed\s*elev(ation)?)\b", re.I),
}


def _classify_items(dfs2):
    """
    Map item names -> indices for P, Q, h sources.

    Returns
    -------
    idx_p, idx_q, idx_h, idx_eta, idx_zb
      Indices are 1-based for MIKE read calls. None if not found.
    """
    idx_p = idx_q = idx_h = idx_eta = idx_zb = None
    for k, info in enumerate(dfs2.ItemInfo, start=1):
        name = str(getattr(info, "Name", "") or "")
        n = name.strip()
        if idx_p is None and _PAT["pflux"].search(n):
            idx_p = k
        elif idx_q is None and _PAT["qflux"].search(n):
            idx_q = k
        elif idx_h is None and _PAT["wdepth"].search(n):
            idx_h = k
        elif idx_eta is None and _PAT["wlevel"].search(n):
            idx_eta = k
        elif idx_zb is None and _PAT["bed"].search(n):
            idx_zb = k
    return idx_p, idx_q, idx_h, idx_eta, idx_zb


def _compute_h(depth_arr, eta_arr, zb_arr):
    """
    Choose water depth array h from available inputs.
    Priority: depth_arr if provided, else max(0, eta - zb).
    """
    if depth_arr is not None:
        return depth_arr
    if eta_arr is not None and zb_arr is not None:
        h = eta_arr - zb_arr
        np.maximum(h, 0.0, out=h)
        return h
    return None


# -----------------------------
# Converter
# -----------------------------
def Dfs2_to_Dfsu(in_path,
                 out_path,
                 *,
                 show_qt_progress: bool = True,
                 compute_uv: bool = True,
                 h_min: float = 0.01):
    """
    Convert DFS2 to 2D DFSU with original items and optional derived U/V.

    Parameters
    ----------
    in_path : str
    out_path : str
    show_qt_progress : bool
        Show topmost progress with Cancel.
    compute_uv : bool
        If True, append U/V derived from P/Q and water depth.
    h_min : float
        Minimum depth cutoff for velocity derivation.

    Returns
    -------
    True | str
        True on success. String message on early exit or cancel.
    """
    ui = _QtProgress() if show_qt_progress else None
    if ui:
        from os.path import basename
        ui.set_suffix(f"[{basename(in_path)} → {basename(out_path)}]")
    report = (ui.update if ui else (lambda *a, **k: None))

    if os.path.exists(out_path):
        os.remove(out_path)

    report(2, "Opening DFS2")
    dfs2 = DfsFileFactory.Dfs2FileOpen(str(in_path))

    # Axis / time
    ax = dfs2.SpatialAxis
    nx = int(ax.XCount)
    ny = int(ax.YCount)
    ta = dfs2.FileInfo.TimeAxis

    start_time = getattr(ta, "StartDateTime", None)
    if not isinstance(start_time, datetime):
        start_time = datetime(2000, 1, 1)

    tsec = _times_seconds(ta).astype(float)
    n_steps = int(tsec.size) if tsec.size else 1
    if tsec.size == 0:
        tsec = np.array([0.0], dtype=float)
    dt_header = float(tsec[1] - tsec[0]) if n_steps > 1 else 1.0

    # Nodes (raw grid)
    report(8, "Building nodes", f"nx={nx}, ny={ny}")
    Xn, Yn, nx_chk, ny_chk = _grid_nodes_from_dfs2(dfs2)
    assert nx_chk == nx and ny_chk == ny
    n_node = (ny + 1) * (nx + 1)
    Zn = np.zeros(n_node, dtype=np.float32)
    codes = np.ones(n_node, dtype=np.int32)

    # Elements (quads)
    report(12, "Building elements")
    node_id = (np.arange(n_node).reshape(ny + 1, nx + 1) + 1).astype(np.int32)
    elements = []
    for j in range(ny):
        for i in range(nx):
            n00 = node_id[j, i]
            n10 = node_id[j, i + 1]
            n11 = node_id[j + 1, i + 1]
            n01 = node_id[j + 1, i]
            elements.append(np.asarray([n00, n10, n11, n01], dtype=np.int32))

    if not elements:
        if ui:
            ui.close()
        if dfs2:
            dfs2.Close()
        return "No valid cells to convert."

    # Projection
    report(16, "Creating projection")
    proj = _build_projection_from_dfs2(dfs2)

    # DFSU type
    two_d = None
    for m in DfsuFileType:
        if "2D" in m.name.upper() or "MESH2" in m.name.upper():
            two_d = m
            break
    if two_d is None:
        if ui:
            ui.close()
        dfs2.Close()
        return "No 2D DfsuFileType found."

    # Detect items for U/V derivation
    idx_p, idx_q, idx_h, idx_eta, idx_zb = _classify_items(dfs2)
    can_make_uv = compute_uv and (idx_p is not None) and (idx_q is not None) and (idx_h is not None or (idx_eta is not None and idx_zb is not None))

    # Build DFSU
    n_items_src = len(dfs2.ItemInfo)
    n_items_out = n_items_src + (2 if can_make_uv else 0)

    report(20, "Creating DFSU file", f"items={n_items_out}, start={start_time.isoformat()}")
    builder = DfsuBuilder.Create(two_d)
    builder.SetNodes(Xn, Yn, Zn, codes)
    builder.SetElements(elements)
    builder.SetProjection(proj)               # set BEFORE CreateFile
    builder.SetTimeInfo(start_time, float(dt_header))

    # Add original items (keep names and quantities)
    for k in range(n_items_src):
        info = dfs2.ItemInfo[k]
        qty = getattr(info, "Quantity", None) or eumQuantity.Create(
            eumItem.eumIGeneral, eumUnit.eumUunitUndefined
        )
        builder.AddDynamicItem(info.Name, qty)

    # Add derived items if possible

    if can_make_uv:
        u_qty = eumQuantity.Create(eumItem.eumIuVelocity, eumUnit.eumUmeterPerSec)
        v_qty = eumQuantity.Create(eumItem.eumIvVelocity, eumUnit.eumUmeterPerSec)
        builder.AddDynamicItem("U velocity", u_qty)
        builder.AddDynamicItem("V velocity", v_qty)

    dfsu = builder.CreateFile(str(out_path))

    # Stream data
    report(30, "Writing data", f"steps={n_steps}, items={n_items_out}")
    total_frames = max(1, n_steps * n_items_out)
    wrote = 0

    dv_in = dfs2.FileInfo.DeleteValueFloat
    dv_out = dfsu.DeleteValueFloat

    def _clean(a: np.ndarray) -> np.ndarray:
        """Map dfs2 delete -> NaN for math, keep array float32 later."""
        a = np.asarray(a, dtype=float)
        a[a == dv_in] = np.nan
        return a

    for it in range(n_steps):
        t_sec = float(tsec[it])
        # 1) Write original items as-is (mapped delete -> dfsu delete)
        for k in range(1, n_items_src + 1):
            vals = dfs2.ReadItemTimeStep(k, it).Data
            vals = np.asarray(vals, dtype=float)
            mask = vals == dv_in
            vals[mask] = dv_out
            elem_vals = vals.reshape(ny, nx).ravel(order="C").astype(np.float32, copy=False)
            dfsu.WriteItemTimeStepNext(t_sec, elem_vals)

            wrote += 1
            pct = 30 + 68 * (wrote / total_frames)
            if ui and ui.cancelled:
                dfsu.Close(); dfs2.Close()
                if os.path.exists(out_path):
                    os.remove(out_path)
                ui.close()
                return "Cancelled by user"
            report(pct, f"Writing {wrote}/{total_frames}", f"t={t_sec:.3f}s, item={k}/{n_items_out}")

        # 2) Derived U/V from P,Q,h
        if can_make_uv:
            P = _clean(dfs2.ReadItemTimeStep(idx_p, it).Data)
            Q = _clean(dfs2.ReadItemTimeStep(idx_q, it).Data)

            depth_arr = _clean(dfs2.ReadItemTimeStep(idx_h, it).Data) if idx_h is not None else None
            eta_arr = _clean(dfs2.ReadItemTimeStep(idx_eta, it).Data) if idx_eta is not None else None
            zb_arr = _clean(dfs2.ReadItemTimeStep(idx_zb, it).Data) if idx_zb is not None else None

            h = _compute_h(depth_arr, eta_arr, zb_arr)

            if h is None:
                # Cannot compute this step. Write delete arrays for U/V.
                U = np.full_like(P, np.nan)
                V = np.full_like(Q, np.nan)
            else:
                U = P / h
                V = Q / h

                # Mask small/invalid depth or bad inputs
                bad = ~np.isfinite(P) | ~np.isfinite(Q) | ~np.isfinite(h) | (h <= float(h_min))
                U[bad] = np.nan
                V[bad] = np.nan

            # map NaN -> dfsu delete
            U = np.where(np.isfinite(U), U, dv_out)
            V = np.where(np.isfinite(V), V, dv_out)

            elem_u = U.reshape(ny, nx).ravel(order="C").astype(np.float32, copy=False)
            dfsu.WriteItemTimeStepNext(t_sec, elem_u)
            wrote += 1
            pct = 30 + 68 * (wrote / total_frames)
            if ui and ui.cancelled:
                dfsu.Close(); dfs2.Close()
                if os.path.exists(out_path):
                    os.remove(out_path)
                ui.close()
                return "Cancelled by user"
            report(pct, f"Writing {wrote}/{total_frames}", f"t={t_sec:.3f}s, U from P/h")

            elem_v = V.reshape(ny, nx).ravel(order="C").astype(np.float32, copy=False)
            dfsu.WriteItemTimeStepNext(t_sec, elem_v)
            wrote += 1
            pct = 30 + 68 * (wrote / total_frames)
            if ui and ui.cancelled:
                dfsu.Close(); dfs2.Close()
                if os.path.exists(out_path):
                    os.remove(out_path)
                ui.close()
                return "Cancelled by user"
            report(pct, f"Writing {wrote}/{total_frames}", f"t={t_sec:.3f}s, V from Q/h")

    report(98, "Finalizing")
    dfsu.Close()
    dfs2.Close()
    if ui:
        ui.update(100, "Done")
        ui.close()
    return True



if __name__ == '__main__':
    in_path = r'//usden1-stor.dhi.dk/Projects/61803553-05/Models/F3/2024/10. October/MT/MTD20241002.dfs2'
    out_path = r'\\USDEN1-STOR.DHI.DK\Projects\61803553-05\Models\F3\2024\10. October/MT/MTD20241002_1.dfsu'
    
    status = Dfs2_to_Dfsu(in_path, out_path, show_qt_progress=True)
