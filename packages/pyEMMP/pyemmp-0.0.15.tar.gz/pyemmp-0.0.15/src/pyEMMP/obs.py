import pandas as pd
from numpy.typing import NDArray
from dataclasses import dataclass, field
from datetime import datetime
import numpy as np
from dateutil import parser

from .plotting import PlottingShell
from .utils import Constants

class OBS():
    def __init__(self, cfg: str) -> None:
        self._cfg = cfg
        self.name = self._cfg.get('name', "MyOBS")
        self.filename = self._cfg.get('filename', None)
        header = self._cfg.get('header', 0)
        sep = self._cfg.get('sep', ',')
        if sep == "Tab":
            sep = "\t"
        elif sep == "WhiteSpaces":
            sep = "\s+"
        df = pd.read_csv(self.filename, header=header, sep=sep, skiprows=header-1)
        
        date_col = self._cfg.get('date_col', 'Date')
        time_col = self._cfg.get('time_col', 'Time')
        depth_col = self._cfg.get('depth_col', 'Depth')
        ntu_col = self._cfg.get('ntu_col', 'NTU')
        df["DateTime"] = pd.to_datetime(df[date_col] + " " + df[time_col], errors="coerce")
        df.drop(columns=[date_col, time_col], inplace=True)
        
        self.position = None # to be added externally as needed
        self.plot = Plotting(self)
        
        def get_valid(cfg, key, default):
            # helper for parsing dictionary values
            val = cfg.get(key, default)
            if val is None:
                return default
            try:
                if isinstance(val, float) and np.isnan(val):
                    return default
            except TypeError:
                pass
            return val
        
        @dataclass
        class OBSData:
            datetime: NDArray[np.datetime64] = field(metadata={"desc": "Datetime values"})
            depth: NDArray[np.float64] = field(metadata={"desc": "Depth values"})
            ntu: NDArray[np.float64] = field(metadata={"desc": "NTU values"})
            ssc: NDArray[np.float64] = field(metadata={"desc": "Calculated SSC values, (mg/L)"})

        self.data = OBSData(
            datetime=df["DateTime"].to_numpy(dtype=np.datetime64),
            depth=df[depth_col].to_numpy(dtype=np.float64),
            ntu=df[ntu_col].to_numpy(dtype=np.float64),
            ssc = None,
        )
        
        
        @dataclass
        class MaskParams:
            start_datetime: datetime = field(metadata={"desc": "Start datetime for masking"})
            end_datetime: datetime = field(metadata={"desc": "End datetime for masking"})
            depthMin: float = field(metadata={"desc": "Minimum depth for masking"})
            depthMax: float = field(metadata={"desc": "Maximum depth for masking"})
            ntuMin: float = field(metadata={"desc": "Minimum NTU for masking"})
            ntuMax: float = field(metadata={"desc": "Maximum NTU for masking"})
            OBSMask: NDArray = field(metadata={"desc": "Mask for OBS data"})

        self.masking = MaskParams(
            start_datetime=np.datetime64(parser.parse(self._cfg.get('start_datetime', Constants._FAR_PAST_DATETIME))),
            end_datetime=np.datetime64(parser.parse(self._cfg.get('end_datetime', Constants._FAR_FUTURE_DATETIME))),
            depthMin=self._cfg.get('depthMin', Constants._LOW_NUMBER),
            depthMax=self._cfg.get('depthMax', Constants._HIGH_NUMBER),
            ntuMin=self._cfg.get('ntuMin', Constants._LOW_NUMBER),
            ntuMax=self._cfg.get('ntuMax', Constants._HIGH_NUMBER),
            OBSMask=None
        )

        self._generate_OBSMask()
        
        @dataclass
        class SSCParams:
            A: float = field(metadata={"desc": "Parameter A in SSC = A * 10^(B * ABS)"})
            B: float = field(metadata={"desc": "Parameter B in SSC = A * 10^(B * ABS)"})
        
        sscpar_cfg = self._cfg.get('ssc_params', {})
        
        self.ssc_params = SSCParams(
            A=get_valid(sscpar_cfg,'A', None),
            B=get_valid(sscpar_cfg,'B', None)
        )
        
        if (self.ssc_params.B):
            self._calculate_SSC()
            
    def _calculate_SSC(self):
        self.data.ssc = self.data.ntu*self.ssc_params.B + self.ssc_params.A

    def _generate_OBSMask(self):
        datetimes = self.data.datetime
        datetime_mask = (datetimes >= self.masking.start_datetime) & (datetimes <= self.masking.end_datetime)

        depths = self.data.depth
        depth_mask = (depths >= self.masking.depthMin) & (depths <= self.masking.depthMax)

        ntus = self.data.ntu
        ntu_mask = (ntus >= self.masking.ntuMin) & (ntus <= self.masking.ntuMax)

        master_mask = np.logical_or.reduce([datetime_mask, depth_mask, ntu_mask])
        self.masking.OBSMask = master_mask
        
