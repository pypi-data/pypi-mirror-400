from pathlib import Path
from typing import List, Tuple, Dict, Optional, Union
from dataclasses import dataclass, field
from datetime import datetime, timedelta
import numpy as np
import numpy.ma as ma
from numpy.lib.stride_tricks import sliding_window_view
from numpy.typing import NDArray
from dateutil import parser
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import matplotlib.gridspec as gridspec
import matplotlib.colors as mcolors
from matplotlib.animation import FuncAnimation, PillowWriter
from matplotlib.collections import LineCollection
from matplotlib.lines import Line2D
from matplotlib.ticker import ScalarFormatter, FuncFormatter
from matplotlib.colors import Normalize, LogNorm
from scipy.ndimage import gaussian_filter1d

from .utils import Utils, Constants, XYZ
from .pd0 import Pd0Decoder
from ._adcp_position import ADCPPosition
from .plotting import PlottingShell

class ADCP():
    """Container for reading, processing, and analyzing ADCP PD0 data.

    This class wraps the full ADCP processing workflow, including:
    file decoding, time and geometry setup, platform position handling,
    velocity transformations, backscatter/SSC derivation, masking, and
    convenience accessors for beam and velocity time series.

    Attributes:
        _cfg (dict): Configuration dictionary for the ADCP object.
        _pd0_path (pathlib.Path): Path to the PD0 (.000) file.
        name (str): Name of the ADCP dataset, typically used in plots
            and outputs.
        _pd0 (Pd0Decoder): Low-level PD0 decoder instance.
        plot (PlottingShell): Helper object for generating plots.
        corrections (ADCPCorrections): Global corrections applied to
            the dataset (magnetic declination, UTC offset, transect
            shifts, etc.).
        time (ADCPTime): Ensemble-level timing and numbering metadata.
        aux_sensor_data (ADCPAuxSensorData): Auxiliary sensor data
            (pressure, tilt, temperature, salinity, etc.).
        position (ADCPPosition): Platform position and orientation time
            series, resampled to ensemble times.
        geometry (ADCPGeometry): Instrument and beam geometry, bin
            spacing, and derived spatial coordinates.
        beam_data (ADCPBeamData): Raw and derived beam-space data
            (echo intensity, correlation magnitude, backscatter, SSC).
        bottom_track (ADCPBottomTrack | None): Bottom-track data and
            derived quantities, if bottom tracking is active.
        velocity (Velocity): Velocity fields in beam, instrument, ship,
            and earth frames, including speed and direction.
        water_properties (WaterProperties): Water-column properties used
            for attenuation and density-related calculations.
        sediment_properties (SedimentProperties): Sediment parameters
            used in SSC and attenuation calculations.
        ssc_params (SSCParams): Calibration parameters for converting
            backscatter to suspended solids concentration.
        abs_params (AbsoluteBackscatterParams): Parameters used in
            absolute backscatter and signal-to-noise calculations.
        masking (MaskParams): Configuration and composite masks for
            velocity and beam data.
        _bt_mode_active (bool): Flag indicating whether bottom track
            data are present and used.
    """
    def __init__(self, cfg: str | Path) -> None:
        """Initialize an ADCP instance from a configuration mapping.

        The configuration is expected to include at least a ``filename``
        entry pointing to a valid PD0 (.000) file. All nested dataclasses
        (time, geometry, beam data, bottom track, water/sediment
        properties, SSC/backscatter parameters, and masking options) are
        initialized here using the PD0 contents and the configuration.

        Args:
            cfg (str | pathlib.Path | dict): Configuration mapping or a
                path to a configuration file that has already been read
                into a dictionary-like object. Must contain a
                ``"filename"`` key pointing to a PD0 file.

        Raises:
            ValueError: If the configuration does not contain a valid
                ``"filename"`` entry for the PD0 file.
        """
        self._cfg = cfg 
        self._pd0_path = self._cfg.get("filename", None)
        self.name = self._cfg.get("name", 'MyADCP')
        

        if self._pd0_path is not None:
            self._pd0_path = Utils._validate_file_path(self._pd0_path, Constants._PD0_SUFFIX)
        else:
            Utils.error(
                logger=self.logger,
                msg=f"Configuration for {self.name} must contain key 'filename' corresponding to a valid path to a PD0 (.000) file.",
                exc=ValueError,
                level=self.__class__.__name__
            )
            
        self._pd0 = Pd0Decoder(self._pd0_path, self._cfg)

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
        class ADCPCorrections:
            magnetic_declination: float = field(metadata={"desc": "Degrees CCW to rotate velocity data to account for magnetic declination"})
            utc_offset: float = field(metadata={"desc": "Hours to shift ensemble datetimes to account for UTC offset"})
            transect_shift_x: float = field(metadata={"desc": "Shifting distance of entire ADCP transect for model calibration (X axis, meters)"})
            transect_shift_y: float = field(metadata={"desc": "Shifting distance of entire ADCP transect for model calibration (Y axis, meters)"})
            transect_shift_t: float = field(metadata={"desc": "Shifting time of entire ADCP transect for model calibration (time axis, hours)"})
            velocity_average_window_len: int = field(metadata={"desc": "Number of ensembles to average (via rolling window) for velocity data"})
            background_ssc: float = field(metadata={"desc": "Background suspended solids concentration (e.g., mg/L) to subtract from SSC estimates"})
            background_ssc_mode: str = field(metadata={"desc": "Method to apply background SSC correction: 'fixed' subtracts a constant value; 'percentile' subtracts a percentile-based value; 'none' applies no correction"})
            
        self.corrections = ADCPCorrections(
            magnetic_declination=float(get_valid(self._cfg, 'magnetic_declination', 0)),
            utc_offset=float(get_valid(self._cfg, 'utc_offset', 0)),
            transect_shift_x=float(get_valid(self._cfg, 'transect_shift_x', 0)),
            transect_shift_y=float(get_valid(self._cfg, 'transect_shift_y', 0)),
            transect_shift_t=float(get_valid(self._cfg, 'transect_shift_t', 0)),
            velocity_average_window_len = int(get_valid(self._cfg, 'velocity_average_window_len', 5)),
            background_ssc_mode = get_valid(self._cfg, 'background_ssc_mode', 'fixed'),
            background_ssc = float(get_valid(self._cfg, 'background_ssc', 0)),
        )
        
        ## Time class
        @dataclass    
        class ADCPTime:
            n_ensembles: int = field(metadata={"desc": "Number of ensembles in the dataset"})
            ensemble_datetimes: int = field(metadata={"desc": "DateTime corresponding to each ensemble in the dataset"})
            ensemble_numbers: NDArray[np.int64] = field(metadata={"desc": "Number corresponding to each ensemble in the dataset. Read directly from source file"})
          
        self.time = ADCPTime(
            n_ensembles = self._pd0._n_ensembles,
            ensemble_datetimes = self._get_datetimes(),
            ensemble_numbers = self._pd0.get_variable_leader_attr('ensemble_number')
            )
        
        @dataclass
        class ADCPAuxSensorData:
            pressure: NDArray[np.float64] = field(
                metadata={"desc": "Water pressure at the transducer head (dbar), scaled from 0.1 Pa. Range: 0–4,294,967 dbar. Requires external pressure sensor; likely manually specified if absent."}
            )
            pressure_var: NDArray[np.float64] = field(
                metadata={"desc": "Pressure variance (dbar²), scaled from 0.1 Pa². Range: 0–4,294,967 dbar². Requires external pressure sensor; likely manually specified if absent."}
            )
            depth_of_transducer: NDArray[np.float64] = field(
                metadata={"desc": "Depth of transducer below water surface (m), scaled from decimeters. Range: 0.1–999.9 m. May be set manually or computed from pressure sensor."}
            )
            temperature: NDArray[np.float64] = field(
                metadata={"desc": "Water temperature (°C), scaled from 0.01°C. Range: -5.00–40.00°C. Requires external temperature sensor; may be manually set if absent."}
            )
            salinity: NDArray[np.float64] = field(
                metadata={"desc": "Water salinity (PSU), 1:1 scaling. Range: 0–40 PSU. Requires external conductivity sensor; typically manually specified."}
            )
            speed_of_sound: NDArray[np.float64] = field(
                metadata={"desc": "Speed of sound (m/s). Range: 1400–1600 m/s. May be derived from temperature, salinity, and pressure; otherwise, manually set."}
            )
            heading: NDArray[np.float64] = field(
                metadata={"desc": "Instrument heading (°), scaled from 0.01°. Range: 0.00–359.99°. Requires internal compass or external gyro."}
            )
            pitch: NDArray[np.float64] = field(
                metadata={"desc": "Pitch angle (°), scaled from 0.01°. Range: -20.00–20.00°. Requires internal tilt sensor."}
            )
            roll: NDArray[np.float64] = field(
                metadata={"desc": "Roll angle (°), scaled from 0.01°. Range: -20.00–20.00°. Requires internal tilt sensor."}
            )
            heading_std: NDArray[np.float64] = field(
                metadata={"desc": "Heading standard deviation (°). Range: 0–180°. Requires internal or external compass."}
            )
            pitch_std: NDArray[np.float64] = field(
                metadata={"desc": "Pitch standard deviation (°), scaled from 0.1°. Range: 0.0–20.0°. Requires internal tilt sensor."}
            )
            roll_std: NDArray[np.float64] = field(
                metadata={"desc": "Roll standard deviation (°), scaled from 0.1°. Range: 0.0–20.0°. Requires internal tilt sensor."}
            )

        self.aux_sensor_data = ADCPAuxSensorData(
            pressure=self._pd0.get_variable_leader_attr("pressure") * 0.001,  # decapascal → dbar
            pressure_var=self._pd0.get_variable_leader_attr("pressure_sensor_variance") * 0.001,
            depth_of_transducer=self._pd0.get_variable_leader_attr("depth_of_transducer_ed") * 0.1,  # dm → m
            temperature=self._pd0.get_variable_leader_attr("temperature_et") * 0.01,
            salinity=self._pd0.get_variable_leader_attr("salinity_es"),
            speed_of_sound= self._pd0.get_variable_leader_attr("speed_of_sound_ec"),
            heading=self._pd0.get_variable_leader_attr("heading_eh") * 0.01,
            pitch=self._pd0.get_variable_leader_attr("pitch_tilt_1_ep") * 0.01,
            roll=self._pd0.get_variable_leader_attr("roll_tilt_2_er") * 0.01,
            heading_std=self._pd0.get_variable_leader_attr("hdg_std_dev")*.1,
            pitch_std=self._pd0.get_variable_leader_attr("pitch_std_dev") * 0.1,
            roll_std=self._pd0.get_variable_leader_attr("roll_std_dev") * 0.1,
        )
        
        ## Platform Position class
        self.position = ADCPPosition(self._cfg['pos_cfg'])
        self.position._resample_to(self.time.ensemble_datetimes)
        
        if np.all(self.position.heading ==0):
            self.position.heading = self.aux_sensor_data.heading
            
        if np.all(self.position.pitch ==0):
            self.position.pitch = self.aux_sensor_data.pitch  
            
        if np.all(self.position.roll ==0):
            self.position.roll = self.aux_sensor_data.roll
        
        @dataclass
        class ADCPGeometry:
            beam_facing: str = field(metadata={"desc": "Beam direction (Up/Down)"})
            n_bins: float = field(metadata={"desc": "Number of bins"})
            n_beams: float = field(metadata={"desc": "Number of beams"})
            beam_angle: float = field(metadata={"desc": "Beam angle in degrees from vertical"})
            bin_1_distance: float = field(metadata={"desc": "Distance to the center of the first bin (m)"})
            bin_length: float = field(metadata={"desc": "Vertical length of each measurement bin (m)"})
            bin_midpoint_distances: NDArray[np.float64] = field(metadata={"desc": "Array of distances from ADCP to bin centers (m)"})
            beam_dr: float  = field(metadata={"desc": "distance between center of transducer and center of instrument (m)"})
            crp_offset_x: float = field(metadata={"desc": "Offset of ADCP from platform CRP (X axis, meters)"})
            crp_offset_y: float = field(metadata={"desc": "Offset of ADCP from platform CRP (Y axis, meters)"})
            crp_offset_z: float = field(metadata={"desc": "Offset of ADCP from platform CRP (Z axis, meters)"})
            crp_rotation_angle: float = field(metadata={"desc": "CCW rotation of ADCP in casing (degrees)"})
            relative_beam_origin: NDArray[np.float64] = field (metadata = {"desc": "Relative XYZ position of the beams with respect to CRP"})
            relative_beam_midpoint_positions: NDArray[np.float64] = field(metadata={"desc": "XYZ position of each beam/bin/ensemble pair relative to centroid of transducer faces (meters, pos above, neg below)"})
            geographic_beam_midpoint_positions: NDArray[np.float64] = field(metadata={"desc": f"geographic XYZ position of each beam/bin/ensemble pair (meters) , EPSG {self.position.epsg}"})
            HAB_beam_midpoint_distances: NDArray[np.float64] = field(metadata={"desc": "Array of distances from seabed to bin centers (m)"})

        self.geometry = ADCPGeometry(
            beam_facing=self._pd0.fixed_leaders[0].system_configuration.beam_facing.lower(),
            n_bins=self._pd0.fixed_leaders[0].number_of_cells_wn,
            n_beams=self._pd0.fixed_leaders[0].number_of_beams,
            beam_angle=self._pd0.fixed_leaders[0].beam_angle,
            bin_1_distance=self._pd0.fixed_leaders[0].bin_1_distance / 100,
            bin_length=self._pd0.fixed_leaders[0].depth_cell_length_ws / 100,
            bin_midpoint_distances=None,
            beam_dr =float(get_valid(self._cfg, 'beam_dr', 0.1)),
            crp_offset_x=float(get_valid(self._cfg, 'crp_offset_x', 0)),
            crp_offset_y=float(get_valid(self._cfg, 'crp_offset_y', 0)),
            crp_offset_z=float(get_valid(self._cfg, 'crp_offset_z', 0)),
            crp_rotation_angle=float(get_valid(self._cfg, 'crp_rotation_angle',0)),
            relative_beam_origin = None,
            relative_beam_midpoint_positions=None,
            geographic_beam_midpoint_positions=None,
            HAB_beam_midpoint_distances = None,
        )

        self.geometry.bin_midpoint_distances=self._get_bin_midpoints()

        relative_org, relative_bmp, geographic_bmp = self._calculate_beam_geometry()
        self.geometry.relative_beam_midpoint_positions = relative_bmp
        self.geometry.geographic_beam_midpoint_positions = geographic_bmp
        self.geometry.relative_beam_origin  = relative_org  
        
        # Beam data (unmasked)
        @dataclass
        class ADCPBeamData:
            echo_intensity: np.ndarray = field(metadata={"desc": "Raw echo intensity from each beam. Unitless ADC counts representing backscatter strength."})
            correlation_magnitude: np.ndarray = field(metadata={"desc": "Correlation magnitude from each beam, used as a data quality metric."})
            percent_good: np.ndarray = field(metadata={"desc": "Percentage of good data for each beam and cell, based on instrument quality control logic."})
            absolute_backscatter: np.ndarray = field(default=None, metadata={"desc": "Calibrated absolute backscatter in dB, derived from raw echo intensity using beam-specific corrections."})
            signal_to_noise_ratio: np.ndarray = field(default=None, metadata={"desc": "SNR in dB, calculated as the difference between backscatter and instrument noise floor."})
            suspended_solids_concentration: np.ndarray = field(default=None, metadata={"desc": "Estimated suspended solids concentration (e.g., mg/L) derived from absolute backscatter using calibration coefficients."})
            sediment_attenuation: np.ndarray = field(default=None, metadata={"desc": "Estimated acoustic power attenuation due to suspended sediments in water (dB/km)"})

        self.beam_data = ADCPBeamData(
            echo_intensity=self._pd0.get_echo_intensity().astype(float),
            correlation_magnitude=self._pd0.get_correlation_magnitude().astype(float),
            percent_good=self._pd0.get_percent_good().astype(float),
            absolute_backscatter = None,  # placeholder until compute
            suspended_solids_concentration=None,  # placeholder until compute 
            signal_to_noise_ratio = None, # placeholder until compute
            sediment_attenuation = None,  # placeholder until compute
            )
        
        # Bottom Track data (unmasked)
        @dataclass
        class ADCPBottomTrack:
            eval_amp: np.ndarray = field(metadata={"desc": "Bottom-track evaluation amplitude for each beam (counts)"})
            correlation_magnitude: np.ndarray = field(metadata={"desc": "Bottom-track correlation magnitude for each beam (counts)"})
            percent_good: np.ndarray = field(metadata={"desc": "Bottom-track percent-good per beam (0–100%)"})
            range_to_seabed: np.ndarray = field(metadata={"desc": "Vertical range to seabed per beam (meters)"})
            adjusted_range_to_seabed: np.ndarray = field(metadata={"desc": "Vertical range to seabed per beam (meters), adjusted for beam angle and platform orientation"})
            seabed_points: np.ndarray = field(metadata={"desc": "Geographic location of all bottom track range measurements"})
            velocity: np.ndarray = field(metadata={"desc": "Bottom-track velocity vectors for each beam (m/s), in raw coordinate frame (set by EX_command)"})
            velocity_ship: np.ndarray = field(metadata={"desc": "Bottom-track velocity vectors for each beam (m/s), (F,B,Z,ev) in ship coordinate frame"})
            velocity_earth: np.ndarray = field(metadata={"desc": "Bottom-track velocity vectors for each beam (m/s), (E,N,U,ev) in earth coordinate frame"})
            ref_layer_velocity: np.ndarray = field(metadata={"desc": "Reference layer velocity for each beam (m/s)"})
            ref_correlation_magnitude: np.ndarray = field(metadata={"desc": "Correlation magnitude in reference layer (counts)"})
            ref_echo_intensity: np.ndarray = field(metadata={"desc": "Echo intensity in reference layer (counts)"})
            ref_percent_good: np.ndarray = field(metadata={"desc": "Percent-good in reference layer (0–100%)"})
            rssi_amp: np.ndarray = field(metadata={"desc": "Receiver Signal Strength Indicator amplitude in bottom echo (counts)"})
        
            # Configuration and metadata fields
            fid: int = field(metadata={"desc": "Bottom-track data ID (constant 0x0600)"})
            corr_mag_min_bc: int = field(metadata={"desc": "Minimum correlation magnitude (BC command)"})
            delay_before_reacquire_bd: int = field(metadata={"desc": "Ensembles to wait before reacquiring bottom (BD command)"})
            error_velocity_max_be: int = field(metadata={"desc": "Maximum error velocity (mm/s) (BE command)"})
            eval_amp_min_ba: int = field(metadata={"desc": "Minimum evaluation amplitude (BA command)"})
            max_depth_bx: int = field(metadata={"desc": "Maximum tracking depth (decimeters) (BX command)"})
            mode_bm: int = field(metadata={"desc": "Bottom-tracking mode (BM command)"})
            percent_good_min_bg: int = field(metadata={"desc": "Minimum percent-good required per ensemble (BG command)"})
            pings_per_ensemble_bp: int = field(metadata={"desc": "Bottom-track pings per ensemble (BP command)"})
            gain: int = field(metadata={"desc": "Gain level for shallow water bottom tracking"})
        
            # Reference layer bounds (BL command)
            ref_layer_far_bl: int = field(metadata={"desc": "Reference layer far boundary (dm)"})
            ref_layer_min_bl: int = field(metadata={"desc": "Reference layer minimum size (dm)"})
            ref_layer_near_bl: int = field(metadata={"desc": "Reference layer near boundary (dm)"})
               

        bt_list = self._pd0.get_bottom_track()
        if bt_list:
            self._bt_mode_active = True
            self.bottom_track = ADCPBottomTrack(
                eval_amp = np.array([[getattr(bt_list[e], f"beam{b}_eval_amp") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                correlation_magnitude = np.array([[getattr(bt_list[e], f"beam{b}_bt_corr") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                percent_good = np.array([[getattr(bt_list[e], f"beam{b}_bt_pgood") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                range_to_seabed = np.array([[getattr(bt_list[e], f"beam{b}_bt_range") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)], dtype = np.float64).T/100,
                adjusted_range_to_seabed =None,
                seabed_points = None,
                velocity = np.array([[getattr(bt_list[e], f"beam{b}_bt_vel") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)], dtype = np.float64).T,
                velocity_ship = None,
                velocity_earth = None,
                ref_layer_velocity = np.array([[getattr(bt_list[e], f"beam_{b}_ref_layer_vel") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)], dtype = np.float64).T,
                ref_correlation_magnitude = np.array([[getattr(bt_list[e], f"bm{b}_ref_corr") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                ref_echo_intensity = np.array([[getattr(bt_list[e], f"bm{b}_ref_int") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                ref_percent_good = np.array([[getattr(bt_list[e], f"bm{b}_ref_pgood") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                rssi_amp = np.array([[getattr(bt_list[e], f"bm{b}_rssi_amp") for b in range(1, self.geometry.n_beams+1)] for e in range(self.time.n_ensembles)]).T,
                fid = np.array([bt.bottom_track_id for bt in bt_list]),
                corr_mag_min_bc = np.array([bt.bt_corr_mag_min_bc for bt in bt_list]),
                delay_before_reacquire_bd = np.array([bt.bt_delay_before_reacquire_bd for bt in bt_list]),
                error_velocity_max_be = np.array([bt.bt_err_vel_max_be for bt in bt_list]),
                eval_amp_min_ba = np.array([bt.bt_eval_amp_min_ba for bt in bt_list]),
                max_depth_bx = np.array([bt.bt_max_depth_bx for bt in bt_list]),
                mode_bm = np.array([bt.bt_mode_bm for bt in bt_list]),
                percent_good_min_bg = np.array([bt.bt_percent_good_min_bg for bt in bt_list]),
                pings_per_ensemble_bp = np.array([bt.bt_pings_per_ensemble_bp for bt in bt_list]),
                gain = np.array([bt.gain for bt in bt_list]),
                ref_layer_far_bl = np.array([bt.ref_layer_far_bl for bt in bt_list]),
                ref_layer_min_bl = np.array([bt.ref_layer_min_bl for bt in bt_list]),
                ref_layer_near_bl = np.array([bt.ref_layer_near_bl for bt in bt_list]),
            )
        
            
            self.bottom_track.velocity_ship = self._get_bt_velocity(target_frame = 'ship')
            self.bottom_track.velocity_earth = self._get_bt_velocity(target_frame = 'earth')
            
            adjusted_depth, seabed_points = self._calculate_bottom_track_geometry()
            
            self.bottom_track.adjusted_range_to_seabed = adjusted_depth
            self.bottom_track.seabed_points = seabed_points
            self.geometry.HAB_beam_midpoint_distances = self._calculate_height_above_bed()
        else: 
            self._bt_mode_active = False
            
       
        @dataclass
        class BeamVel:
            b1: np.ndarray
            b2: np.ndarray
            b3: np.ndarray
            b4: np.ndarray
            units: str = field(default="m/s")
        
        @dataclass
        class InstVel:
            x: np.ndarray
            y: np.ndarray
            z: np.ndarray
            ev: np.ndarray
            speed: np.ndarray
            direction: np.ndarray
            units: str = field(default="m/s")
        
        @dataclass
        class ShipVel:
            s: np.ndarray
            f: np.ndarray
            u: np.ndarray
            ev: np.ndarray
            speed: np.ndarray
            direction: np.ndarray
            units: str = field(default="m/s")
        
        @dataclass
        class EarthVel:
            u: np.ndarray
            v: np.ndarray
            z: np.ndarray
            ev: np.ndarray
            speed: np.ndarray
            direction: np.ndarray
            units: str = field(default="m/s")
        
        @dataclass
        class Velocity:
            """
            Access patterns:
              self.velocity.from_beam.b1 .. b4
              self.velocity.from_instrument.x, y, z
              self.velocity.from_ship.S, F, U
              self.velocity.from_earth.u, v, z
              self.velocity.ev  # error velocity, if available
            """
            from_beam: Optional[BeamVel] = None
            from_instrument: Optional[InstVel] = None
            from_ship: Optional[ShipVel] = None
            from_earth: Optional[EarthVel] = None


        def _populate_velocity() -> None:
            """
            Populate self.velocity using native frame and forward transforms only.
            Uses class methods; no re-derivations.
            """
            frame = self._pd0.fixed_leaders[0].coordinate_transform.frame.lower()
        
            # Attitude and corrections (length T)
            heading_deg = self.aux_sensor_data.heading
            pitch_deg = self.aux_sensor_data.pitch
            roll_deg = self.aux_sensor_data.roll
            declination_deg = self.corrections.magnetic_declination
            heading_bias_deg = self.geometry.crp_rotation_angle
            use_tilts = True
        
            # Native profile velocities (T, K, 4): mm/s → m/s
            raw = self._pd0.get_velocity() / 1000.0
        
            # get raw bottom track velocities and subtract
            if self._bt_mode_active:
                raw_bt = self.bottom_track.velocity.T/1000
                raw = raw - raw_bt[:,None,:]
            # Reset container
            self.velocity = Velocity()
        
            if frame == "beam":
                # Beam
                b1, b2, b3, b4 = raw[..., 0], raw[..., 1], raw[..., 2], raw[..., 3]
                self.velocity.from_beam = BeamVel(b1, b2, b3, b4)
        
                # Instrument
                I4 = self._beam_to_inst_coords(raw)                 # (T,K,4)
                X, Y, Z, ev = I4[..., 0], I4[..., 1], I4[..., 2], I4[..., 3]
                speed = np.hypot(X,Y)
                direction = (np.degrees(np.arctan2(X, Y)) % 360.0)
                self.velocity.from_instrument = InstVel(X, Y, Z, ev, speed, direction)
        
                # Ship
                S3 = self._inst_to_ship_coords(I4[..., :3], pitch_deg, roll_deg, use_tilts)
                S, F, U = S3[..., 0], S3[..., 1], S3[..., 2]
                speed = np.hypot(S,F)
                direction = (np.degrees(np.arctan2(S, F)) % 360.0)
                self.velocity.from_ship = ShipVel(S, F, U, ev, speed, direction)
        
                # Earth
                E3 = self._inst_to_earth_coords(
                    I4[..., :3],
                    heading_deg,
                    pitch_deg,
                    roll_deg,
                    declination_deg,
                    heading_bias_deg,
                    use_tilts,
                )
                u, v, z = E3[..., 0], E3[..., 1], E3[..., 2]
                speed = np.hypot(u,v)
                direction = (np.degrees(np.arctan2(u, v)) % 360.0)
                self.velocity.from_earth = EarthVel(u, v, z, ev, speed,direction)
        
            elif frame == "instrument":
                # Instrument
                X, Y, Z, ev = raw[..., 0], raw[..., 1], raw[..., 2], raw[..., 3]
                speed = np.hypot(X,Y)
                direction = (np.degrees(np.arctan2(X, Y)) % 360.0)
                self.velocity.from_instrument = InstVel(X, Y, Z, ev, speed, direction)
        
                # Ship
                S3 = self._inst_to_ship_coords(raw[..., :3], pitch_deg, roll_deg, use_tilts)
                S, F, U = S3[..., 0], S3[..., 1], S3[..., 2]
                speed = np.hypot(S,F)
                direction = (np.degrees(np.arctan2(S, F)) % 360.0)
                self.velocity.from_ship = ShipVel(S, F, U, ev, speed, direction)
        
                # Earth
                E3 = self._inst_to_earth_coords(
                    raw[..., :3],
                    heading_deg,
                    pitch_deg,
                    roll_deg,
                    declination_deg,
                    heading_bias_deg,
                    use_tilts,
                )
                u, v, z = E3[..., 0], E3[..., 1], E3[..., 2]
                speed = np.hypot(u,v)
                direction = (np.degrees(np.arctan2(u, v)) % 360.0)
                self.velocity.from_earth = EarthVel(u, v, z, ev, speed,direction)
        
            elif frame == "ship":
                # Ship
                S, F, U, ev = raw[..., 0], raw[..., 1], raw[..., 2], raw[..., 3]
                speed = np.hypot(S,F)
                direction = (np.degrees(np.arctan2(S, F)) % 360.0)
                self.velocity.from_ship = ShipVel(S, F, U, ev, speed, direction)
        
                # Earth
                E4 = self._ship_to_earth_coords(raw, heading_deg)   # preserves err
                u, v, z, ev_e = E4[..., 0], E4[..., 1], E4[..., 2], E4[..., 3]
                speed = np.hypot(u,v)
                direction = (np.degrees(np.arctan2(u, v)) % 360.0)
                self.velocity.from_earth = EarthVel(u, v, z, ev, speed,direction)
        
            elif frame == "earth":
                # Earth
                u, v, z, ev = raw[..., 0], raw[..., 1], raw[..., 2], raw[..., 3]
                speed = np.hypot(u,v)
                direction = (np.degrees(np.arctan2(u, v)) % 360.0)
                self.velocity.from_earth = EarthVel(u, v, z, ev, speed,direction)
        
            else:
                raise ValueError(f"Unknown native frame '{frame}'")

        _populate_velocity()       
                 
        ## water properties class
        @dataclass
        class WaterProperties:
            density: NDArray[np.float64] = field(metadata={"desc": "Water density (kg/m³)."})
            salinity: NDArray[np.float64] = field(metadata={"desc": "Water salinity (PSU)."})
            temperature: NDArray[np.float64] = field(metadata={"desc": "Water temperature (°C)."})
            pH: NDArray[np.float64] = field(metadata={"desc": "Water pH (unitless)."})
            pressure: Optional[NDArray[np.float64]] = field(default=None, metadata={"desc": "Water pressure array (deci-bar, )"})
            
        # default typical Singapore coastal values:
        # Density: ~1023 kg/m³, Salinity: ~30 PSU, Temp: ~28°C, pH: ~8.1
        wp_cfg = self._cfg.get('water_properties', {}) # get water rproperties dictionary
        # approximate water pressure based on bin distances. 
        bin_distances = self.geometry.bin_midpoint_distances
        pressure = self.aux_sensor_data.pressure
        pressure = np.outer(pressure, np.ones(self.geometry.n_bins))
        if self.geometry.beam_facing.lower() == 'down':
            pressure += bin_distances * 0.981
        else:
            pressure -= bin_distances * 0.981
           
        # get sensor temperature

        temperature = np.array(get_valid(wp_cfg,'temperature', None))
        if not temperature:
            temperature = self.aux_sensor_data.temperature # if not manual entry, use sensor data
        else:
            temperature = temperature*np.ones(self.time.n_ensembles)# else cast input variable to correct dimension 
        temperature = np.outer(temperature, np.ones(self.geometry.n_bins)) # cast to correct dimensions                      

        self.water_properties = WaterProperties(
            density=np.array(get_valid(wp_cfg, 'density', [1023.0]), dtype=np.float64),
            salinity=np.array(get_valid(wp_cfg, 'salinity', [30.0]), dtype=np.float64),
            temperature=temperature,
            pressure=pressure,
            pH=np.array(get_valid(wp_cfg, 'pH', [8.1]), dtype=np.float64),
        )
        
        ## Sediment properties class
        @dataclass
        class SedimentProperties:
            particle_diameter: NDArray[np.float64] = field(metadata={"desc": "Median particle diameter (µm)."})
            particle_density: NDArray[np.float64] = field(metadata={"desc": "Particle density (kg/m³)."})
        
        # Default: 30 µm diameter (fine silt), 2650 kg/m³ (quartz)
        sed_cfg = self._cfg.get('sediment_properties', {})
        self.sediment_properties = SedimentProperties(
            particle_diameter=np.array(sed_cfg.get('particle_diameter', [30.0]), dtype=np.float64),
            particle_density=np.array(sed_cfg.get('particle_density', [2650.0]), dtype=np.float64),
        )   

        @dataclass
        class SSCParams:
            A: float = field(metadata={"desc": "Parameter A in SSC = A * 10^(B * ABS)"})
            B: float = field(metadata={"desc": "Parameter B in SSC = A * 10^(B * ABS)"})
        
        sscpar_cfg = self._cfg.get('ssc_params', {})
        
        self.ssc_params = SSCParams(
            A=get_valid(sscpar_cfg,'A', 0.05),
            B=get_valid(sscpar_cfg,'B', 5)
        )
                
        ## absolute backscatter params class
        abs_cfg = self._cfg.get('abs_params', {})
        @dataclass
        class AbsoluteBackscatterParams:
            """Parameters used in calculating absolute backscatter from echo intensity."""
            E_r: float = field(default=39.0, metadata={"desc": "Noise floor (counts)"})
            C: float = field(default=None, metadata={"desc": "System-specific calibration constant (dB)"})
            alpha_s: Optional[NDArray[np.float64]] = field(default=None, metadata={"desc": "Sediment Attenuation coefficient array (dB/m)"})
            alpha_w: Optional[NDArray[np.float64]] = field(default=None, metadata={"desc": "Water Attenuation coefficient array (dB/m)"})
            P_dbw: float = field(default=None, metadata={"desc": "Transmit power (dBW)"})
            WB: float =  field(default=None, metadata={"desc": "System Bandwidth (dBW)"}) 
            rssi: Dict[int, float] = field(default_factory=lambda: {1: 0.41, 2: 0.41, 3: 0.41, 4: 0.41},metadata={"desc": "RSSI scaling factors (counts to decibals) per beam"}),
            frequency: float = field(default=None, metadata={"desc": "System frequency"})
            tx_pulse_length: float = field(default=None, metadata={"desc": "Transmit pule length (m)"})
            
        # set default Absolute Backscatter params 
        n_beams = self.geometry.n_beams
        n_bins = self.geometry.n_bins
        n_ens = self.time.n_ensembles
        
        # Determine system-specific default C based on bandwidth
        bandwidth = self._pd0.fixed_leaders[0].system_bandwidth_wb
        C = -139.09 if bandwidth == 0 else -149.14
    
        # set default sediment attenuation coefficient  (all zeros)
        alpha_s = np.zeros((n_ens,n_bins,n_beams), dtype = float)
        
        # compute water attenuation coefficient
        pulse_lengths = self._pd0.get_fixed_leader_attr('xmit_pulse_length_based_on_wt')*.01#_get_sensor_transmit_pulse_length()
        bin_depths = abs(self.geometry.geographic_beam_midpoint_positions.z)
        freq = self._pd0.fixed_leaders[0].system_configuration.frequency
        freq = float(freq.split('-')[0])
        
        temperature = self.water_properties.temperature
        
        salinity = self.water_properties.salinity
        density = self.water_properties.density
        pH = self.water_properties.pH
        water_density = density * np.ones((n_ens, n_bins, n_beams))
        bin_distances = np.outer(bin_distances, np.ones(n_ens)).T
        alpha_w = self._water_absorption_coeff(
                          T = self.water_properties.temperature,
                          S = self.water_properties.salinity,
                          z = pressure, 
                          f = freq, 
                          pH = pH)
        
        # Default P_dbw based on frequency
        freq_defaults = {
            75:  27.3,
            300: 14.0,
            600:  9.0}
        
        P_dbw = freq_defaults.get(freq, 9)
        
        # Override with config if provided
        C = abs_cfg.get("C", C)
        P_dbw = abs_cfg.get("P_dbw", P_dbw)
        E_r = abs_cfg.get("E_r", 39.0)
    
        # Beam-specific RSSI from rssi dataclass
        rssi ={1:float(get_valid(abs_cfg,'rssi_beam1', 0.41)),
               2:float(get_valid(abs_cfg,'rssi_beam2', 0.41)),
               3:float(get_valid(abs_cfg,'rssi_beam3', 0.41)),
               4:float(get_valid(abs_cfg,'rssi_beam4', 0.41))}
        
        self.abs_params = AbsoluteBackscatterParams(
                            E_r=E_r,
                            C=C,
                            alpha_s = alpha_s,
                            alpha_w = alpha_w,
                            P_dbw=P_dbw,
                            rssi=rssi,
                            frequency = freq,
                            tx_pulse_length = pulse_lengths,
                            WB = bandwidth)
        
        #calculate absolute backscatter
        ABS,StN = self._calculate_absolute_backscatter()
        self.beam_data.absolute_backscatter = ABS
        self.beam_data.signal_to_noise_ratio = StN
        
        ## masking attributres class
        @dataclass
        class MaskParams:
            pg_min: float = field(metadata={"desc": "Minimum 'percent good' threshold below which data is masked. Reflects the combined percentage of viable 3 and 4 beam velocity solutions PG1 + PG3. Applies to masks for velocity data only."})
            cormag_min: int = field(metadata={"desc": "Minimum correlation magnitude accepted. Applies to masks for beam data only."})
            cormag_max: int = field(metadata={"desc": "Maximum correlation magnitude accepted. Applies to masks for beam data only."})
            echo_min: int = field(metadata={"desc": "Minimum echo intensity threshold accepted. Applies to masks for beam data only."})
            echo_max: int = field(metadata={"desc": "Maximum echo intensity threshold accepted. Applies to masks for beam data only."})
            abs_min: int = field(metadata={"desc": "Minimum absolute backscatter intensity threshold accepted. Applies to masks for beam data only."})
            abs_max: int = field(metadata={"desc": "Maximum absolute backscatter intensity threshold accepted. Applies to masks for beam data only."})
            vel_min: float = field(metadata={"desc": "Minimum accepted velocity magnitude (m/s). Applies to masks for velocity data only."})
            vel_max: float = field(metadata={"desc": "Maximum accepted velocity magnitude (m/s). Applies to masks for velocity data only."})
            bt_bin_offset: int = field(metadata={"desc": "Number of additional cells to mask above bottom track range to seabed mask."})
            err_vel_max: Union[float,str] = field(metadata={"desc": "Maximum accepted absolute value of error velocity (m/s).If 'auto' then. Applies to masks for velocity data only." })
            start_datetime: datetime = field(metadata={"desc": "Start time for valid ensemble masking window. Applies to masks for velocity and beam data."})
            end_datetime: datetime = field(metadata={"desc": "End time for valid ensemble masking window. Applies to masks for velocity and beam data."})
            first_good_ensemble: int = field(metadata={"desc": "Index of first ensemble to retain. Zero based index. Applies to masks for velocity and beam data."})
            last_good_ensemble: int = field(metadata={"desc": "Index of last ensemble to retain. Zero based index. Applies to masks for velocity and beam data."})
            beam_data_mask: NDArray[np.float64] = field(metadata={"desc": "(calculated) Boolean array (n_ens,n_bin,n_beam) contaning composite mask for all beam data variables"})
            velocity_data_mask: NDArray[np.float64] = field(metadata={"desc": "(calculated) Boolean array (n_ens,n_bin) contaning composite mask for all velocity data variables"})
                
            
        self.masking = MaskParams(
            pg_min=float(get_valid(self._cfg, 'pg_min', 0)),
            cormag_min=int(get_valid(self._cfg, 'cormag_min', 0)),
            cormag_max=int(get_valid(self._cfg, 'cormag_max', 255)),
            echo_min=int(get_valid(self._cfg, 'echo_min', 0)),
            echo_max=int(get_valid(self._cfg, 'echo_max', 255)),
            abs_min=int(get_valid(self._cfg, 'abs_min', Constants._LOW_NUMBER)),
            abs_max=int(get_valid(self._cfg, 'abs_max', 0)),
            vel_min=float(get_valid(self._cfg, 'vel_min', Constants._LOW_NUMBER)),
            vel_max=float(get_valid(self._cfg, 'vel_max', Constants._HIGH_NUMBER)),
            bt_bin_offset = int(get_valid(self._cfg, 'bt_bin_offset', 0)),
            err_vel_max = (lambda v: "auto" if isinstance(v, str) and v.lower() == "auto"
               else float(v) if isinstance(v, (int, float)) or (isinstance(v, str) and v.replace('.', '', 1).isdigit())
               else (_ for _ in ()).throw(ValueError(f"Invalid err_vel_max: {v!r}"))
              )(self._cfg.get('err_vel_max', 'auto')),
            start_datetime=parser.parse(get_valid(self._cfg, 'start_datetime', Constants._FAR_PAST_DATETIME)),
            end_datetime=parser.parse(get_valid(self._cfg, 'end_datetime', Constants._FAR_FUTURE_DATETIME)),
            first_good_ensemble=int(get_valid(self._cfg, 'first_good_ensemble', 1)),
            last_good_ensemble=int(get_valid(self._cfg, 'last_good_ensemble', self.time.n_ensembles +1)),
            beam_data_mask=None,
            velocity_data_mask=None,
        )

        
        self._generate_velocity_data_masks()
        self._generate_beam_data_masks()
        self.beam_data.suspended_solids_concentration = self._calculate_ssc()
        
    def _get_bin_midpoints(self) -> np.ndarray:
        """Compute distances from the transducer to bin centers.

        The distances are computed along the beam from the transducer
        to the center of each depth cell, based on the distance to the
        first bin and the bin length.

        Returns:
            np.ndarray: One-dimensional array of bin midpoint distances
            in meters with shape ``(n_bins,)``.
        """
        beam_length = self.geometry.n_bins * self.geometry.bin_length
        bin_midpoints = np.linspace(
            self.geometry.bin_1_distance,
            beam_length + self.geometry.bin_1_distance,
            self.geometry.n_bins
        )
        return bin_midpoints 

    def get_beam_data(self, field_name: str, mask: bool = True) -> np.ndarray:
        """Return a beam-space variable, optionally masked.

        Args:
            field_name (str): Name of the beam data field to retrieve.
                Valid values are:
                ``'echo_intensity'``, ``'correlation_magnitude'``,
                ``'percent_good'``, ``'absolute_backscatter'``,
                ``'signal_to_noise_ratio'``,
                ``'suspended_solids_concentration'``,
                ``'sediment_attenuation'``.
            mask (bool, optional): If True, applies
                ``self.masking.beam_data_mask`` and sets masked values
                to ``np.nan``. If False, returns the raw unmasked data.
                Defaults to True.

        Returns:
            np.ndarray: Beam data array with shape
            ``(n_ensembles, n_bins, n_beams)``.

        Raises:
            ValueError: If ``field_name`` is not one of the supported
                beam data fields.
        """
        field_name = field_name.lower().strip()
    
        # Validate field name
        valid_fields = ['echo_intensity', 'correlation_magnitude', 'percent_good',
                        'absolute_backscatter', 'signal_to_noise_ratio',
                        'suspended_solids_concentration', 'sediment_attenuation']
        if field_name not in valid_fields:
            raise ValueError(f"Invalid field name '{field_name}'. Must be one of: {valid_fields}")
    
        data = getattr(self.beam_data, field_name)
       
        if mask:
            data[self.masking.beam_data_mask] = np.nan
        
        return data
    
    def get_beam_series(self, field_name: str, mode: str, target: Union[int, float, str], beam: Union[str, int, list[int]]="mean"):
        """Extract a time series from beam-space data using bin selection
        or aggregation rules.

        The method operates on ``self.get_beam_data(field_name, mask=True)``
        and either:
        - selects a single bin per beam using a numeric target, or
        - aggregates over all bins (and optionally beams) using a
          string target (e.g. ``"mean"`` or ``"p90"``).

        Args:
            field_name (str): Beam field name passed to
                :meth:`get_beam_data`, for example
                ``'echo_intensity'`` or ``'absolute_backscatter'``.
            mode (str): Selection mode when ``target`` is numeric. One
                of:
                * ``'bin'``: select a fixed 1-based bin index.
                * ``'range'``: select the bin whose along-beam distance
                  (m) is closest to ``target`` using
                  ``self.geometry.bin_midpoint_distances``.
                * ``'hab'``: select, per ensemble and beam, the bin
                  whose height above bed (m) is closest to ``target``
                  using ``self.geometry.HAB_beam_midpoint_distances``.
            target (int | float | str): Selector or aggregation
                instruction.
                - If numeric (int/float) and ``mode`` is ``'bin'``,
                  ``'range'``, or ``'hab'``, it is interpreted as the
                  target bin index, range (m), or HAB (m).
                - If a string, it applies an aggregation across all bins
                  for the selected beams:
                  * ``'mean'`` or ``'avg'``: mean over bins × beams.
                  * ``'pXX'``: percentile (0–100) over bins × beams,
                    e.g. ``'p50'``, ``'p90'``.
            beam (str | int | list[int], optional): Beam selection
                (1-based indices). If ``'mean'`` or ``'avg'``, all beams
                are included. If an integer or list of integers, only
                those beams are used. Defaults to ``'mean'``.

        Returns:
            tuple[np.ndarray, dict]:
                - ``out``: One-dimensional array with shape
                  ``(n_ensembles,)`` containing the selected or
                  aggregated values.
                - ``meta``: Dictionary with diagnostics, including:
                    * ``'mode'`` (str): ``'bin'``, ``'range'``,
                      ``'hab'``, or ``'aggregate'``.
                    * ``'beam_mask'`` (np.ndarray): Boolean beam
                      mask with shape ``(n_beams,)``.
                    * For ``mode='bin'``/``'range'``:
                      ``'bin_index'`` (int), and for ``'range'``,
                      ``'depth_m'`` (float).
                    * For ``mode='hab'``:
                      per-beam bin indices/HAB arrays and ensemble
                      mean HAB.
                    * For aggregation targets:
                      ``'aggregation'`` (e.g. ``'mean'``, ``'p90'``).

        Raises:
            ValueError: If ``field_name``, ``mode``, or string
                ``target`` is invalid, or if a numeric bin/range/HAB
                index is out of range.
            TypeError: If ``target`` is a sequence instead of a single
                numeric value or aggregation string.
        """
    
        data = self.get_beam_data(field_name, mask=True)  # (ne, nb, nm)
        ne, nb, nm = data.shape
    
        # Beam mask
        if isinstance(beam, str) and beam.lower() in {"mean", "avg"}:
            beam_mask = np.ones(nm, dtype=bool)
        else:
            sel = [beam] if isinstance(beam, (int, np.integer)) else list(beam)
            idx = [int(b) - 1 for b in sel if 1 <= int(b) <= nm]
            beam_mask = np.zeros(nm, dtype=bool)
            beam_mask[idx] = True
        beam_mask3 = beam_mask[None, None, :]  # (1,1,nm)
    
        # Aggregation target?
        if isinstance(target, str):
            t = target.strip().lower()
            meta = {"mode": "aggregate", "beam_mask": beam_mask.copy()}
            vals = np.where(beam_mask3, data, np.nan)  # all bins for selected beams
    
            if t in {"mean", "avg"}:
                meta["aggregation"] = "mean"
                out = np.nanmean(vals, axis=(1, 2))
            elif t.startswith("p") and t[1:].replace(".", "", 1).isdigit():
                q = float(t[1:])
                if not (0.0 <= q <= 100.0):
                    raise ValueError("percentile must be between 0 and 100.")
                meta["aggregation"] = f"p{q:g}"
                out = np.nanpercentile(vals, q, axis=(1, 2), method="nearest")
            else:
                raise ValueError("string target must be 'mean'/'avg' or 'pXX' like 'p50'.")
    
            empty = ~np.any(np.isfinite(vals), axis=(1, 2))
            out[empty] = np.nan
            return out, meta
    
        # Numeric selector path
        if isinstance(target, (tuple, list, np.ndarray)):
            raise TypeError("target must be a single int/float or an aggregation string.")
        mode = mode.lower().strip()
        meta = {"mode": mode, "beam_mask": beam_mask.copy()}
    
        if mode == "bin":
            b = int(target)
            if b < 1 or b > nb:
                raise ValueError(f"bin target {b} out of range 1..{nb}")
            bin_mask = np.zeros(nb, dtype=bool); bin_mask[b - 1] = True
            sel_bins = np.broadcast_to(bin_mask[None, :, None], (ne, nb, nm))
            sel_mask = sel_bins & np.broadcast_to(beam_mask3, (ne, nb, nm))
            meta["bin_index"] = int(b)
    
        elif mode == "range":
            r_bins = np.asarray(self.geometry.bin_midpoint_distances, float)  # (nb,)
            tgt = float(target)
            b_idx = int(np.nanargmin(np.abs(r_bins - tgt)))  # 0-based
            bin_mask = np.zeros(nb, dtype=bool); bin_mask[b_idx] = True
            sel_bins = np.broadcast_to(bin_mask[None, :, None], (ne, nb, nm))
            sel_mask = sel_bins & np.broadcast_to(beam_mask3, (ne, nb, nm))
            meta["bin_index"] = int(b_idx + 1)
            meta["depth_m"] = float(r_bins[b_idx])
    
        elif mode == "hab":
            hab = np.asarray(self.geometry.HAB_beam_midpoint_distances, float)  # (ne, nb, nm)
            tgt = float(target)
            sel_mask = np.zeros((ne, nb, nm), dtype=bool)
            bin_idx_pb = np.full((ne, nm), np.nan)
            hab_pb = np.full((ne, nm), np.nan)
    
            for m in range(nm):
                if not beam_mask[m]:
                    continue
                hb = hab[:, :, m]  # (ne, nb)
                finite = np.isfinite(hb)
                hb_fill = np.where(finite, hb, np.inf)
                idx_min = np.argmin(np.abs(hb_fill - tgt), axis=1)  # (ne,)
                rows = np.arange(ne)
                sel_mask[rows, idx_min, m] = True
                bin_idx_pb[:, m] = idx_min + 1
                hab_pb[:, m] = hb[rows, idx_min]
    
            meta["bin_index_per_beam"] = bin_idx_pb
            meta["hab_m_per_beam"] = hab_pb
            with np.errstate(invalid="ignore"):
                meta["hab_m"] = np.nanmean(np.where(beam_mask[None, :], hab_pb, np.nan), axis=1)
    
        else:
            raise ValueError("mode must be one of {'bin','range','hab'} for numeric targets.")
    
        vals = np.where(sel_mask, data, np.nan)
        out = np.nanmean(vals, axis=(1, 2))  # single-bin per beam → mean across selected beams
        empty = ~np.any(np.isfinite(vals), axis=(1, 2))
        out[empty] = np.nan
        return out, meta

    def get_velocity_data(self, coord_sys: str = "earth", mask: bool = True,):
        """Return velocity data in a chosen coordinate system.

        Velocities are drawn from ``self.velocity`` (which is populated
        at initialization) and optionally masked and smoothed using a
        centered rolling average in ensemble space.

        Args:
            coord_sys (str, optional): Target coordinate system. One of
                ``'instrument'``, ``'ship'``, or ``'earth'``. Defaults
                to ``'earth'``.
            mask (bool, optional): If True, applies
                ``self.masking.velocity_data_mask`` before computing
                speed and direction. Defaults to True.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                A 6-tuple of arrays with shape ``(n_ensembles, n_bins)``:
                - ``v1``: First component (X / S / U, depending on
                  ``coord_sys``).
                - ``v2``: Second component (Y / F / V).
                - ``v3``: Third component (Z / U / W).
                - ``ev``: Error velocity (always defined in earth
                  frame).
                - ``speed``: Horizontal speed magnitude,
                  ``sqrt(v1**2 + v2**2)``.
                - ``direction``: Azimuthal direction in degrees
                  (0–360), defined such that 0° is along +v2 and angles
                  increase clockwise toward +v1.

        Raises:
            ValueError: If ``coord_sys`` is not one of
                ``{'instrument', 'ship', 'earth'}``.
        """
        def _nanmean_centered(a: np.ndarray, win: int) -> np.ndarray:
            if win is None or win <= 1:
                return a
            if a.ndim == 1:
                a = a[:, None]
            left = (win - 1) // 2
            right = win - 1 - left
            w = sliding_window_view(a, window_shape=(win,), axis=0)  # (T-win+1, ..., win)
            m = np.nanmean(w, axis= -1)                              # (T-win+1, ...)
            pad = [(left, right)] + [(0, 0)] * (m.ndim - 1)
            out = np.pad(m, pad_width=pad, mode="constant", constant_values=np.nan)
            return out.squeeze()
    
        coord_sys = coord_sys.lower().strip()
        valid_fields = ["instrument", "ship", "earth"]
        if coord_sys not in valid_fields:
            raise ValueError(f"Invalid coordinate system '{coord_sys}'. Must be one of: {valid_fields}")
            
        averaging_window = self.corrections.velocity_average_window_len
    
        ev = self.velocity.from_earth.ev  # error velocity is defined in earth frame
    
        if coord_sys == "instrument":
            src = self.velocity.from_instrument
            v1, v2, v3 = np.array(src.x, float), np.array(src.y, float), np.array(src.z, float)
        elif coord_sys == "ship":
            src = self.velocity.from_ship
            v1, v2, v3 = np.array(src.s, float), np.array(src.f, float), np.array(src.u, float)
        else:  # earth
            src = self.velocity.from_earth
            v1, v2, v3 = np.array(src.u, float), np.array(src.v, float), np.array(src.z, float)
    
        # Mask first
        if mask:
            m = self.masking.velocity_data_mask  # shape matches (time, bins)
            for arr in (v1, v2, v3, ev):
                arr[m] = np.nan
    
        # Rolling average on v1,v2,v3
        if averaging_window and averaging_window > 1:
            v1 = _nanmean_centered(v1, averaging_window)
            v2 = _nanmean_centered(v2, averaging_window)
            v3 = _nanmean_centered(v3, averaging_window)
    
        # Recompute speed and azimuth from averaged v1,v2
        speed = np.hypot(v1, v2)
        # Azimuth: 0 = toward +v2 axis, increases clockwise toward +v1 axis.
        direction = (np.degrees(np.arctan2(v1, v2)) + 360.0) % 360.0
    
        return v1, v2, v3, ev, speed, direction

    def get_velocity_series(self, component: str, mode: str, target: Union[int, float, str]):
        """Extract a time series from earth-frame velocities.

        This method uses :meth:`get_velocity_data` with
        ``coord_sys='earth'`` and then either:
        - selects a single bin per ensemble using a numeric target, or
        - aggregates over all bins using a string target (e.g.
          ``'mean'`` or ``'p90'``).

        Args:
            component (str): Velocity quantity to extract. One of:
                * ``'u'``: first horizontal component (eastward).
                * ``'v'``: second horizontal component (northward).
                * ``'w'``: vertical component.
                * ``'ev'``: error velocity.
                * ``'speed'``: horizontal speed magnitude.
                * ``'direction'``: flow direction in degrees (0–360).
            mode (str): Selection mode when ``target`` is numeric. One
                of:
                * ``'bin'``: select a fixed 1-based bin index.
                * ``'range'``: select the bin whose range (m) is
                  closest to ``target``. Uses either
                  ``geometry.bin_midpoint_distances`` or
                  ``geometry.range_bin_midpoints``.
                * ``'hab'``: select, per ensemble, the bin whose
                  height above bed (m) is closest to ``target``. Uses
                  either ``geometry.HAB_cell_midpoint_distances`` or
                  ``geometry.hab_bin_midpoints``.
            target (int | float | str): Selector or aggregation
                instruction.
                - Numeric (int/float): used with ``mode`` as bin index,
                  range (m), or HAB (m).
                - String: aggregation over all bins:
                  * ``'mean'`` or ``'avg'``: mean across bins. For
                    ``'direction'`` a circular mean is used.
                  * ``'pXX'``: percentile (0–100) across bins, e.g.
                    ``'p50'``, ``'p90'``. Not allowed for
                    ``'direction'``.

        Returns:
            tuple[np.ndarray, dict]:
                - ``out``: One-dimensional array of shape
                  ``(n_ensembles,)`` containing the selected or
                  aggregated values.
                - ``meta``: Dictionary of diagnostics, including:
                    * ``'component'`` (str): requested component.
                    * ``'mode'`` (str): ``'bin'``, ``'range'``,
                      ``'hab'``, or ``'aggregate'``.
                    * For numeric selection: bin indices and selected
                      range/HAB values.
                    * For aggregation: ``'aggregation'`` and whether a
                      circular mean was used (``'circular'``).

        Raises:
            ValueError: If ``component``, ``mode``, the distance/HAB
                geometry arrays, or a string ``target`` are invalid.
            TypeError: If ``target`` is a sequence instead of a single
                numeric value or aggregation string.
        """
    
        # ---------- fetch earth-frame velocity products ----------
        v1, v2, v3, ev, speed, direction = self.get_velocity_data(
            coord_sys="earth", mask=True
        )  # each (ne, nb)
        ne, nb = v1.shape
    
        comp = component.strip().lower()
        if comp == "u":
            data = np.asarray(v1, dtype=float)
        elif comp == "v":
            data = np.asarray(v2, dtype=float)
        elif comp == "w":
            data = np.asarray(v3, dtype=float)
        elif comp == "ev":
            data = np.asarray(ev, dtype=float)
        elif comp == "speed":
            data = np.asarray(speed, dtype=float)
        elif comp == "direction":
            data = np.asarray(direction, dtype=float)
        else:
            raise ValueError("component must be one of {'u','v','w','ev','speed','direction'}.")
    
        # ---------- aggregation path (target is a string) ----------
        if isinstance(target, str):
            t = target.strip().lower()
            meta = {"mode": "aggregate", "component": comp}
    
            if t in {"mean", "avg"}:
                meta["aggregation"] = "mean"
                if comp == "direction":
                    # circular mean in degrees
                    rad = np.deg2rad(data)
                    c = np.nanmean(np.cos(rad), axis=1)
                    s = np.nanmean(np.sin(rad), axis=1)
                    ang = np.rad2deg(np.arctan2(s, c)) % 360.0
                    out = ang
                    meta["circular"] = True
                else:
                    out = np.nanmean(data, axis=1)
                    meta["circular"] = False
    
            elif t.startswith("p") and t[1:].replace(".", "", 1).isdigit():
                if comp == "direction":
                    raise ValueError("Percentiles for 'direction' are undefined. Use 'mean' instead.")
                q = float(t[1:])
                if not (0.0 <= q <= 100.0):
                    raise ValueError("percentile must be between 0 and 100.")
                meta["aggregation"] = f"p{q:g}"
                meta["circular"] = False
                out = np.nanpercentile(data, q, axis=1, method="nearest")
            else:
                raise ValueError("string target must be 'mean'/'avg' or 'pXX' like 'p50'.")
    
            # ensembles with all-NaN across bins
            empty = ~np.any(np.isfinite(data), axis=1)
            out = np.asarray(out, dtype=float)
            out[empty] = np.nan
            return out, meta
    
        # ---------- numeric selector path (single bin per ensemble or fixed bin) ----------
        if isinstance(target, (tuple, list, np.ndarray)):
            raise TypeError("target must be a single int/float or an aggregation string.")
    
        mode = mode.lower().strip()
        meta = {"mode": mode, "component": comp}
    
        if mode == "bin":
            b = int(target)
            if b < 1 or b > nb:
                raise ValueError(f"bin target {b} out of range 1..{nb}")
            meta["bin_index"] = int(b)
            out = data[:, b - 1]
    
        elif mode == "range":
            # try common attribute names for per-bin range distances
            rng = None
            src_name = None
            for cand in (
                "bin_midpoint_distances",
                "range_bin_midpoints",
            ):
                if hasattr(self.geometry, cand):
                    rng = np.asarray(getattr(self.geometry, cand), dtype=float)
                    src_name = cand
                    break
            if rng is None:
                raise ValueError(
                    "Provide a 1D per-bin distance array on self.geometry, e.g., "
                    "'bin_midpoint_distances' or 'range_bin_midpoints' (shape (nb,))."
                )
            if rng.shape[0] != nb:
                raise ValueError(f"Distance array '{src_name}' must have length nb={nb}.")
    
            tgt = float(target)
            b_idx0 = int(np.nanargmin(np.abs(rng - tgt)))  # 0-based
            meta["bin_index"] = int(b_idx0 + 1)
            meta["range_m"] = float(rng[b_idx0])
            out = data[:, b_idx0]
    
        elif mode == "hab":
            # try common attribute names for per-ensemble per-bin HAB distances
            hab = None
            src_name = None
            for cand in (
                "HAB_cell_midpoint_distances",
                "hab_bin_midpoints",
            ):
                if hasattr(self.geometry, cand):
                    hab = np.asarray(getattr(self.geometry, cand), dtype=float)
                    src_name = cand
                    break
            if hab is None:
                raise ValueError(
                    "Provide a 2D HAB array on self.geometry, e.g., "
                    "'HAB_cell_midpoint_distances' or 'hab_bin_midpoints' (shape (ne, nb))."
                )
            if hab.shape != (ne, nb):
                raise ValueError(f"HAB array '{src_name}' must have shape (ne, nb)=({ne}, {nb}).")
    
            tgt = float(target)
            sel_idx = np.full(ne, np.nan)
            sel_hab = np.full(ne, np.nan)
    
            finite = np.isfinite(hab)
            # Replace NaN with +inf so argmin ignores them
            hab_fill = np.where(finite, hab, np.inf)
            idx_min = np.argmin(np.abs(hab_fill - tgt), axis=1)  # (ne,)
            rows = np.arange(ne)
            sel_idx[:] = idx_min + 1
            sel_hab[:] = hab[rows, idx_min]
    
            meta["bin_index_per_ens"] = sel_idx
            meta["hab_m_per_ens"] = sel_hab
            meta["hab_note"] = f"selected using geometry.{src_name}"
    
            out = data[rows, idx_min]
    
        else:
            raise ValueError("mode must be one of {'bin','range','hab'} for numeric targets.")
    
        # set NaN where selection is invalid
        out = np.asarray(out, dtype=float)
        out[~np.isfinite(out)] = np.nan
        return out, meta

    def _generate_velocity_data_masks(self) ->None:
        """Build the composite mask for velocity-related variables.

        This method combines several criteria into
        ``self.masking.velocity_data_mask``, including:

        * speed thresholds (``vel_min``/``vel_max``),
        * percent-good limits (using beams 1 and 4),
        * error-velocity filtering (either user-specified or
          automatically derived using an IQR-based rule),
        * ensemble index limits (``first_good_ensemble`` /
          ``last_good_ensemble``),
        * datetime limits (``start_datetime`` / ``end_datetime``),
        * and, if bottom track is active, a bottom-track-based mask
          with an optional cell offset.

        The result is a boolean array with shape
        ``(n_ensembles, n_bins)`` where True indicates masked (invalid)
        data.
        """
        # speed
        speed = self.velocity.from_earth.speed
        speed_mask = (speed > self.masking.vel_max) | (speed < self.masking.vel_min)
        
        # percent good
        pg = self.beam_data.percent_good
        pg = pg[:,:,0] + pg[:,:,3] 
        pg_mask =  (pg < self.masking.pg_min)
    
        # error velocity
        
        if self.masking.err_vel_max == 'auto':
            ev = self.velocity.from_earth.ev
 
            err_vel_max = 0.5
            k = 3
            # mask based on IQR
            q1 = np.nanpercentile(ev, 25)
            q3 = np.nanpercentile(ev, 75)
            iqr = q3 - q1
            lo = q1 - k * iqr
            hi = q3 + k * iqr
            ev_mask = (ev < lo) | (ev > hi) | (np.abs(ev)>err_vel_max)
            
        else: # mask based on input value
            ev = abs(self.velocity.from_earth.ev)
            ev_mask = (ev > self.masking.err_vel_max) | (ev < self.masking.err_vel_min)
            

        # first/last good ensemble 
        ens = np.arange(start = 1, stop = self.time.n_ensembles + 1)
        ens_mask = (ens > self.masking.last_good_ensemble) | (ens < self.masking.first_good_ensemble)
        ens_mask = ens_mask[:, np.newaxis]
        ens_mask = np.broadcast_to(ens_mask, (self.time.n_ensembles, self.geometry.n_bins))

        #start/end dates 
        dt = self.time.ensemble_datetimes
        dt_mask = (dt > self.masking.end_datetime) | (dt < self.masking.start_datetime)
        dt_mask = dt_mask[:, np.newaxis]
        dt_mask = np.broadcast_to(dt_mask, (self.time.n_ensembles, self.geometry.n_bins))
        # consolidated summary at the bottom
        total = speed_mask.size
        if self._bt_mode_active:
            bt_mask = self._generate_bottom_track_mask(cell_offset = self.masking.bt_bin_offset)[:,:,0]
            master_mask = np.logical_or.reduce([speed_mask, ev_mask,pg_mask, ens_mask, dt_mask, ~bt_mask])
        else: 
            master_mask = np.logical_or.reduce([speed_mask, ev_mask,pg_mask, ens_mask, dt_mask])
        self.masking.velocity_data_mask = master_mask
                       
    def _generate_beam_data_masks(self) -> None:
        """Build the composite mask for beam-space variables.

        This method combines several criteria into
        ``self.masking.beam_data_mask``, including:

        * correlation magnitude thresholds
          (``cormag_min``/``cormag_max``),
        * echo intensity thresholds (``echo_min``/``echo_max``),
        * absolute backscatter thresholds (``abs_min``/``abs_max``),
        * ensemble index limits (``first_good_ensemble`` /
          ``last_good_ensemble``),
        * datetime limits (``start_datetime`` / ``end_datetime``),
        * and, if bottom track is active, a bottom-track-based mask
          with an optional cell offset.

        The result is a boolean array with shape
        ``(n_ensembles, n_bins, n_beams)`` where True indicates masked
        (invalid) data.
        """
        # correlation magnitude
        cmag = self.beam_data.correlation_magnitude
        cmag_mask = (cmag > self.masking.cormag_max) | (cmag < self.masking.cormag_min)
        
        # echo intensity
        echo = self.beam_data.echo_intensity
        echo_mask = (echo > self.masking.echo_max) | (echo < self.masking.echo_min)
        
        # absolute backscatter
        sv = self.beam_data.absolute_backscatter
        sv_mask = (sv > self.masking.abs_max) | (sv < self.masking.abs_min)
        
        # first/last good ensemble 
        ens = np.arange(start = 1, stop = self.time.n_ensembles + 1)
        ens_mask = (ens > self.masking.last_good_ensemble) | (ens < self.masking.first_good_ensemble)
        ens_mask = ens_mask[:, np.newaxis, np.newaxis]
        ens_mask = np.broadcast_to(ens_mask, (self.time.n_ensembles, self.geometry.n_bins, self.geometry.n_beams))

        #start/end dates 
        dt = self.time.ensemble_datetimes
        dt_mask = (dt > self.masking.end_datetime) | (dt < self.masking.start_datetime)
        dt_mask = dt_mask[:, np.newaxis, np.newaxis]
        dt_mask = np.broadcast_to(dt_mask, (self.time.n_ensembles, self.geometry.n_bins, self.geometry.n_beams))

        if self._bt_mode_active:
            bt_mask = self._generate_bottom_track_mask(cell_offset = self.masking.bt_bin_offset)
            master_mask = np.logical_or.reduce([cmag_mask, echo_mask, sv_mask, ens_mask, dt_mask, ~bt_mask])
        else:
           master_mask = np.logical_or.reduce([cmag_mask, echo_mask, sv_mask, ens_mask, dt_mask])

        self.masking.beam_data_mask = master_mask
        
    def _generate_bottom_track_mask(self, cell_offset: int = 0, incl_sidelobe = True) -> None:
        """Create a mask indicating cells above the seabed based on
        bottom-track ranges.

        The bottom-track range for each beam/ensemble is compared to the
        along-beam bin-center distances, optionally adjusted for
        sidelobe interference and a user-specified cell offset.

        Args:
            cell_offset (int, optional): Number of additional cells to
                offset the mask relative to the bottom-track cell.
                Positive values move the mask shallower (masking more
                cells above the bed), and negative values move it
                deeper. Defaults to 0.
            incl_sidelobe (bool, optional): If True, applies a
                sidelobe-interference correction by scaling the
                bottom-track range by ``cos(beam_angle)``. Defaults to
                True.

        Returns:
            np.ndarray: Boolean mask with shape
            ``(n_ensembles, n_bins, n_beams)`` where True indicates
            valid (above-bottom) cells and False indicates cells at or
            below the seabed.
        """
        # Get bottom track range (in meters)
        bt_range = self.bottom_track.range_to_seabed  # shape: (n_beams, n_ensembles)
        
        if incl_sidelobe:
            bt_range = bt_range*np.cos(self.geometry.beam_angle*np.pi/180)
            
        # Expand bottom track range to match beam data shape: (n_beams, n_bins, n_ensembles)
        bt_range_expanded = np.repeat(bt_range[:, np.newaxis, :], self.geometry.n_bins, axis=1)
    
        # Get bin center distances (in meters)
        bin_centers = np.outer(self.geometry.bin_midpoint_distances, np.ones(self.time.n_ensembles))
        bin_centers = np.repeat(bin_centers[np.newaxis, :, :], self.geometry.n_beams, axis=0)
    
        # Apply offset (positive = mask above bottom, negative = below)
        bin_centers += cell_offset * self.geometry.bin_length
    
        # Create mask: True = valid (above bottom), False = invalid (below bottom)
        mask = bin_centers < bt_range_expanded
        mask = mask.T
        
        return mask
        
    def _get_datetimes(self, apply_corrections: bool = True) -> List[datetime]:
        """Return ensemble datetimes, optionally applying time corrections.

        Datetimes are read from the PD0 file and, if requested, are
        shifted by the configured UTC offset and transect time shift.

        Args:
            apply_corrections (bool, optional): If True, applies
                ``corrections.utc_offset`` and
                ``corrections.transect_shift_t`` (in hours) to the raw
                datetimes. Defaults to True.

        Returns:
            np.ndarray: One-dimensional array of ``datetime`` objects
            with shape ``(n_ensembles,)``.
        """
        datetimes = self._pd0.get_datetimes()
        if apply_corrections:
            delta = timedelta(hours=float(self.corrections.utc_offset)) + \
                    timedelta(hours=float(self.corrections.transect_shift_t))
            datetimes = [dt + delta for dt in datetimes]
        
        return np.array(datetimes)
    
    def _beam_to_inst_coords(self, B):
        """Transform beam velocities into instrument-frame coordinates.

        The transformation uses the beam pattern and beam angle from
        the PD0 fixed leader configuration. It supports both profile
        velocities and bottom-track velocities.

        Args:
            B (np.ndarray): Beam-space velocities. Accepted shapes are:
                * ``(T, K, 4)``: profile beams
                  ``[..., 0:4] = [b1, b2, b3, b4]``.
                * ``(T, 4)``: bottom-track beams.
                * ``(T, 3)``: already in instrument frame
                  ``[X, Y, Z]`` (returned unchanged except for dtype).

        Returns:
            np.ndarray: Instrument-frame velocities. Shapes mirror the
            input:
                * Input ``(T, K, 4)`` → output ``(T, K, 4)`` where
                  ``[..., 0:3] = [X, Y, Z]`` and ``[..., 3]`` is error
                  velocity.
                * Input ``(T, 4)`` → output ``(T, 3)`` = ``[X, Y, Z]``.
                * Input ``(T, 3)`` → output ``(T, 3)`` = ``[X, Y, Z]``.
        """
        B = np.asarray(B, dtype=float)
    
        # Geometry from PD0 fixed leader
        beam_pattern = self._pd0.fixed_leaders[0].system_configuration.beam_pattern
        beam_angle = int(self._pd0.fixed_leaders[0].system_configuration.beam_angle[:2])
        c = {"CONVEX": 1, "CONCAVE": -1}[beam_pattern]
    
        th = np.deg2rad(beam_angle)
        a = 1.0 / (2.0 * np.sin(th))
        b = 1.0 / (4.0 * np.cos(th))
        d = a / np.sqrt(2.0)
    
        # Matrices
        M = np.array([  # 4x4, rows X,Y,Z,err; cols b1..b4
            [c * a, -c * a, 0.0, 0.0],
            [0.0, 0.0, -c * a, c * a],
            [b, b, b, b],
            [d, d, -d, -d],
        ], float)
        
        I =  B @ M.T
        return I
  
    def _inst_to_earth_coords(self,I, heading_deg, pitch_deg, roll_deg,
                      declination_deg=0.0, heading_bias_deg=0.0, use_tilts=True):
        """Rotate instrument-frame velocities into earth (ENU) coordinates.

        Args:
            I (np.ndarray): Instrument-frame velocities with shape
                ``(T, K, 3)`` where the last axis is ``[X, Y, Z]``.
            heading_deg (np.ndarray): Heading time series in degrees
                with shape ``(T,)``.
            pitch_deg (np.ndarray): Pitch time series in degrees with
                shape ``(T,)``.
            roll_deg (np.ndarray): Roll time series in degrees with
                shape ``(T,)``.
            declination_deg (float, optional): Magnetic declination
                added to the heading (degrees). Defaults to 0.0.
            heading_bias_deg (float, optional): Additional heading bias
                (degrees). Defaults to 0.0.
            use_tilts (bool, optional): If False, pitch and roll are
                treated as zero when constructing the rotation
                matrices. Defaults to True.

        Returns:
            np.ndarray: Earth-frame velocities with shape ``(T, K, 3)``
            where the last axis is ``[E, N, U]`` in m/s.
        """
        T = I.shape[0]
        K = I.shape[1]
        E = np.empty_like(I)
    
        H = np.deg2rad(heading_deg + declination_deg + heading_bias_deg)
        P = np.deg2rad(pitch_deg if use_tilts else 0.0)
        R = np.deg2rad(roll_deg if use_tilts else 0.0)
    
        CH, SH = np.cos(H), np.sin(H)
        CP, SP = np.cos(P), np.sin(P)
        CR, SR = np.cos(R), np.sin(R)
    
        for t in range(T):
            # Rotation matrix M_t (instrument XYZ → earth ENU), Eq. 18 (TRDI)
            M_t = np.array([
                [CH[t]*CR[t] + SH[t]*SP[t]*SR[t],  SH[t]*CP[t],  CH[t]*SR[t] - SH[t]*SP[t]*CR[t]],
                [-SH[t]*CR[t] + CH[t]*SP[t]*SR[t], CH[t]*CP[t], -SH[t]*SR[t] - CH[t]*SP[t]*CR[t]],
                [          -CP[t]*SR[t],                 SP[t],              CP[t]*CR[t]],
            ], dtype=float)
    
            # (K,3) @ (3,3) → (K,3)
            E[t] = I[t] @ M_t.T
    
        return E
    
    def _inst_to_ship_coords(self,I, pitch_deg, roll_deg, use_tilts=True):
        """Rotate instrument-frame velocities into ship (SFU) coordinates.

        The transformation assumes zero heading (H = 0) so that the
        ship frame is aligned with the instrument frame in yaw, and
        only pitch and roll rotations are applied.

        Args:
            I (np.ndarray): Instrument-frame velocities with shape
                ``(T, K, 3)`` where the last axis is ``[X, Y, Z]``.
            pitch_deg (np.ndarray): Pitch time series in degrees with
                shape ``(T,)``.
            roll_deg (np.ndarray): Roll time series in degrees with
                shape ``(T,)``.
            use_tilts (bool, optional): If False, pitch and roll are
                treated as zero when constructing the rotation
                matrices. Defaults to True.

        Returns:
            np.ndarray: Ship-frame velocities with shape ``(T, K, 3)``
            where the last axis is ``[Starboard, Forward, Up]`` in m/s.
        """
        
        T = I.shape[0]
        K = I.shape[1]
        S = np.empty_like(I)
    
        P = np.deg2rad(pitch_deg if use_tilts else 0.0)
        R = np.deg2rad(roll_deg if use_tilts else 0.0)
        CP, SP = np.cos(P), np.sin(P)
        CR, SR = np.cos(R), np.sin(R)
    
        for t in range(T):
            # H=0 ⇒ CH=1, SH=0. TRDI Eq. 18 reduced to ship frame.
            M = np.array([
                [CR[t],          0.0,        SR[t]],       # → Starboard
                [SP[t]*SR[t],    CP[t],     -SP[t]*CR[t]], # → Forward
                [-CP[t]*SR[t],   SP[t],      CP[t]*CR[t]], # → Up
            ], dtype=float)
    
            # (K,3) @ (3,3) → (K,3)
            S[t] = I[t] @ M.T
    
        return S
               
    def _get_transformed_velocity(
        self, target_frame: str = "earth"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return profile velocities transformed to a target frame.

        Velocities are read from the PD0 file in its native coordinate
        frame and, if necessary, transformed to the requested frame
        (beam, instrument, ship, or earth). Error velocity is carried
        through where available.

        Args:
            target_frame (str, optional): Desired output frame. One of
                ``'beam'``, ``'instrument'``, ``'ship'``, or
                ``'earth'``. Defaults to ``'earth'``.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                Component arrays with shape ``(T, K)``:
                - ``u``: first component (beam/instrument/ship/earth).
                - ``v``: second component.
                - ``w``: third component.
                - ``err``: error velocity.

        Raises:
            ValueError: If the native frame is unknown or the requested
                transformation is not supported.
        """
        frame = self._pd0.fixed_leaders[0].coordinate_transform.frame
        heading_deg = self.aux_sensor_data.heading
        pitch_deg = self.aux_sensor_data.pitch
        roll_deg = self.aux_sensor_data.roll
        declination_deg = self.corrections.magnetic_declination
        heading_bias_deg = self.geometry.crp_rotation_angle
        use_tilts = True
    
        raw = self._pd0.get_velocity() / 1000.0  # (T,K,4) mm/s → m/s
    
        if frame == target_frame:
            return raw[..., 0], raw[..., 1], raw[..., 2], raw[..., 3]
    
        if frame == "beam":
            I4 = self._beam_to_inst_coords(raw)     # (T,K,4)
            err = I4[..., 3]
            I = I4[..., :3]
            if target_frame == "instrument":
                return I[..., 0], I[..., 1], I[..., 2], err
            if target_frame == "ship":
     
                S = self._inst_to_ship_coords(I, pitch_deg, roll_deg)
                return S[..., 0], S[..., 1], S[..., 2], err
            if target_frame == "earth":
                E = self._inst_to_earth_coords(
                    I, heading_deg, pitch_deg, roll_deg,
                    declination_deg, heading_bias_deg,)
                return E[..., 0], E[..., 1], E[..., 2], err
    
        elif frame == "instrument":
            err = raw[..., 3]
            I = raw[..., :3]
            if target_frame == "instrument":
                return I[..., 0], I[..., 1], I[..., 2], err
            if target_frame == "ship":
                S = self._inst_to_ship_coords(I, pitch_deg, roll_deg)
                return S[..., 0], S[..., 1], S[..., 2], err
            if target_frame == "earth":
                E = self._inst_to_earth_coords(
                    I, heading_deg, pitch_deg, roll_deg,
                    declination_deg, heading_bias_deg)
                return E[..., 0], E[..., 1], E[..., 2], err
    
        elif frame == "ship":
            S = raw[..., :3]
            err = raw[..., 3]
            if target_frame == "ship":
                return S[..., 0], S[..., 1], S[..., 2], err
            if target_frame == "earth":
                E = self._ship_to_earth_coords(raw, heading_deg)  # preserves err
                return E[..., 0], E[..., 1], E[..., 2], E[..., 3]
    
        elif frame == "earth":
            if target_frame == "ship":
                raise NotImplementedError("earth → ship not supported")
    
        else:
            raise ValueError(f"Unknown native frame '{frame}'.")
    
        raise ValueError(
            f"Transformation from native '{frame}' to '{target_frame}' not supported."
        )

    def _get_bt_velocity(
        self, target_frame: str = "earth"
    ) -> Tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
        """Return bottom-track velocities transformed to a target frame.

        Bottom-track velocities are decoded from the PD0 file in their
        native coordinate frame and, if requested, converted to
        instrument, ship, or earth frames using the current attitude and
        correction parameters.

        Args:
            target_frame (str, optional): Desired output frame. One of
                ``'beam'``, ``'instrument'``, ``'ship'``, or
                ``'earth'``. Defaults to ``'earth'``.

        Returns:
            tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
                Component arrays with shape ``(T,)``:
                - beam: ``b1``, ``b2``, ``b3``, ``b4``.
                - instrument: ``X``, ``Y``, ``Z``, ``err``.
                - ship: ``S``, ``F``, ``U``, ``err``.
                - earth: ``E``, ``N``, ``U``, ``err``.

        Raises:
            ValueError: If the native frame or requested transformation
                is not supported for bottom-track data.
        """
        frame = self._pd0.fixed_leaders[0].coordinate_transform.frame
    
        # Attitude and corrections (length T)
        heading_deg = self.aux_sensor_data.heading
        pitch_deg = self.aux_sensor_data.pitch
        roll_deg = self.aux_sensor_data.roll
        declination_deg = self.corrections.magnetic_declination
        heading_bias_deg = self.geometry.crp_rotation_angle
        use_tilts = True
    
        # Native BT: (T,4) in mm/s → m/s
        raw = self.bottom_track.velocity.T / 1000.0  # (T,4)
    
        # Already in requested frame
        if frame == target_frame:
            return raw[:, 0], raw[:, 1], raw[:, 2], raw[:, 3]
           
        # Beam/instrument → ship/earth, split error BEFORE rotation
        if frame in ("beam", "instrument"):
            I4 = self._beam_to_inst_coords(raw) if frame == "beam" else raw  # (T,4)
            err = I4[:, 3]
            I = I4[:, :3]                                                    # (T,3)
    
            if target_frame == "instrument":
                return I[:, 0], I[:, 1], I[:, 2], err
    
            if target_frame == "ship":
                S3 = self._inst_to_ship_coords(I[:, None, :], pitch_deg, roll_deg, use_tilts)
                S = S3[:, 0, :]                                              # (T,3)
                return S[:, 0], S[:, 1], S[:, 2], err
    
            if target_frame == "earth":
                E3 = self._inst_to_earth_coords(
                    I[:, None, :],
                    heading_deg,
                    pitch_deg,
                    roll_deg,
                    declination_deg,
                    heading_bias_deg,
                    use_tilts,
                )
                E = E3[:, 0, :]                                              # (T,3)
                return E[:, 0], E[:, 1], E[:, 2], err
    
        # Ship → earth or pass-through
        if frame == "ship":
            if target_frame == "ship":
                return raw[:, 0], raw[:, 1], raw[:, 2], raw[:, 3]
            
            if target_frame == "earth":
                E4 = self._ship_to_earth_coords(raw, heading_deg)            # (T,4)
                return E4[:, 0], E4[:, 1], E4[:, 2], E4[:, 3]
    
        # Earth → ship not implemented
        raise ValueError(f"Transformation from native '{frame}' to '{target_frame}' not supported for BT.")

    def _calculate_height_above_bed(self, clamp_zero: bool = True):
        """Compute height above bed (HAB) for each ensemble, bin, and beam.

        HAB is derived from the adjusted bottom-track range and the
        vertical distance of each bin center from the transducer, using
        beam geometry in earth coordinates.

        Args:
            clamp_zero (bool, optional): If True, negative HAB values
                are set to ``np.nan`` (i.e., bins below the interpolated
                seabed are treated as invalid). Defaults to True.

        Returns:
            np.ndarray: HAB array with shape ``(n_ensembles, n_bins,
            n_beams)`` in meters. Entries are ``np.nan`` if beam-facing
            is not ``'down'``, bottom-track geometry is unavailable, or
            the necessary arrays cannot be reconciled to the expected
            shapes.
        """
        ne = int(self.time.n_ensembles)
        nb = int(self.geometry.n_bins)
        nm = int(self.geometry.n_beams)
    
        if str(self.geometry.beam_facing).lower() != "down":
            return np.full((ne, nb, nm), np.nan)
    
        bt = getattr(self, "bottom_track", None)
        if bt is None or not hasattr(bt, "adjusted_range_to_seabed"):
            return np.full((ne, nb, nm), np.nan)
    
        # Bin midpoints: rel_xyz.z is transducer->bin in earth z. Positive up => make positive down.
        _, rel_xyz, _ = self._calculate_beam_geometry()      # rel_xyz.z: (ne, nb, nm)
        dz_vert = -np.asarray(rel_xyz.z, float)              # positive down
    
        # Adjusted BT depth: shape must be (n_beams, n_ensembles)
        adj = np.asarray(bt.adjusted_range_to_seabed, float)
        if adj.shape == (ne, nm):
            adj = adj.T
        if adj.shape != (nm, ne):
            return np.full((ne, nb, nm), np.nan)
    
        # Broadcast BT depth to all bins
        adj_full = np.broadcast_to(adj.T[:, None, :], (ne, nb, nm))
    
        # HAB = bottom depth - bin vertical depth
        hab = adj_full - dz_vert
    
        # Mask invalids using broadcasted shapes
        invalid = ~np.isfinite(adj_full) | ~np.isfinite(dz_vert)
        hab[invalid] = np.nan
    
        if clamp_zero:
            hab[hab < 0] =np.nan
    
        return hab

    def _calculate_beam_geometry(self):
            
            crp_theta = self.geometry.crp_rotation_angle
            off = np.array([self.geometry.crp_offset_x,
                            self.geometry.crp_offset_y,
                            self.geometry.crp_offset_z])
            dr = self.geometry.beam_dr
            R_crp = Utils.gen_rot_z(crp_theta)
        
            bases = np.array([[ dr, -dr,  0,   0],
                              [  0,   0, dr, -dr],
                              [  0,   0,  0,   0]], dtype=float)
    
            rel_orig = (R_crp @ bases)
        
            n_beams = self.geometry.n_beams
            n_cells = self.geometry.n_bins
            ne = self.time.n_ensembles
            beam_angle = self.geometry.beam_angle
            rel = np.zeros((3, n_beams, n_cells, ne))
        
            bin_mids = self.geometry.bin_midpoint_distances
            z_off = -bin_mids if self.geometry.beam_facing == "down" else bin_mids
        
            for b in range(n_beams):
                if b in (0, 1):
                    Rb = Utils.gen_rot_y((-1 if b == 0 else 1) * beam_angle)
                else:
                    Rb = Utils.gen_rot_x((1 if b == 3 else -1) * beam_angle)
                mids = np.zeros((3, n_cells))
                mids[2, :] = z_off
                base = Rb @ mids
                rel[:, b, :, :] = base[:, :, None]
    
            for e in range(ne):
                yaw = -(self.position.heading if isinstance(self.position.heading, float) else self.position.heading[e] + crp_theta)
                pitch = self.position.pitch if isinstance(self.position.pitch, float) else self.position.pitch[e]
                roll = self.position.roll if isinstance(self.position.roll, float) else self.position.roll[e]
                R_att = Utils.gen_rot_z(yaw) @ Utils.gen_rot_y(pitch) @ Utils.gen_rot_x(roll)
                for b in range(n_beams):
                    rel[:, b, :, e] = (
                        R_att @ rel[:, b, :, e]
                        + (R_att @ rel_orig[:, b])[:, None]
                        + (R_att @ (R_crp @ off))[:, None]
                    )
    
            # choose position source based on EPSG type
            from pyproj import CRS
            src = CRS.from_user_input(self.position.epsg)
            if src.is_geographic:
                xloc = np.full(ne, self.position.x_local_m) if isinstance(self.position.x_local_m, (float, int)) else np.asarray(self.position.x_local_m)
                yloc = np.full(ne, self.position.y_local_m) if isinstance(self.position.y_local_m, (float, int)) else np.asarray(self.position.y_local_m)
            else:
                xloc = np.full(ne, self.position.x) if isinstance(self.position.x, (float, int)) else np.asarray(self.position.x)
                yloc = np.full(ne, self.position.y) if isinstance(self.position.y, (float, int)) else np.asarray(self.position.y)
            zz = np.full(ne, self.position.z) if isinstance(self.position.z, float) else np.asarray(self.position.z)
    
            from pyproj import CRS
    
            xx = np.full(ne, self.position.x) if isinstance(self.position.x, float) else np.asarray(self.position.x)
            yy = np.full(ne, self.position.y) if isinstance(self.position.y, float) else np.asarray(self.position.y)
            xloc = np.full(ne, self.position.x_local_m) if isinstance(self.position.x_local_m, (float, int)) else np.asarray(self.position.x_local_m)
            yloc = np.full(ne, self.position.y_local_m) if isinstance(self.position.y_local_m, (float, int)) else np.asarray(self.position.y_local_m)
    
            src = CRS.from_user_input(self.position.epsg)
            use_local = src.is_geographic
    
            gx = np.empty((ne, n_cells, n_beams))
            gy = np.empty((ne, n_cells, n_beams))
            gz = np.empty((ne, n_cells, n_beams))
    
            for e in range(ne):
                xb = xloc[e] if use_local else xx[e]
                yb = yloc[e] if use_local else yy[e]
                gx[e] = (xb + rel[0, :, :, e]).T
                gy[e] = (yb + rel[1, :, :, e]).T
                gz[e] = (zz[e] + rel[2, :, :, e]).T
    
            relative_beam_midpoint_positions = XYZ(
                x=rel[0].transpose(2, 1, 0),
                y=rel[1].transpose(2, 1, 0),
                z=rel[2].transpose(2, 1, 0),
            )
            
            rel_orig += off[:, None]  
            geographic_beam_midpoint_positions = XYZ(x=gx, y=gy, z=gz)
    
            return rel_orig, relative_beam_midpoint_positions, geographic_beam_midpoint_positions

    def _calculate_bottom_track_geometry(self):
        """
        Tilt-corrected vertical bottom-track depth per beam×ensemble.
    
        Parameters
        ----------
        return_points : bool
            If True, also return seabed hit points XYZ(time, beam).
        save_adjusted : bool
            If True, write self.bottom_track.adjusted_range_to_seabed.
    
        Returns
        -------
        adjusted_range_to_seabed : (n_beams, n_ensembles) float
        seabed_points : XYZ or None
        """
        import numpy as np
        from pyproj import CRS
    
        n_beams = int(self.geometry.n_beams)
        n_ens   = int(self.time.n_ensembles)
    
        # Preconditions
        bt = getattr(self, "bottom_track", None)
        if bt is None or not hasattr(bt, "range_to_seabed"):
            adj = np.full((n_beams, n_ens), np.nan)
            return adj, None if return_points else None
    
        if str(self.geometry.beam_facing).lower() != "down":
            adj = np.full((n_beams, n_ens), np.nan)
            return adj, None if return_points else None
    
        # Slant TRDI ranges (beam, ens) – may arrive in other shapes; coerce
        R_bt = np.asarray(bt.range_to_seabed, float)
        if R_bt.ndim == 1:
            R_bt = R_bt[:, None] if R_bt.size == n_beams else R_bt[None, :]
        if R_bt.shape == (n_ens, n_beams):
            R_bt = R_bt.T
        if R_bt.shape != (n_beams, n_ens):
            adj = np.full((n_beams, n_ens), np.nan)
            return adj, None if return_points else None
    
        # CRP rotation and beam bases (instrument frame)
        crp_theta = float(self.geometry.crp_rotation_angle)
        dr = float(self.geometry.beam_dr)
        R_crp = Utils.gen_rot_z(crp_theta)
        bases = np.array([[ dr, -dr,  0,   0],
                          [  0,   0,  dr, -dr],
                          [  0,   0,   0,   0]], float)[:, :n_beams]
        rel_orig = R_crp @ bases
        off_vec = np.array([self.geometry.crp_offset_x,
                            self.geometry.crp_offset_y,
                            self.geometry.crp_offset_z], float)
    
        # Beam unit vectors in instrument frame (down-looking => -Z)
        beam_angle = float(self.geometry.beam_angle)
        out_sign = -1.0
        u_beam_inst = np.zeros((n_beams, 3), float)
        for b in range(n_beams):
            if b in (0, 1):
                Rb = Utils.gen_rot_y((-1 if b == 0 else 1) * beam_angle)
            else:
                Rb = Utils.gen_rot_x((1 if b == 3 else -1) * beam_angle)
            v = Rb @ np.array([0.0, 0.0, out_sign])
            nrm = np.linalg.norm(v)
            u_beam_inst[b] = v / nrm if nrm > 0 else v
    
        # Position arrays for optional hit points
        def ens_array(val):
            return np.full(n_ens, float(val)) if isinstance(val, (int, float)) else np.asarray(val, float)
    
        xx   = ens_array(self.position.x)
        yy   = ens_array(self.position.y)
        xloc = ens_array(self.position.x_local_m)
        yloc = ens_array(self.position.y_local_m)
        zz   = ens_array(self.position.z)
    
        use_local = CRS.from_user_input(self.position.epsg).is_geographic
    
        # Outputs
        adjusted = np.full((n_beams, n_ens), np.nan, float)
        seabed_points = None

        gx = np.full((n_ens, n_beams), np.nan, float)
        gy = np.full((n_ens, n_beams), np.nan, float)
        gz = np.full((n_ens, n_beams), np.nan, float)
    
        # Per-ensemble attitude
        for e in range(n_ens):
            heading = self.position.heading if isinstance(self.position.heading, float) else self.position.heading[e]
            pitch   = self.position.pitch  if isinstance(self.position.pitch,  float) else self.position.pitch[e]
            roll    = self.position.roll   if isinstance(self.position.roll,   float) else self.position.roll[e]
            yaw = -(heading + crp_theta)
    
            R_att = Utils.gen_rot_z(yaw) @ Utils.gen_rot_y(pitch) @ Utils.gen_rot_x(roll)
    
            # Beam bases in earth frame
            base_e = R_att @ (rel_orig + off_vec[:, None])
    
            xb = xloc[e] if use_local else xx[e]
            yb = yloc[e] if use_local else yy[e]
            zb = zz[e]
    
            for b in range(n_beams):
                r = R_bt[b, e]
                if not np.isfinite(r):
                    continue
    
                u = R_att @ u_beam_inst[b]
                nrm = np.linalg.norm(u)
                if nrm == 0 or not np.isfinite(nrm):
                    continue
                u /= nrm
    
                vz = abs(float(u[2]))            # cosine with vertical
                adjusted[b, e] = r * vz          # vertical depth from transducer
    
                
                gx[e, b] = xb + base_e[0, b] + u[0] * r
                gy[e, b] = yb + base_e[1, b] + u[1] * r
                gz[e, b] = zb + base_e[2, b] + u[2] * r
    
        seabed_points = XYZ(x=gx, y=gy, z=gz)
    
        return adjusted, seabed_points

    def _counts_to_absolute_backscatter(self, E,E_r, k_c, alpha, C, R, Tx_T, Tx_PL, P_dbw):
        """
        Absolute Backscatter Equation from Deines (Updated - Mullison 2017 TRDI Application Note FSA031)
    
        Parameters
        ----------
        E : ndarray
            Measured echo intensity, in counts.
        R : ndarray
            Along-beam range to the measurement in meters.
        Tx_T : ndarray
            Transducer temperature in deg C.
        Tx_PL : ndarray
            Transmit pulse length in dBm.
        E_r : float
            Measured RSSI amplitude in absence of signal (noise), in counts.
        k_c : float
            Factor to convert amplitude counts to decibels (dB).
            
        alpha_w : float
            Acoustic absorption of water (dB/m), array of same shape as E.
            
        alpha_s : float
            Acoustic absorption of sediment (dB/m), array of same shape as E.
                    
        C : float
            Constant combining several parameters specific to the instrument.
        P_DBW : float
            Transmit pulse power in dBW.
    
        Returns
        -------
        Sv : ndarray
            Apparent volume scattering strength.
        StN : ndarray
            True signal to noise ratio.
        """
        
        
        E_db = k_c * E / 10
        E_r_db = k_c * E_r / 10
        
        # Prevent division by zero and negative log input
        with np.errstate(divide='ignore', invalid='ignore'):
            delta_power = np.maximum(10 ** (0.1 * k_c * (E - E_r)) - 1, 1e-10)
            Sv = (
                C
                + np.log10(np.maximum((Tx_T + 273.16) * (R ** 2), 1e-10)) * 10
                - np.log10(np.maximum(Tx_PL, 1e-10)) * 10
                - P_dbw
                + 2 * alpha * R
                + np.log10(delta_power) * 10
            )
    
            StN = (10 ** E_db - 10 ** E_r_db) / np.maximum(10 ** E_r_db, 1e-10)
    
        Sv = np.where(np.isfinite(Sv), Sv, np.nan)
        StN = np.where(np.isfinite(StN), StN, np.nan)
    
        return Sv, StN
         

    def _calculate_absolute_backscatter(self) -> np.ndarray:
        """
        Convert echo intensity to absolute backscatter.

        Returns:
        --------
            np.ndarray: A 2D array of absolute backscatter values for each ensemble and cell.
        """
        echo_intensity = self._pd0.get_echo_intensity()
        E_r = self.abs_params.E_r
        WB = self.abs_params.WB
        C = self.abs_params.C
        k_c = self.abs_params.rssi
        alpha_w = self.abs_params.alpha_w # water attenuation coefficient 
        alpha_s = self.abs_params.alpha_s # sediment attenuation coefficient 
        P_dbw = self.abs_params.P_dbw
        temperature = self.water_properties.temperature #np.outer(self._pd0._get_sensor_temperature(), np.ones(self.geometry.n_bins))
        bin_distances = np.outer(self.geometry.bin_midpoint_distances, np.ones(self.time.n_ensembles)).T
        transmit_pulse_length = np.outer(self.abs_params.tx_pulse_length, np.ones(self.geometry.n_bins))

        X = []
        StN = []
        for i in range(self.geometry.n_beams):
            E = echo_intensity[:, :, i]
            alpha = alpha_w + alpha_s[:,:,i]
            sv, stn = self._counts_to_absolute_backscatter(E, E_r, float(k_c[i+1]), alpha, C, bin_distances, temperature, transmit_pulse_length, P_dbw)
            X.append(sv)
            StN.append(stn)
        X = np.array(X).transpose(1, 2, 0).astype(int).astype(float)  # Shape: (n_ensembles, n_cells, n_beams) Absolute backscatter
        StN = np.array(StN).transpose(1, 2, 0).astype(int).astype(float)  # Shape: (n_ensembles, n_cells, n_beams) Signal to noise ratio
        
        return X, StN

    def _water_absorption_coeff(self, T, S, z, f, pH):
        """
        Compute acoustic absorption in seawater using the Francois & Garrison (1982) model.
    
        Parameters
        ----------
        T : array_like
            Temperature in °C.
        S : array_like
            Salinity in PSU.
        z : array_like
            Depth in meters.
        f : array_like
            Frequency in kHz.
        pH : array_like
            Seawater pH (unitless).
    
        Returns
        -------
        alpha_w : array_like
            Sound absorption in dB/m.
        """
        T_K = 273 + T  # Temperature in Kelvin
    
        # Sound speed approximation (c in m/s)
        c = 1449.2 + 4.6 * T - 0.055 * T**2 + 0.00029 * T**3 + (0.0134 * T) * (S - 35) + 0.016 * z
    
        # Boric acid contribution
        A1 = (8.686 / c) * 10**(0.78 * pH - 5)
        f1 = 2.8 * np.sqrt(S / 35) * 10**(4 - (1245 / T_K))
    
        # MgSO4 contribution
        A2 = (21.44 * S / c) * (1 + 0.025 * T)
        f2 = (8.17 * 10**(8 - (1990 / T_K))) / (1 + 0.0018 * (S - 35))
    
        # Pure water contribution (temperature-dependent polynomial)
        A3 = np.where(
            T <= 20,
            4.937e-4 - 2.59e-5 * T + 9.11e-7 * T**2 - 1.5e-8 * T**3,
            3.964e-4 - 1.146e-5 * T + 1.45e-7 * T**2 - 6.5e-8 * T**3,
        )
        A3 = np.clip(A3, 0, None)
    
        # Optional pressure corrections (empirical, not in original F&G 1982)
        P2 = 1 - 1.37e-4 * z + 6.2e-9 * z**2
        P3 = 1 - 3.83e-5 * z + 4.9e-10 * z**2
    
        # Total absorption in dB/km
        alpha_dBkm = (
            A1 * (f**2 / (f1**2 + f**2)) +
            A2 * P2 * (f**2 / (f2**2 + f**2)) +
            A3 * P3 * f**2
        )
    
        # Convert to dB/m
        return alpha_dBkm / 1000

    def _sediment_absorption_coeff(self,ps, pw, d, SSC, T, S, f, z):

        c = 1449.2 + 4.6 * T - 0.055 * T**2 + 0.00029 * T**3 + (0.0134 * T) * (S - 35) + 0.016 * z
        v = (40e-6) / (20 + T)
        B = (np.pi * f / v) * 0.5
        delt = 0.5 * (1 + 9 / (B * d))
        sig = ps / pw
        s = 9 / (2 * B * d) * (1 + 2 / (B * d))
        k = 2 * np.pi / c
    
        term1 = k**4 * d**3 / (96 * ps)
        term2 = k * (sig - 1)**2 / (2 * ps)
        term3 = (s / (s**2 + (sig + delt)**2)) * (20 / np.log(10)) * SSC
    
        return term1 + term2 + term3
        
    def _backscatter_to_ssc(self,backscatter):
        ssc = 10**(self.ssc_params.A + backscatter*self.ssc_params.B)
        background_ssc_mode = self.corrections.background_ssc_mode
        background_ssc = self.corrections.background_ssc
        if background_ssc_mode.lower() == 'percentile':
            background_ssc = np.nanpercentile(ssc, self.corrections.background_ssc_percentile)
        mask = ~np.isnan(ssc)
        ssc[mask] = ssc[mask] - background_ssc
        mask = ssc < 0
        ssc[mask] = 0.0
        return ssc
        
        
   
    def _calculate_ssc(self):
        """
        Calculate SSC from absolute backscatter using iterative alpha correction.
    
        Parameters
        ----------
        A1 : float
            Coefficient for ABS to NTU conversion.
        B1 : float
            Exponent for ABS to NTU conversion.
        A2 : float
            Coefficient for NTU to SSC conversion.
        """
        bks = self.beam_data.absolute_backscatter
        return self._backscatter_to_ssc(bks)


class Plotting:
    def __init__(self, adcp: ADCP) -> None:
        self._adcp = adcp

    def platform_orientation(self, title=None):
        pos = self._adcp.geometry.relative_beam_origin
        fig, (ax, ax2) = PlottingShell.subplots(
            figheight=6, figwidth=4, nrow=2, height_ratios = [3,1]
        )
        
        # Temporary limit calc for scaling label offsets
        x_span = max(abs(pos[0, :])) or 1
        y_span = max(abs(pos[1, :])) or 1
        r_offset = 0.05 * max(x_span, y_span)
        
        # Metadata dictionary
        meta = {
            'Δx': self._adcp.geometry.crp_offset_x,
            'Δy': self._adcp.geometry.crp_offset_y,
            'Δz': self._adcp.geometry.crp_offset_z,
            'Rotation (° CW)': self._adcp.geometry.crp_rotation_angle,
        }
        
        # --- Top plot: beam geometry ---
        for b in range(self._adcp.geometry.n_beams):
            x = pos[0, b]
            y = pos[1, b]

            ax.scatter(x, y, s=25, c='black', zorder=3, marker = rf'${str(b+1)}$')

        limit = max(max(map(abs, ax.get_xlim())), max(map(abs, ax.get_ylim()))) * 1.2
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_aspect('equal', adjustable='box')
        
        arrow_length = limit * 0.2
        ax.arrow(0, 0, 0, arrow_length,
                 head_width=arrow_length * 0.08, head_length=arrow_length * 0.12,
                 fc='blue', ec='blue', length_includes_head=True, linewidth=1)
        ax.text(0, arrow_length + r_offset, "Vessel direction",
                ha='center', va='bottom', fontsize=8, color='blue')
        
        ax.scatter(0, 0, s=20, marker='s', color='red')
        ax.annotate("Vessel CRP", (0, -r_offset),
                    ha='center', va='top', fontsize=8, color='red',
                    bbox=dict(boxstyle="round,pad=0.2", fc="white", ec="none", alpha=0.6))
        
        mean_x = np.mean(pos[0, :])
        mean_y = np.mean(pos[1, :])
        meta_text = "\n".join(
            f"{k}: {v:.3f}" if isinstance(v, (int, float)) else f"{k}: {v}"
            for k, v in meta.items()
        )
        pad_factor = 0.80
        if abs(mean_x) >= abs(mean_y):
            text_x = -np.sign(mean_x) * limit * pad_factor if mean_x != 0 else -limit * pad_factor
            text_y = 0
        else:
            text_x = 0
            text_y = -np.sign(mean_y) * limit * pad_factor if mean_y != 0 else -limit * pad_factor
        ax.text(text_x, text_y, meta_text,
                ha='center', va='center', fontsize=8,
                bbox=dict(fc="white", ec="none", alpha=0.3))
        
        ax.set_xlabel('Δx (m)')
        ax.set_ylabel('Δy (m)')
        if title is None:
            title = f'{self._adcp.name} Platform Orientation'
        ax.set_title(title)
        
        # --- Bottom plot: Z-offset relative to CRP ---
        y = np.mean(pos[1,:])
        z = np.mean(pos[2,:])
        
        ax2.scatter(0, 0, c='red', marker='s', s=10)
        ax2.scatter(y, z, c='black', s=10)
        
        # Determine plot limits for bottom plot
        limit2 = max(max(map(abs, ax2.get_xlim())), max(map(abs, ax2.get_ylim()))) * 1.2
        ax2.set_xlim(-limit2, limit2)
        ax2.set_ylim(-limit2, limit2)
        ax2.set_aspect('equal', adjustable='datalim')
        
        # Water line arrow spanning full x-axis extent
        ax2.arrow(-limit2, 0, 2 * limit2, 0,
                  fc='blue', ec='blue', linestyle='--', alpha=0.5,
                  length_includes_head=True, linewidth=1)
        ax2.text(limit2, 0, "Water line",
                 ha='right', va='bottom', fontsize=8, color='blue', alpha=0.7)
        
        ax2.set_ylabel("Δz (m)")
        ax2.set_xlabel("Δy (m)")
        
        fig.tight_layout()
        return fig, (ax, ax2)
        
    def transect_animation(
        self,
        figheight: float = 5,
        figwidth: float = 5,
        cmap: str | plt.Colormap = 'viridis',
        vmin: float | None = None,
        vmax: float | None = None,
        show_pos_trail: bool = True,
        show_beam_trail: bool = True,
        pos_trail_len: int | None = None,
        beam_trail_len: int | None = None,
        interval_ms: int = 50,
        cax_label: str = 'Absolute backscatter',
        save_gif: bool = False,
        gif_name: str | None = None
    ) -> FuncAnimation:
        adcp = self._adcp
        
        t = np.asarray(adcp.time.ensemble_datetimes)
        ens = np.asarray(adcp.time.ensemble_numbers)
        
        if adcp.position.epsg == 4326:
            x = np.asarray(adcp.position.x_local_m, dtype=float)
            y = np.asarray(adcp.position.y_local_m, dtype=float)
        else:
            x = np.asarray(adcp.position.x, dtype=float)
            y = np.asarray(adcp.position.y, dtype=float)
        
        
        beam_x = np.asarray(adcp.geometry.geographic_beam_midpoint_positions.x, dtype=float)
        beam_y = np.asarray(adcp.geometry.geographic_beam_midpoint_positions.y, dtype=float)
        beam_bs = np.asarray(adcp.get_beam_data(field_name='absolute_backscatter', mask=True), dtype=float)

        mask = np.isfinite(x) & np.isfinite(y)
        if mask.sum() < 2:
            raise ValueError('Not enough finite (x,y) pairs to animate.')
        t, ens, x, y = t[mask], ens[mask], x[mask], y[mask]
        beam_x, beam_y, beam_bs = beam_x[mask], beam_y[mask], beam_bs[mask]
        n_beams = int(beam_x.shape[2])

        fig, ax = PlottingShell.subplots(figheight=figheight, figwidth=figwidth)
        ax.set_xlabel('x (m)')
        ax.set_ylabel('y (m)')
        ax.set_title(f'{adcp.name} vessel track')
        ax.set_aspect('equal', adjustable='datalim')
        # Force plain numeric formatting without scientific notation
        ax.xaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        ax.yaxis.set_major_formatter(ScalarFormatter(useOffset=False))
        ax.ticklabel_format(style='plain', axis='both')

        
        pad = 0.05
        xmin = np.nanmin([np.nanmin(x), np.nanmin(beam_x)])
        xmax = np.nanmax([np.nanmax(x), np.nanmax(beam_x)])
        ymin = np.nanmin([np.nanmin(y), np.nanmin(beam_y)])
        ymax = np.nanmax([np.nanmax(y), np.nanmax(beam_y)])
        xc, yc = 0.5 * (xmin + xmax), 0.5 * (ymin + ymax)
        r = (1 + pad) * max(max((xmax - xmin) * 0.5, 1e-9), max((ymax - ymin) * 0.5, 1e-9))
        ax.set_xlim(xc - r, xc + r)
        ax.set_ylim(yc - r, yc + r)


        (point,) = ax.plot([], [], 'o', ms=3, zorder=3)
        (trail_line,) = ax.plot([], [], '-', lw=1, alpha=0.85, zorder=2)
        ts_text = ax.text(0.02, 0.98, '', transform=ax.transAxes, ha='left', va='top', fontsize=9)

        if isinstance(cmap, str):
            cmap = plt.get_cmap(cmap).copy()
        else:
            cmap = cmap.copy()
        cmap.set_bad('white')

        if vmin is None or vmax is None:
            finite_bs = beam_bs[np.isfinite(beam_bs)]
            if finite_bs.size == 0:
                vmin_calc, vmax_calc = 0.0, 1.0
            else:
                vmin_calc, vmax_calc = np.nanpercentile(finite_bs, [2, 98])
                if not np.isfinite(vmin_calc) or not np.isfinite(vmax_calc) or vmin_calc == vmax_calc:
                    vmin_calc, vmax_calc = np.nanmin(finite_bs), np.nanmax(finite_bs)
            vmin = vmin if vmin is not None else float(vmin_calc)
            vmax = vmax if vmax is not None else float(vmax_calc)
        norm = mcolors.Normalize(vmin=vmin, vmax=vmax)

        beam_lcs = [LineCollection([], cmap=cmap, norm=norm, linewidths=2, zorder=1) for _ in range(n_beams)]
        for lc in beam_lcs:
            ax.add_collection(lc)

        sm = plt.cm.ScalarMappable(norm=norm, cmap=cmap)
        sm.set_array([])
        cbar = fig.colorbar(sm, ax=ax, orientation='vertical', pad=0.02, fraction=0.06)
        cbar.set_label(cax_label)

        def _make_segments_for_beam(bx_b, by_b, bs_b):
            x0, x1 = bx_b[:-1], bx_b[1:]
            y0, y1 = by_b[:-1], by_b[1:]
            c0, c1 = bs_b[:-1], bs_b[1:]
            coord_ok = np.isfinite(x0) & np.isfinite(y0) & np.isfinite(x1) & np.isfinite(y1)
            if not np.any(coord_ok):
                return np.empty((0, 2, 2)), np.empty((0,))
            segs = np.stack([np.stack([x0[coord_ok], y0[coord_ok]], axis=1), np.stack([x1[coord_ok], y1[coord_ok]], axis=1)], axis=1)
            colors = 0.5 * (c0 + c1)[coord_ok]
            return segs, colors

        def _accumulate_segments(i, j0, b):
            segs_list, cols_list = [], []
            for k in range(j0, i + 1):
                segs_k, cols_k = _make_segments_for_beam(beam_x[k, :, b], beam_y[k, :, b], beam_bs[k, :, b])
                if segs_k.size:
                    segs_list.append(segs_k)
                    cols_list.append(cols_k)
            if not segs_list:
                return np.empty((0, 2, 2)), np.empty((0,))
            return np.vstack(segs_list), np.concatenate(cols_list)

        def init():
            point.set_data([], [])
            trail_line.set_data([], [])
            for lc in beam_lcs:
                lc.set_segments([])
                lc.set_array(np.array([]))
            ts_text.set_text('')
            return (point, trail_line, *beam_lcs, ts_text)

        def update(i):
            if show_pos_trail:
                j0_pos = 0 if pos_trail_len is None else max(0, i - pos_trail_len)
                trail_line.set_data(x[j0_pos:i+1], y[j0_pos:i+1])
            else:
                trail_line.set_data([], [])
            point.set_data([x[i]], [y[i]])
            j0_beam = i if not show_beam_trail else (0 if beam_trail_len is None else max(0, i - beam_trail_len))
            for b, lc in enumerate(beam_lcs):
                segs, colors = (_accumulate_segments(i, j0_beam, b) if show_beam_trail else _make_segments_for_beam(beam_x[i, :, b], beam_y[i, :, b], beam_bs[i, :, b]))
                lc.set_segments(segs)
                lc.set_array(np.ma.array(colors, mask=np.isnan(colors)))
            ts = mdates.num2date(mdates.date2num(t[i])).strftime('%Y-%m-%d %H:%M:%S')
            ts_text.set_text(f'{ts} (ens #:{int(ens[i])})')
            return (point, trail_line, *beam_lcs, ts_text)

        ani = FuncAnimation(fig, update, frames=len(t), init_func=init, interval=interval_ms, blit=False)

        if save_gif:
            if gif_name is None:
                gif_name = f"{adcp.name} transect animation.gif"
            ani.save(gif_name, dpi=120, fps=1000/interval_ms)
        
        return fig,ani

    def beam_geometry_animation(self, figheight: float = 6,
                                figwidth: float = 7,
                                interval: int = 50,
                                blit: bool = False,
                                export_gif: bool = False,
                                gif_path: str = None,
                                show_heading: bool = True,
                                heading_length_scale: float = 0.9):
        """
        Animate relative beam geometry in 3D across ensembles.

        Parameters
        ----------
        figheight : float, default 6
            Figure height in inches.
        figwidth : float, default 7
            Figure width in inches.
        interval : int, default 50
            Delay between frames in milliseconds.
        blit : bool, default False
            Whether to use blitting.
        show : bool, default True
            If True, calls ``plt.show()`` at the end.
        export_gif : bool, default False
            If True, exports the animation as a GIF.
        gif_path : str, optional
            Path for saving the GIF. Defaults to "{adcp.name} beam geometry animation.gif".
        show_heading : bool, default True
            If True, draws an arrow at the origin pointing along vessel heading each frame.
        heading_length_scale : float, default 0.9
            Fraction of the global axis limit used for arrow length.

        Returns
        -------
        ani : matplotlib.animation.FuncAnimation
            The animation object.
        ax : matplotlib.axes._subplots.Axes3DSubplot
            The 3D axes used for plotting.
        """

        adcp = self._adcp

        # --- Data ---
        t = np.asarray(adcp.time.ensemble_datetimes)
        ens = np.asarray(adcp.time.ensemble_numbers)

        bx = np.asarray(adcp.geometry.relative_beam_midpoint_positions.x, dtype=float)
        by = np.asarray(adcp.geometry.relative_beam_midpoint_positions.y, dtype=float)
        bz = np.asarray(adcp.geometry.relative_beam_midpoint_positions.z, dtype=float)

        if bx.ndim != 3 or by.ndim != 3 or bz.ndim != 3:
            raise ValueError("relative_beam_midpoint_positions must be shaped (time, bins, beams)")

        n_t, n_bins, n_beams = bx.shape

        # Heading from adcp.position.heading
        heading_deg = np.mod(np.asarray(adcp.position.heading, dtype=float).reshape(-1), 360.0)

        # --- Figure/Axes ---
        fig, ax = PlottingShell.subplots3d(figheight=figheight, figwidth=figwidth)
        ax.set_title(f"{adcp.name} — Relative Beam Geometry (3D)")
        ax.set_xlabel('Δx (m)')
        ax.set_ylabel('Δy (m)')
        ax.set_zlabel('Δz (m)')
        ax.set_box_aspect((1, 1, 1))

        # --- Global limits ---
        finite = np.isfinite(bx) & np.isfinite(by) & np.isfinite(bz)
        if not np.any(finite):
            raise ValueError("No finite beam midpoint coordinates to animate.")
        maxabs = max(np.nanmax(np.abs(bx[finite])),
                     np.nanmax(np.abs(by[finite])),
                     np.nanmax(np.abs(bz[finite])),
                     1e-9)
        L = 1.1 * maxabs
        ax.set_xlim(-L, L)
        ax.set_ylim(-L, L)
        ax.set_zlim(-L, L)

        # --- Artists ---
        colors = plt.rcParams['axes.prop_cycle'].by_key().get('color', ['C0', 'C1', 'C2', 'C3', 'C4', 'C5'])
        beam_lines, head_markers = [], []
        for b in range(n_beams):
            (ln,) = ax.plot([], [], [], '-', lw=2, color=colors[b % len(colors)], label=f'Beam {b + 1}')
            (mk,) = ax.plot([], [], [], 'o', ms=4, color=colors[b % len(colors)])
            beam_lines.append(ln)
            head_markers.append(mk)

        label = ax.text2D(0.02, 0.98, '', transform=ax.transAxes, ha='left', va='top', fontsize=9)

        heading_quiver = None
        if show_heading:
            heading_proxy = Line2D([0], [0], color='k', lw=2)
            handles, texts = ax.get_legend_handles_labels()
            handles.append(heading_proxy)
            texts.append('Vessel heading')
            ax.legend(handles=handles, labels=texts, loc='upper right', fontsize=8)
        else:
            ax.legend(loc='upper right', fontsize=8)

        # --- Helpers ---
        def _format_ts(ts):
            try:
                return ts.strftime('%Y-%m-%d %H:%M:%S')
            except Exception:
                return mdates.num2date(mdates.date2num(ts)).strftime('%Y-%m-%d %H:%M:%S')

        def _draw_heading(i):
            nonlocal heading_quiver
            if not show_heading:
                return
            theta = np.deg2rad(float(heading_deg[i]))
            ux = np.sin(theta)
            uy = np.cos(theta)
            if heading_quiver is not None:
                try:
                    heading_quiver.remove()
                except Exception:
                    pass
            heading_quiver = ax.quiver(0.0, 0.0, 0.0,
                                       ux, uy, 0.0,
                                       length=L * heading_length_scale,
                                       normalize=True,
                                       linewidth=2.0,
                                       color='k')

        # --- Animation callbacks ---
        def init():
            for ln, mk in zip(beam_lines, head_markers):
                ln.set_data_3d([], [], [])
                mk.set_data_3d([], [], [])
            label.set_text('')
            _draw_heading(0)
            if heading_quiver is None:
                return (*beam_lines, *head_markers, label)
            return (*beam_lines, *head_markers, label, heading_quiver)

        def update(i):
            for b, (ln, mk) in enumerate(zip(beam_lines, head_markers)):
                xb = bx[i, :, b]
                yb = by[i, :, b]
                zb = bz[i, :, b]
                m = np.isfinite(xb) & np.isfinite(yb) & np.isfinite(zb)
                if np.any(m):
                    ln.set_data_3d(xb[m], yb[m], zb[m])
                    first_idx = np.argmax(m)
                    mk.set_data_3d([xb[first_idx]], [yb[first_idx]], [zb[first_idx]])
                else:
                    ln.set_data_3d([], [], [])
                    mk.set_data_3d([], [], [])
            _draw_heading(i)
            label.set_text(f"{_format_ts(t[i])}  (#{int(ens[i])})")
            if heading_quiver is None:
                return (*beam_lines, *head_markers, label)
            return (*beam_lines, *head_markers, label, heading_quiver)

        # --- Build animation ---
        ani = FuncAnimation(fig, update, frames=n_t, init_func=init, interval=interval, blit=blit)

        # --- Export GIF ---
        if export_gif:
            if gif_path is None:
                gif_path = f"{adcp.name} beam geometry animation.gif"
            ani.save(gif_path, writer=PillowWriter(fps=max(1, 1000 // interval)))

        return fig,ani
                
    def single_beam_flood_plot(
            self,
            beam: int | str,
            field_name: str = "echo_intensity",
            y_axis_mode: str = "depth",          # "depth", "bin", or "z"
            cmap=None,                            # None → "turbo"
            vmin: float | None = None,
            vmax: float | None = None,
            n_time_ticks: int = 6,
            title: str | None = None,
            mask: bool = True,
            ax=None,
            cax=None,
            *,
            color_scale: str = "linear",          # "linear" or "log"
            cmap_levels: list | tuple | None = None,
            cbar_tick_labels: list[str] | None = None,
            tick_decimals: int = 2,
            x_axis_mode: str = "time",            # "time" or "ensemble"
        ):
        if cmap is None:
            cmap = "turbo"
    
        # --- Beam selection ---
        if isinstance(beam, (str, bytes, bytearray)):
            beam_text = (beam.decode() if isinstance(beam, (bytes, bytearray)) else beam).strip().lower()
        else:
            beam_text = None
        use_mean = beam_text in {"mean", "avg", "average"}
        if not use_mean:
            try:
                ib = int(beam) - 1
            except Exception:
                raise TypeError("beam must be an int 1..n or 'mean'")
            n_beams = int(self._adcp.geometry.n_beams)
            if not (0 <= ib < n_beams):
                raise ValueError(f"beam must be in [1, {n_beams}] or 'mean'")
    
        plt.rcParams.update({"axes.titlesize": 8, "axes.labelsize": 8,
                             "xtick.labelsize": 8, "ytick.labelsize": 8})
    
        A = self._adcp
    
        # --- X axis selection ---
        xmode = str(x_axis_mode).lower()
        t_dt  = np.asarray(A.time.ensemble_datetimes)
        t_num = mdates.date2num(t_dt).astype(float)
        e_num = np.asarray(A.time.ensemble_numbers, dtype=float)
        e_num = e_num - e_num[0] + 1
        
        if xmode == "ensemble":
            x = e_num
            x_label = "Ensemble"
        else:
            x = t_num
            x_label = "Time"
        x0, x1 = float(x[0]), float(x[-1])
    
        # --- Data ---
        beam_data = ma.masked_invalid(A.get_beam_data(field_name=field_name, mask=mask))  # (time,bins,beams)
        data_tb   = ma.masked_invalid(ma.mean(beam_data, axis=2)) if use_mean else ma.masked_invalid(beam_data[:, :, ib])
    
        scale_mode = str(color_scale).lower()
        if scale_mode == "log":
            data_tb = ma.masked_where(~(data_tb > 0), data_tb)
    
        bin_dist_m = np.asarray(A.geometry.bin_midpoint_distances, dtype=float)
        z_rel      = np.asarray(A.geometry.relative_beam_midpoint_positions.z, dtype=float)
        
        # Bottom track envelope
        _bt = getattr(A.bottom_track, "adjusted_range_to_seabed",
                      getattr(A.bottom_track, "range_to_seabed", None))
        bt_top_s = bt_bottom_s = bt_series_s = None
        ymin = None
        if _bt is not None:
            bt_all = -np.asarray(_bt, dtype=float).T
            if np.isfinite(bt_all).any():
                ymin = 1.25 * float(np.nanmin(bt_all))
                if use_mean:
                    bt_top    = np.nanmax(bt_all, axis=1)
                    bt_bottom = np.nanmin(bt_all, axis=1)
                    bt_top_s    = gaussian_filter1d(bt_top,    sigma=1.5, mode="nearest")
                    bt_bottom_s = gaussian_filter1d(bt_bottom, sigma=1.5, mode="nearest")
                else:
                    bt_series   = bt_all[:, ib]
                    bt_series_s = gaussian_filter1d(bt_series, sigma=1.5, mode="nearest")
    
        # --- Color limits ---
        finite_vals = data_tb.compressed()
        if finite_vals.size == 0:
            raise ValueError("No finite data in selected field after masking.")
        if vmin is None:
            vmin = float(np.nanmin(finite_vals))
        if vmax is None:
            vmax = float(np.nanmax(finite_vals))
        if scale_mode == "log":
            if vmin <= 0:
                vmin = float(np.nanmin(finite_vals[finite_vals > 0]))
            if vmax <= vmin:
                vmax = float(np.nextafter(vmin, np.inf))
    
        # --- Honor cmap_levels when choosing norm bounds ---
        vmin_use, vmax_use = vmin, vmax
        if cmap_levels is not None and len(cmap_levels) > 0:
            lv = np.asarray(cmap_levels, dtype=float)
            if scale_mode == "log":
                lv = lv[lv > 0]
            if lv.size > 0:
                low, high = np.nanmin(lv), np.nanmax(lv)
                vmin_use = min(vmin, low)
                vmax_use = max(vmax, high)
        if scale_mode == "log":
            vmin_use = max(vmin_use, np.nextafter(0.0, 1.0))
            if vmax_use <= vmin_use:
                vmax_use = float(np.nextafter(vmin_use, np.inf))
    
        units_map = {
            "echo_intensity": "Counts",
            "correlation_magnitude": "Counts",
            "percent_good": "%",
            "absolute_backscatter": "dB",
            "absolute backscatter": "dB",
            "alpha_s": "dB/km",
            "alpha_w": "dB/km",
            "signal_to_noise_ratio": "",
            "suspended_solids_concentration": "mg/L",
        }
        def pretty(s: str) -> str: return s.replace("_", " ").strip().capitalize()
    
        # --- Y axis extent ---
        ymode = (y_axis_mode or "depth").lower()
        ymin = None
        if ymode == "bin":
            y_label = "Bin distance (m)"
            y1, y0 = float(bin_dist_m[0]), float(bin_dist_m[-1])
            ymin = 0
            ymax = y0
            origin = "upper"
            invert_y = False
        else:
            y_label = "Depth (m)" if ymode == "depth" else "Mean z (m)"
            if use_mean:
                z_mean = np.nanmean(np.nanmean(z_rel, axis=2), axis=0)
            else:
                z_mean = np.nanmean(z_rel[:, :, ib], axis=0)
            if not np.isfinite(z_mean).any():
                z_mean = bin_dist_m
            y0, y1 = float(z_mean[0]), float(z_mean[-1])
            ymax = 0.0
            ymin = 1.25 * float(np.nanmin(z_rel)) if np.isfinite(z_rel).any() else float(-np.nanmax(bin_dist_m))
            origin = "lower"
            invert_y = True
            
        # --- Axes / Layout ---
        if ax is None:
            fig = plt.figure(figsize=(8, 4.5), constrained_layout=True)
            gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[20, 0.6], figure=fig)
            ax = fig.add_subplot(gs[0, 0])
            cax = fig.add_subplot(gs[0, 1]) if cax is None else cax
            fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.02, wspace=0.05, hspace=0.05)
            fig.suptitle(str(title) if title is not None else str(A.name), fontsize=9, fontweight="bold")
        else:
            fig = ax.figure
            if title is not None:
                ax.set_title(str(title), fontsize=9, fontweight="bold")
            if cax is None:
                try:
                    fig.set_constrained_layout(False)
                except Exception:
                    pass
                from mpl_toolkits.axes_grid1 import make_axes_locatable
                divider = make_axes_locatable(ax)
                cax = divider.append_axes("right", size="3%", pad=0.05)
    
        # --- X ticks ---
        xticks = np.linspace(x0, x1, n_time_ticks)
    
        # --- Colormap normalization ---
        norm = LogNorm(vmin=vmin_use, vmax=vmax_use) if scale_mode == "log" else Normalize(vmin=vmin_use, vmax=vmax_use)
    
        # --- Image ---
        im = ax.matshow(
            data_tb.T, origin=origin, aspect="auto",
            extent=[x0, x1, y0, y1], cmap=cmap, norm=norm
        )
    
        # --- Geometry window ---
        
        if ymin is None:
            ymin = 1.25 * float(np.nanmin(z_rel)) if np.isfinite(z_rel).any() else float(-np.nanmax(bin_dist_m))
        ax.set_ylim(ymax, ymin)
        if invert_y:
            ax.invert_yaxis()
    
        # --- Bottom track ---
        if y_axis_mode != "bin":
            if use_mean and (bt_top_s is not None) and (bt_bottom_s is not None):
                ax.fill_between(x, bt_top_s, bt_bottom_s, facecolor="#808080", alpha=0.25, edgecolor="none")
                ax.plot(x, bt_top_s,    linestyle="--", color="k", linewidth=1)
                ax.plot(x, bt_bottom_s, linestyle="--", color="k", linewidth=1)
            elif (bt_series_s is not None):
                ax.plot(x, bt_series_s, linestyle="-", color="k", linewidth=1)
    
        # --- X axis formatting ---
        ax.xaxis.set_ticks_position("bottom")
        ax.xaxis.set_label_position("bottom")
        ax.set_xticks(xticks)
        if xmode == "ensemble":
            ax.set_xticklabels([f"{int(round(v))}" for v in xticks])
        else:
            lbls = []
            for i, xv in enumerate(xticks):
                dt = mdates.num2date(xv)
                lbls.append(dt.strftime("%Y-%m-%d\n%H:%M:%S") if i in (0, len(xticks)-1) else dt.strftime("%H:%M:%S"))
            ax.set_xticklabels(lbls)
        ax.set_xlabel(x_label, fontsize=8)
    
        # --- Y label and beam tag ---
        ax.set_ylabel(y_label, fontsize=8)
        beam_tag = ("Beam mean" if use_mean else f"Beam {ib + 1}")
        ax.text(0.01, 0.02, beam_tag, transform=ax.transAxes,
                ha="left", va="bottom", fontsize=7,
                bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    
        # --- Top distance axis ---
        dist = np.asarray(A.position.distance, dtype=float)
        idx = np.abs(x[:, None] - xticks[None, :]).argmin(axis=0)
        dist_ticks = dist[idx]
        ax_top = ax.twiny()
        ax_top.set_xlim(x0, x1)
        ax_top.set_xticks(xticks)
        ax_top.set_xticklabels([f"{d:.0f}" for d in dist_ticks])
        ax_top.set_xlabel("Distance along transect (m)", fontsize=8)
        ax_top.tick_params(axis="x", labelsize=8)
    
        # --- Colorbar ---
        cblabel = f"{pretty(field_name)}" + (f" ({units_map.get(field_name, '')})" if units_map.get(field_name, "") else "")
    
        if cmap_levels is not None and len(cmap_levels) > 0:
            lv_for_ext = np.asarray(cmap_levels, dtype=float)
            if scale_mode == "log":
                lv_for_ext = lv_for_ext[lv_for_ext > 0]
            has_low_gap  = lv_for_ext.size > 0 and np.nanmin(lv_for_ext) > vmin_use
            has_high_gap = lv_for_ext.size > 0 and np.nanmax(lv_for_ext) < vmax_use
            cbar_extend = "both" if (has_low_gap and has_high_gap) else ("min" if has_low_gap else ("max" if has_high_gap else "neither"))
        else:
            cbar_extend = "neither"
    
        cbar = fig.colorbar(im, cax=cax, orientation="vertical", extend=cbar_extend)
        cbar.set_label(cblabel, fontsize=8)
        cbar.ax.tick_params(labelsize=8)
    
        if cmap_levels is not None:
            levels = list(cmap_levels)
            if scale_mode == "log":
                levels = [v for v in levels if v > 0]
            if len(levels) > 0:
                cbar.set_ticks(levels)
                if cbar_tick_labels is not None:
                    if len(cbar_tick_labels) != len(levels):
                        raise ValueError("cbar_tick_labels must match length of cmap_levels.")
                    cbar.set_ticklabels(list(cbar_tick_labels))
                else:
                    if scale_mode == "log":
                        fmt = f"{{x:.{int(tick_decimals)}f}}"
                        cbar.formatter = FuncFormatter(lambda x, pos: fmt.format(x=x))
                        cbar.update_ticks()
                    else:
                        cbar.set_ticklabels([f"{v:.{int(tick_decimals)}f}" for v in levels])
        else:
            if scale_mode == "log":
                fmt = f"{{x:.{int(tick_decimals)}f}}"
                cbar.formatter = FuncFormatter(lambda x, pos: fmt.format(x=x))
                cbar.update_ticks()
    
        return fig, (ax, cax)

    def four_beam_flood_plot(
            self,
            field_name: str = "echo_intensity",
            y_axis_mode: str = "depth",
            cmap=None,
            vmin: float | None = None,
            vmax: float | None = None,
            n_time_ticks: int = 6,
            title: str | None = None,
            mask: bool = True,
            *,
            color_scale: str = "linear",
            cmap_levels: list | tuple | None = None,
            cbar_tick_labels: list[str] | None = None,
            tick_decimals: int = 2,
            x_axis_mode: str = "time",            # "time" or "ensemble"
        ):
        
        if cmap is None:
            cmap = "turbo"
    
        A = self._adcp
        plt.rcParams.update({"axes.titlesize": 8, "axes.labelsize": 8,
                             "xtick.labelsize": 8, "ytick.labelsize": 8})
    
        # --- X axis selection ---
        xmode = str(x_axis_mode).lower()
        t_dt  = np.asarray(A.time.ensemble_datetimes)
        t_num = mdates.date2num(t_dt).astype(float)
        e_num = np.asarray(A.time.ensemble_numbers, dtype=float)
        e_num = e_num -e_num[0] +1
        if xmode == "ensemble":
            x = e_num
            x_label = "Ensemble"
        else:
            x = t_num
            x_label = "Time"
        x0, x1 = float(x[0]), float(x[-1])
    
        # --- Data ---
        beam_data = ma.masked_invalid(A.get_beam_data(field_name=field_name, mask=mask))
        bin_dist_m = np.asarray(A.geometry.bin_midpoint_distances, dtype=float)
        z_rel = np.asarray(A.geometry.relative_beam_midpoint_positions.z, dtype=float)
        # invert_y = str(A.geometry.beam_facing).lower() == "down"
    
        _bt = getattr(A.bottom_track, "adjusted_range_to_seabed",
                      getattr(A.bottom_track, "range_to_seabed", None))
        if _bt is not None:
            if y_axis_mode == "bin":
                bt_range = np.asarray(_bt, dtype=float).T
            else:
                bt_range = -np.asarray(_bt, dtype=float).T
        else:
            bt_range = np.full((x.size, int(A.geometry.n_beams)), np.nan)

        

        scale_mode = str(color_scale).lower()
        if scale_mode == "log":
            beam_data = ma.masked_where(~(beam_data > 0), beam_data)
    
        # --- Color limits ---
        finite_vals = beam_data.compressed()
        if finite_vals.size == 0:
            raise ValueError("No finite data in selected field after masking.")
        if vmin is None:
            vmin = float(np.nanmin(finite_vals))
        if vmax is None:
            vmax = float(np.nanmax(finite_vals))
        if scale_mode == "log":
            if vmin <= 0:
                vmin = float(np.nanmin(finite_vals[finite_vals > 0]))
            if vmax <= vmin:
                vmax = float(np.nextafter(vmin, np.inf))
    
        vmin_use, vmax_use = vmin, vmax
        if cmap_levels is not None and len(cmap_levels) > 0:
            lv = np.asarray(cmap_levels, dtype=float)
            if scale_mode == "log":
                lv = lv[lv > 0]
            if lv.size > 0:
                vmin_use = min(vmin, np.nanmin(lv))
                vmax_use = max(vmax, np.nanmax(lv))
        if scale_mode == "log":
            vmin_use = max(vmin_use, np.nextafter(0.0, 1.0))
            if vmax_use <= vmin_use:
                vmax_use = float(np.nextafter(vmin_use, np.inf))
    
        units_map = {
            "echo_intensity": "Counts",
            "correlation_magnitude": "Counts",
            "percent_good": "%",
            "absolute_backscatter": "dB",
            "absolute backscatter": "dB",
            "alpha_s": "dB/km",
            "alpha_w": "dB/km",
            "signal_to_noise_ratio": "",
            "suspended_solids_concentration": "mg/L",
        }
        def pretty(s): return s.replace("_", " ").strip().capitalize()
    
        # --- Y label mode ---
        ymode = (y_axis_mode or "depth").lower()
        if ymode == "bin":
            y_label = "Bin distance (m)"
        elif ymode == "z":
            y_label = "Mean z (m)"
        else:
            y_label = "Depth (m)"
    
        # --- Layout ---
        fig = plt.figure(figsize=(8, 6), constrained_layout=True)
        gs = gridspec.GridSpec(nrows=int(A.geometry.n_beams), ncols=2,
                               width_ratios=[20, 0.6], wspace=0.05, figure=fig)
        ax_beams = []
        for i in range(int(A.geometry.n_beams)):
            ax = (fig.add_subplot(gs[i, 0]) if i == 0
                  else fig.add_subplot(gs[i, 0], sharex=ax_beams[0], sharey=ax_beams[0]))
            ax_beams.append(ax)
        ax_cbar = fig.add_subplot(gs[:, 1])
    
        fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.02, wspace=0.05, hspace=0.05)
        fig.suptitle(str(title) if title is not None else str(A.name), fontsize=9, fontweight="bold")
    
        # --- Ticks ---
        xticks = np.linspace(x0, x1, n_time_ticks)
    
        # --- Norm ---
        norm = LogNorm(vmin=vmin_use, vmax=vmax_use) if scale_mode == "log" else Normalize(vmin=vmin_use, vmax=vmax_use)
    
        # --- Plot beams ---
        last_im = None
        ymin = None
        ymax = 0.0
    
        for ib, ax in enumerate(ax_beams):
            data_tb = ma.masked_invalid(beam_data[:, :, ib])
    
            if ymode == "bin":
                y1, y0 = float(bin_dist_m[0]), float(bin_dist_m[-1])
                ymin = 0
                ymax = y0
                origin = "upper"
                invert_y = False
            elif ymode == "z":
                origin = "lower"
                invert_y = True
                ymin = 1.25 * np.nanmin(bt_range) if np.isfinite(bt_range).any() else None
                z_mean = np.nanmean(z_rel[:, :, ib], axis=0)
                if not np.isfinite(z_mean).any():
                    z_mean = bin_dist_m
                y0, y1 = float(z_mean[0]), float(z_mean[-1])
            else:
                origin = "lower"
                invert_y = True
                ymin = 1.25 * float(np.nanmin(z_rel)) if np.isfinite(z_rel).any() else None
                z_mean = np.nanmean(z_rel[:, :, ib], axis=0)
                if not np.isfinite(z_mean).any():
                    z_mean = bin_dist_m
                y0, y1 = float(z_mean[0]), float(z_mean[-1])
    
            last_im = ax.matshow(
                data_tb.T, origin=origin, aspect="auto",
                extent=[x0, x1, y0, y1], cmap=cmap, norm=norm
            )
            if ymin is None:
                ymin = 1.25 * float(np.nanmin(z_rel[:, :, ib])) if np.isfinite(z_rel[:, :, ib]).any() else float(-np.nanmax(bin_dist_m))
            ax.set_ylim(ymax, ymin)
            if invert_y:
                ax.invert_yaxis()

            if ymode == "z" or ymode == "depth":
                y_bt = gaussian_filter1d(bt_range[:, ib], sigma=1.5, mode="nearest")
                ax.plot(x, y_bt, color="k", linewidth=1)
    
            ax.xaxis.set_ticks_position("bottom")
            ax.xaxis.set_label_position("bottom")
            ax.set_xticks(xticks)
            if ib != int(A.geometry.n_beams) - 1:
                ax.tick_params(labelbottom=False)
    
            ax.text(0.01, 0.02, f"Beam {ib+1}", transform=ax.transAxes,
                    ha="left", va="bottom", fontsize=7,
                    bbox=dict(boxstyle="round,pad=0.25", fc="white", ec="none", alpha=0.9))
    
        # bottom labels
        if xmode == "ensemble":
            ax_beams[-1].set_xticklabels([f"{int(round(v))}" for v in xticks])
        else:
            lbls = []
            for i, xv in enumerate(xticks):
                dt = mdates.num2date(xv)
                lbls.append(dt.strftime("%Y-%m-%d\n%H:%M:%S") if i in (0, len(xticks)-1) else dt.strftime("%H:%M:%S"))
            ax_beams[-1].set_xticklabels(lbls)
        ax_beams[-1].set_xlabel(x_label, fontsize=8)
    
        # top distance axis
        dist = np.asarray(A.position.distance, dtype=float)
        idx = np.abs(x[:, None] - xticks[None, :]).argmin(axis=0)
        dist_ticks = dist[idx]
        ax_top = ax_beams[0].twiny()
        ax_top.set_xlim(x0, x1)
        ax_top.set_xticks(xticks)
        ax_top.set_xticklabels([f"{d:.0f}" for d in dist_ticks])
        ax_top.set_xlabel("Distance along transect (m)", fontsize=8)
        ax_top.tick_params(axis="x", labelsize=8)
    
        # --- Colorbar ---
        def pretty(s): return s.replace("_", " ").strip().capitalize()
        units = units_map.get(field_name, "")
        cblabel = f"{pretty(field_name)}" + (f" ({units})" if units else "")
    
        if cmap_levels is not None and len(cmap_levels) > 0:
            lv = np.asarray(cmap_levels, dtype=float)
            if scale_mode == "log":
                lv = lv[lv > 0]
            has_low_gap  = lv.size > 0 and np.nanmin(lv) > vmin_use
            has_high_gap = lv.size > 0 and np.nanmax(lv) < vmax_use
            cbar_extend = "both" if (has_low_gap and has_high_gap) else ("min" if has_low_gap else ("max" if has_high_gap else "neither"))
        else:
            cbar_extend = "neither"
    
        cbar = fig.colorbar(last_im, cax=ax_cbar, orientation="vertical", extend=cbar_extend)
        cbar.set_label(cblabel, fontsize=8)
        cbar.ax.tick_params(labelsize=8)
    
        if cmap_levels is not None:
            levels = list(cmap_levels)
            if scale_mode == "log":
                levels = [v for v in levels if v > 0]
            if len(levels) > 0:
                cbar.set_ticks(levels)
                if cbar_tick_labels is not None:
                    if len(cbar_tick_labels) != len(levels):
                        raise ValueError("cbar_tick_labels must match length of cmap_levels.")
                    cbar.set_ticklabels(list(cbar_tick_labels))
                else:
                    if scale_mode == "log":
                        fmt = f"{{x:.{int(tick_decimals)}f}}"
                        cbar.formatter = FuncFormatter(lambda x, pos: fmt.format(x=x))
                        cbar.update_ticks()
                    else:
                        cbar.set_ticklabels([f"{v:.{int(tick_decimals)}f}" for v in levels])
        else:
            if scale_mode == "log":
                fmt = f"{{x:.{int(tick_decimals)}f}}"
                cbar.formatter = FuncFormatter(lambda x, pos: fmt.format(x=x))
                cbar.update_ticks()
    
        # shared y-label
        fig.canvas.draw()
        left_edges = [ax.get_position().x0 for ax in ax_beams]
        x_left = min(left_edges)
        fig.text(x_left - 0.05, 0.5, y_label, rotation=90, va="center", ha="right",
                 fontsize=8, transform=fig.transFigure)
    
        return fig, (ax_beams, ax_cbar)
      
    def velocity_flood_plot(
            self,
            coord: str = "earth",
            metric: str = "speed",
            field_name: str | None = None,
            y_axis_mode: str = "depth",
            cmap=None,
            vmin: float | None = None,
            vmax: float | None = None,
            n_time_ticks: int = 6,
            title: str | None = None,
            mask: bool = True,
            x_axis_mode: str = "time",            # "time" or "ensemble"
        ):
        
        if cmap is None:
            cmap = "turbo"
    
        # ---------------- Field selection ----------------
        c = str(coord).lower()
        if c in {"instrument", "inst"}:
            c = "instrument"
    
        name_map = {
            None: None,
            "speed": "speed",
            "direction": "direction",
            "error_velocity": "ev",
            "error-velocity": "ev",
            "error velocity": "ev",
            "ev": "ev",
        }
        fn = name_map.get(None if field_name is None else str(field_name).lower())
        m = (fn or str(metric).lower())
        if m not in {"speed", "direction", "ev"}:
            m = "speed"
    
        # ---------------- Data ----------------
        u, v, z, ev, s, d = self._adcp.get_velocity_data(coord_sys=c, mask=mask)  # (time,bins)
        data = {"speed": s, "direction": d, "ev": ev}[m]
        data = ma.masked_invalid(data)
    
        # --- X axis selection ---
        xmode = str(x_axis_mode).lower()
        t_dt  = np.asarray(self._adcp.time.ensemble_datetimes)
        t_num = mdates.date2num(t_dt).astype(float)
        e_num = np.asarray(self._adcp.time.ensemble_numbers, dtype=float)
        e_num = e_num - e_num[0] +1
        if xmode == "ensemble":
            x = e_num
            x_label = "Ensemble"
        else:
            x = t_num
            x_label = "Time"
        x0, x1 = float(x[0]), float(x[-1])
    
        bin_dist_m = np.asarray(self._adcp.geometry.bin_midpoint_distances, dtype=float)
        invert_y   = str(self._adcp.geometry.beam_facing).lower() == "down"
    
        # ---------------- Bottom-track swath ----------------
        _bt = getattr(self._adcp.bottom_track, "adjusted_range_to_seabed",
                      getattr(self._adcp.bottom_track, "range_to_seabed", None))
        bt_top_s = bt_bottom_s = None
        ymin = None
        if _bt is not None:
            bt_all = -np.asarray(_bt, float).T  # (time, beams)
            finite_bt = np.isfinite(bt_all)
            if finite_bt.any():
                bt_top    = np.nanmax(bt_all, axis=1)
                bt_bottom = np.nanmin(bt_all, axis=1)
                def _fill_nan(y):
                    y = np.asarray(y, float)
                    msk = np.isfinite(y)
                    if not msk.any():
                        return y
                    idx = np.arange(y.size)
                    y[~msk] = np.interp(idx[~msk], idx[msk], y[msk])
                    return y
                bt_top_s    = gaussian_filter1d(_fill_nan(bt_top),    sigma=1.5, mode="nearest")
                bt_bottom_s = gaussian_filter1d(_fill_nan(bt_bottom), sigma=1.5, mode="nearest")
                ymin = 1.25 * float(np.nanmin(bt_all[finite_bt]))
    
        # ---------------- Y axis for extent ----------------
        ymode = (y_axis_mode or "depth").lower()
        if ymode == "bin":
            y_label = "Bin distance (m)"
            y1, y0 = float(bin_dist_m[0]), float(bin_dist_m[-1])
            ymin = 0
            ymax = y0
            origin = "upper"
            invert_y = False
        else:
            y_label = "Depth (m)" if ymode == "depth" else "Mean z (m)"
            z_mean = np.nanmean(z, axis=0)
            if not np.isfinite(z_mean).any():
                z_mean = bin_dist_m
            y0 = float(z_mean[0]) if np.isfinite(z_mean[0]) else 0.0
            # y1 = float(z_mean[-1]) if np.isfinite(z_mean[-1]) else -float(np.nanmax(bin_dist_m) or 1.0)
            y1 = -float(np.nanmax(bin_dist_m) or 1.0)
            ymax = 0.0
            if ymin is None:
                ymin = 1.25 * float(np.nanmin(z)) if np.isfinite(z).any() else float(-np.nanmax(bin_dist_m))
            origin = "lower"
            invert_y = True

        # ---------------- Color limits ----------------
        if m == "direction" and vmin is None and vmax is None:
            vmin, vmax = 0.0, 360.0
        else:
            finite_vals = data.compressed()
            if finite_vals.size == 0:
                raise ValueError("No finite data in selected field.")
            if vmin is None:
                vmin = float(np.nanmin(finite_vals))
            if vmax is None:
                vmax = float(np.nanmax(finite_vals))
    
        # ---------------- Layout ----------------
        plt.rcParams.update({"axes.titlesize": 8, "axes.labelsize": 8,
                             "xtick.labelsize": 8, "ytick.labelsize": 8})
        fig = plt.figure(figsize=(8, 4.5), constrained_layout=True)
        gs = gridspec.GridSpec(nrows=1, ncols=2, width_ratios=[20, 0.6])
        ax = fig.add_subplot(gs[0, 0])
        ax_cbar = fig.add_subplot(gs[0, 1])
        fig.set_constrained_layout_pads(w_pad=0.02, h_pad=0.02, wspace=0.05, hspace=0.05)
        fig.suptitle(str(title) if title is not None else str(self._adcp.name),
                     fontsize=9, fontweight="bold")
    
        # X ticks
        xticks = np.linspace(x0, x1, n_time_ticks)
    
        # Image
        im = ax.matshow(
            data.T, origin=origin, aspect="auto",
            extent=[x0, x1, y0, y1], vmin=vmin, vmax=vmax, cmap=cmap
        )
    
        # ---------------- Geometry window ----------------
        # ymax = 0.0
        # if (ymin is None) or (not np.isfinite(ymin)):
        #     z_min = float(np.nanmin(z)) if np.isfinite(z).any() else np.nan
        #     if not np.isfinite(z_min):
        #         z_min = -float(np.nanmax(bin_dist_m) or 1.0)
        #     ymin = 1.25 * z_min
        ax.set_ylim(ymax, ymin)
        if invert_y:
            ax.invert_yaxis()
    
        # ---------------- BT envelope ----------------
        if (bt_top_s is not None) and (bt_bottom_s is not None):
            msk = np.isfinite(bt_top_s) & np.isfinite(bt_bottom_s)
            if msk.any():
                ax.fill_between(x[msk], bt_top_s[msk], bt_bottom_s[msk],
                                facecolor="#808080", alpha=0.25, edgecolor="none")
                ax.plot(x[msk], bt_top_s[msk],    linestyle="--", color="k", linewidth=1)
                ax.plot(x[msk], bt_bottom_s[msk], linestyle="--", color="k", linewidth=1)
    
        # ---------------- Axes formatting ----------------
        ax.xaxis.set_ticks_position("bottom")
        ax.xaxis.set_label_position("bottom")
        ax.set_xticks(xticks)
        if xmode == "ensemble":
            ax.set_xticklabels([f"{int(round(v))}" for v in xticks])
        else:
            lbls = []
            for i, xv in enumerate(xticks):
                dt = mdates.num2date(xv)
                lbls.append(dt.strftime("%Y-%m-%d\n%H:%M:%S") if i in (0, len(xticks)-1) else dt.strftime("%H:%M:%S"))
            ax.set_xticklabels(lbls)
        ax.set_xlabel(x_label, fontsize=8)
        ax.set_ylabel(y_label, fontsize=8)
    
        # Top distance axis aligned to x ticks
        dist = np.asarray(self._adcp.position.distance, dtype=float)
        idx = np.abs(x[:, None] - xticks[None, :]).argmin(axis=0)
        dist_ticks = dist[idx]
        ax_top = ax.twiny()
        ax_top.set_xlim(x0, x1)
        ax_top.set_xticks(xticks)
        ax_top.set_xticklabels([f"{d:.0f}" for d in dist_ticks])
        ax_top.set_xlabel("Distance along transect (m)", fontsize=8)
        ax_top.tick_params(axis="x", labelsize=8)
    
        # Colorbar
        def pretty(s): return s.replace("_", " ").strip().capitalize()
        units_map = {"speed": "m/s", "direction": "deg", "ev": "m/s"}
        label_key = {"speed": "speed", "direction": "direction", "ev": "error velocity"}[m]
        cblabel = f"{pretty(label_key)} ({units_map[m]})"
        cbar = fig.colorbar(im, cax=ax_cbar, orientation="vertical")
        cbar.set_label(cblabel, fontsize=8)
        cbar.ax.tick_params(labelsize=8)
    
        return fig, (ax, ax_cbar)

    def transect_velocities(self,
                            bin_sel=15,
                            every_n=1,
                            scale=0.01,
                            title=None,
                            cmap='viridis',
                            vmin=None,
                            vmax=None,
                            line_width=2.5,
                            line_alpha=0.9,
                            hist_bins=20,
                            figsize=(5, 5)):
        cmap = plt.cm.get_cmap(cmap) if isinstance(cmap, str) else cmap
    
        u,v,z,ev,spd,dirn = self._adcp.get_velocity_data(coord_sys = 'earth', mask = True)
        
        x = np.asarray(self._adcp.position.x_local_m).ravel()
        y = np.asarray(self._adcp.position.y_local_m).ravel()
    
        if isinstance(bin_sel, (int, np.integer)):
            bni = int(bin_sel) - 1
            u_b = np.asarray(u[:, bni]).ravel()
            v_b = np.asarray(v[:, bni]).ravel()
        elif str(bin_sel).lower() in {"mean", "avg"}:
            u_b = np.nanmean(u, axis=1).ravel()
            v_b = np.nanmean(v, axis=1).ravel()
        else:
            raise ValueError("bin_sel must be 'mean' or 1..n_bins")
    
        n = min(x.size, y.size, u_b.size, v_b.size)
        x, y, u_b, v_b = x[:n], y[:n], u_b[:n], v_b[:n]

        X, Y, U, V = x, y, u_b, v_b
        SPD = np.hypot(U, V)
    
        fig, ax = plt.subplots(figsize=figsize)
        norm = Normalize(vmin if vmin is not None else np.nanmin(SPD),
                         vmax if vmax is not None else np.nanmax(SPD))
    
        pts = np.column_stack([X, Y])
        segs = np.stack([pts[:-1], pts[1:]], axis=1)
        lc = LineCollection(segs, cmap=cmap, norm=norm, linewidths=line_width, alpha=line_alpha)
        lc.set_array(SPD[:-1])
        ax.add_collection(lc)
    
        ax.quiver(X, Y, U, V, SPD, cmap=cmap, norm=norm,
                  angles='xy', scale_units='xy', scale=scale,
                  width=0.002, headwidth=3, headlength=4, pivot='tail')
    
        cb = fig.colorbar(lc, ax=ax, pad=0.02, aspect=20, location='right')
        cb.set_label('speed (m/s)')
    
        ax.set_aspect('equal', adjustable='datalim')
        ax.set_xlabel('X (m)')
        ax.set_ylabel('Y (m)')
        ax.set_title(title or f"{getattr(self._adcp, 'name', 'ADCP')} — Feather plot, bin {bin_sel}")
        ax.grid(True, alpha=0.3)
    
        xmin, xmax = np.nanmin(X), np.nanmax(X)
        ymin, ymax = np.nanmin(Y), np.nanmax(Y)
        wx, wy = 0.30 * (xmax - xmin), 0.30 * (ymax - ymin)
    
        counts = {
            'bl': np.count_nonzero((X >= xmin) & (X <= xmin + wx) & (Y >= ymin) & (Y <= ymin + wy)),
            'br': np.count_nonzero((X >= xmax - wx) & (X <= xmax) & (Y >= ymin) & (Y <= ymin + wy)),
            'tl': np.count_nonzero((X >= xmin) & (X <= xmin + wx) & (Y >= ymax - wy) & (Y <= ymax)),
            'tr': np.count_nonzero((X >= xmax - wx) & (X <= xmax) & (Y >= ymax - wy) & (Y <= ymax))
        }
        corner = min(counts, key=counts.get)
    
        rect = [0.0, 0.0, 0.40, 0.18]
        corner_map = {
            'bl': [0.05, 0.08, rect[2], rect[3]],
            'br': [0.55, 0.08, rect[2], rect[3]],
            'tl': [0.05, 0.68, rect[2], rect[3]],
            'tr': [0.55, 0.68, rect[2], rect[3]]
        }
        axin = ax.inset_axes(corner_map[corner], transform=ax.transAxes)
        axin.hist(SPD, bins=hist_bins, color='black', edgecolor='white', linewidth=0.3)
        axin.set_xlabel('Speed (m/s)', fontsize=6, labelpad=2)
        axin.tick_params(axis='y', left=False, right=False, labelleft=False)
        axin.tick_params(axis='x', bottom=True, top=False, labelbottom=True, labelsize=5)
        axin.spines['top'].set_visible(False)
        axin.spines['right'].set_visible(False)
        axin.spines['left'].set_visible(False)
        axin.patch.set_alpha(0.0)
    
        return fig, ax
    

if __name__ == "__main__":
    pass