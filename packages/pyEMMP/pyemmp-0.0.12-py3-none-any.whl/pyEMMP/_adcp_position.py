from typing import Dict, Any
import pandas as pd
import numpy as np

from .utils import Utils, Constants

class ADCPPosition:
    _Vars = ["X", "Y", "Depth", "Pitch", "Roll", "Heading", "DateTime"]

    def __init__(self, cfg: Dict[str, Any]) -> None:
        self._cfg = cfg
        fname = self._cfg.get("filename", "")
        self._fname = Utils._validate_file_path(fname, Constants._TABLE_SUFFIX)
        self._extension = self._fname.suffix.lower()
        self.epsg = int(self._cfg.get("epsg", 4326))
        self._skiprows = int(self._cfg.get("skiprows", 0))
        self._sep = self._cfg.get("sep", ",")
        self._header = int(self._cfg.get("header", 0))
        self._modes = {}
        self._values = {}
        self._columns = {}

        for var in self._Vars:
            self._modes[var] = self._cfg.get(f"{var}_mode", "Variable")
            if self._modes[var] == "Variable":
                col = self._cfg.get(f"{var}_value", "")
                if col:
                    self._columns[var] = col
                else:
                    raise ValueError(f"Variable {var} is set to 'Variable' but no column is specified.")
            else:
                val = self._cfg.get(f"{var}_value", 0.0)
                self._values[var] = pd.to_datetime(val, errors="coerce") if var == "DateTime" else float(val)

        self._all_const = len(self._columns) == 0

        if not self._all_const:
            if self._fname.suffix.lower() == ".csv":
                self._df = pd.read_csv(self._fname, skiprows=self._skiprows, sep=self._sep, header=self._header)
            elif self._fname.suffix.lower() in {".xls", ".xlsx"}:
                self._df = pd.read_excel(self._fname, skiprows=self._skiprows, header=self._header)
            else:
                raise ValueError(f"Unsupported file format: {self._fname.suffix}.")

            missing = [c for c in self._columns.values() if c not in self._df.columns]
            if missing:
                raise KeyError(f"Missing columns in file: {missing}")

            for var in self._columns.keys():
                self._values[var] = self._df[self._columns[var]].to_numpy()

        self.x = self._values["X"]
        self.y = self._values["Y"]
        self.z = self._values["Depth"]
        self.pitch = self._values["Pitch"]
        self.roll = self._values["Roll"]
        self.heading = self._values["Heading"]
        self._t = self._values["DateTime"]

        self._broadcast_constants_to_match_variable_dims()
        self._t = pd.to_datetime(self._t, errors='coerce')

        # Always define x_local_m, y_local_m fields
        if int(self.epsg) == 4326:
            self._init_local_xy_meter_frame()
        else:
            self.x_local_m = np.asarray(self.x, dtype=float)
            self.y_local_m = np.asarray(self.y, dtype=float)
            self.local_origin_lat = np.nan
            self.local_origin_lon = np.nan

        if int(self.epsg) == 4326:
            lat = np.asarray(self.y, dtype=float)
            lon = np.asarray(self.x, dtype=float)
            rad = np.pi / 180.0
            R = 6371000.0
            dlat = np.diff(lat) * rad
            dlon = np.diff(lon) * rad
            a = np.sin(dlat / 2) ** 2 + np.cos(lat[:-1] * rad) * np.cos(lat[1:] * rad) * np.sin(dlon / 2) ** 2
            seg = 2 * R * np.arctan2(np.sqrt(a), np.sqrt(1 - a))
            seg = np.concatenate(([0.0], seg))
            self.distance = np.cumsum(seg)
        else:
            dx = np.diff(self.x)
            dy = np.diff(self.y)
            seg = np.concatenate(([0.0], np.hypot(dx, dy)))
            self.distance = np.cumsum(seg)

    def _resample_to(self, new_times: np.ndarray) -> None:
        df = pd.DataFrame({
            'x': self.x,
            'y': self.y,
            'z': self.z,
            'pitch': self.pitch,
            'roll': self.roll,
            'heading': self.heading,
            'distance': self.distance,
            'x_local_m': getattr(self, 'x_local_m', np.asarray(self.x, dtype=float)),
            'y_local_m': getattr(self, 'y_local_m', np.asarray(self.y, dtype=float)),
        }, index=pd.to_datetime(self._t))

        df_resampled = df.reindex(new_times, method='nearest', tolerance=pd.Timedelta("30s"))
        
        self.x = df_resampled['x'].values
        self.y = df_resampled['y'].values
        self.z = df_resampled['z'].values
        self.pitch = df_resampled['pitch'].values
        self.roll = df_resampled['roll'].values
        self.heading = df_resampled['heading'].values
        self.distance = df_resampled['distance'].values
        self.x_local_m = df_resampled['x_local_m'].values
        self.y_local_m = df_resampled['y_local_m'].values
        self._t = new_times

    def _broadcast_constants_to_match_variable_dims(self) -> None:
        if isinstance(self._t, (float, int)):
            raise RuntimeError("Cannot broadcast: 't' is constant and does not define a target length.")

        n = len(self._t)
        attrs = ['x', 'y', 'z', 'pitch', 'roll', 'heading']

        for attr in attrs:
            val = getattr(self, attr)
            if isinstance(val, (float, int, np.floating, np.integer)):
                setattr(self, attr, np.full(n, float(val), dtype=float))

    def _init_local_xy_meter_frame(self) -> None:
        lat = np.asarray(self.y, dtype=float)
        lon = np.asarray(self.x, dtype=float)
        if lat.size == 0 or np.isnan(lat[0]) or np.isnan(lon[0]):
            valid = ~(np.isnan(lat) | np.isnan(lon))
            if not np.any(valid):
                self.x_local_m = np.zeros_like(lon, dtype=float)
                self.y_local_m = np.zeros_like(lat, dtype=float)
                self.local_origin_lat = np.nan
                self.local_origin_lon = np.nan
                return
            lat0 = float(lat[valid][0])
            lon0 = float(lon[valid][0])
        else:
            lat0 = float(lat[0])
            lon0 = float(lon[0])

        rad = np.pi / 180.0
        R = 6378137.0
        dlat = (lat - lat0) * rad
        dlon = (lon - lon0) * rad
        x_local = R * dlon * np.cos(lat0 * rad)
        y_local = R * dlat

        self.x_local_m = x_local.astype(float, copy=False)
        self.y_local_m = y_local.astype(float, copy=False)
        self.local_origin_lat = lat0
        self.local_origin_lon = lon0

    def set_local_origin(self, lat0: float, lon0: float) -> None:
        if int(self.epsg) != 4326:
            self.x_local_m = np.asarray(self.x, dtype=float)
            self.y_local_m = np.asarray(self.y, dtype=float)
            self.local_origin_lat = np.nan
            self.local_origin_lon = np.nan
            return
        lat = np.asarray(self.y, dtype=float)
        lon = np.asarray(self.x, dtype=float)
        rad = np.pi / 180.0
        R = 6378137.0
        dlat = (lat - lat0) * rad
        dlon = (lon - lon0) * rad
        self.x_local_m = (R * dlon * np.cos(lat0 * rad)).astype(float, copy=False)
        self.y_local_m = (R * dlat).astype(float, copy=False)
        self.local_origin_lat = float(lat0)
        self.local_origin_lon = float(lon0)