class Plotting:
    def __init__(self, obs: OBS) -> None:
        self._obs = obs

    def depth_profile(self,
                     plot_field: str = "ntu",
                     use_spline: bool = False,
                     k: int = 2, # spline order
                     ax=None):
        """
        Connect points in chronological order using self._obs.data.datetime.
        If use_spline, draw a pass-through time-parameterized spline.
        """
        import numpy as np
        from scipy.interpolate import InterpolatedUnivariateSpline, UnivariateSpline
    
        if ax is None:
            fig, ax = PlottingShell.subplots(figheight=5, figwidth=3)
        else:
            fig = ax.figure
    
        depth = np.asarray(self._obs.data.depth, float).ravel()
        if plot_field == "ntu":
            x_raw = np.asarray(self._obs.data.ntu, float).ravel()
            xlabel = "Turbidity (NTU)"
        elif plot_field == "ssc":
            x_raw = np.asarray(self._obs.data.ssc, float).ravel()
            xlabel = "SSC (mg/L)"
        else:
            raise ValueError("plot_field must be 'ntu' or 'ssc'.")
    
        # time as strictly increasing parameter
        t_dt = np.asarray(self._obs.data.datetime, "datetime64[ns]").ravel()
        m = np.isfinite(depth) & np.isfinite(x_raw) & (~np.isnat(t_dt))
        if m.sum() < 2:
            raise ValueError("Need at least 2 valid samples with datetime.")
    
        y = depth[m]
        x = x_raw[m]
        t_dt = t_dt[m]
    
        # sort by time
        order = np.argsort(t_dt)
        y = y[order]
        x = x[order]
        t_dt = t_dt[order]
    
        # numeric time in seconds since first sample
        t_sec = t_dt.astype("int64").astype(np.float64) * 1e-9
        t_sec = t_sec - t_sec[0]
    
        # collapse duplicate timestamps by averaging x,y
        tu, inv, cnt = np.unique(t_sec, return_inverse=True, return_counts=True)
        if tu.size != t_sec.size:
            xu = np.zeros_like(tu, dtype=float)
            yu = np.zeros_like(tu, dtype=float)
            np.add.at(xu, inv, x)
            np.add.at(yu, inv, y)
            x, y, t_sec = (xu / cnt), (yu / cnt), tu
    
        if use_spline and t_sec.size >= 2:
            k_eff = int(max(1, min(int(k), t_sec.size - 1)))

            fx = InterpolatedUnivariateSpline(t_sec, x, k=k_eff)
            fy = InterpolatedUnivariateSpline(t_sec, y, k=k_eff)
  
            te = np.linspace(t_sec.min(), t_sec.max(), max(200, 3 * t_sec.size))
            xe = fx(te)
            ye = fy(te)
            ax.plot(xe, ye, lw=0.5, color="black", alpha=0.7)
        else:
            ax.plot(x, y, lw=0.5, color="black", alpha=0.7)
    
        ax.scatter(x, y, s=3, ec="black", fc="white", marker="s", alpha=1, lw=0.5)
        ax.invert_yaxis()
        ax.set_xlabel(xlabel)
        ax.set_ylabel("Depth (m)")
        ax.set_title(f"{getattr(self._obs,'name','OBS')} Depth Profile")
        
        return fig, ax