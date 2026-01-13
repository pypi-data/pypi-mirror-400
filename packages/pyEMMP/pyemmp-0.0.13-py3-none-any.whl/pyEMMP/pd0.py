from pathlib import Path
import numpy as np
from dataclasses import dataclass
import re
from datetime import datetime
import struct
from typing import List, Dict, Any, Tuple, Literal

from ._pd0_fields import Pd0Formats, FieldDef
from .utils import Utils, Constants

@dataclass
class _DataCodeID:
    data_id_code: int

    def __repr__(self):
        return f"_DataCodeID(data_id_code={self.data_id_code})"

def clean_field_name(name: str) -> str:
    name = name.replace(" ", "_")
    name = re.sub(r'[^0-9a-zA-Z_]', '', name)
    if name and name[0].isdigit():
        name = "_" + name
    return name.lower()

@dataclass
class BasePd0Section:
    def __init__(self, field_defs: List[FieldDef], values_dict: Dict[str, any] = None):
        self._field_name_map = {}
        values_dict = values_dict or {}

        for field_def in field_defs:
            original_name = field_def.name
            clean_name = clean_field_name(original_name)
            self._field_name_map[clean_name] = original_name
            value = values_dict.get(original_name, np.nan)
            setattr(self, clean_name, value)

    def to_dict(self):
        """Returns a dict of clean_name → value"""
        return {attr: getattr(self, attr) for attr in self._field_name_map}

    def to_original_dict(self):
        """Returns a dict of original field name → value"""
        return {original: getattr(self, clean) for clean, original in self._field_name_map.items()}

class Header(BasePd0Section):
    def __init__(self, values_dict: Dict[str, any] = None):
        super().__init__(Pd0Formats.ensemble_header, values_dict)
        self.velocity_id: _DataCodeID = _DataCodeID(np.nan)
        self.id_code_4: _DataCodeID = _DataCodeID(np.nan)
        self.id_code_5: _DataCodeID = _DataCodeID(np.nan) 
        self.id_code_6: _DataCodeID = _DataCodeID(np.nan) 
        self.address_offset: List[int] = []

    def __repr__(self):
        text = f"Header:\n"
        for field, value in self.__dict__.items():
            if not field.startswith('_'):
                text += f"  {field}: {value}\n"
        return text

class FixedLeader(BasePd0Section):
    def __init__(self, values_dict: Dict[str, any] = None):
        super().__init__(Pd0Formats.fixed_leader, values_dict)

    def __repr__(self):
        text = f"FixedLeader:\n"
        for field, value in self.__dict__.items():
            if not field.startswith('_'):
                text += f"  {field}: {value}\n"
        return text

class VariableLeader(BasePd0Section):
    def __init__(self, values_dict: Dict[str, any] = None):
        super().__init__(Pd0Formats.variable_leader, values_dict)

    def __repr__(self):
        text = f"VariableLeader:\n"
        for field, value in self.__dict__.items():
            if not field.startswith('_'):
                text += f"  {field}: {value}\n"
        return text

class BottomTrack(BasePd0Section):
    def __init__(self, values_dict: Dict[str, any] = None):
        super().__init__(Pd0Formats.bottom_track, values_dict)

    def __repr__(self):
        text = f"BottomTrack:\n"
        for field, value in self.__dict__.items():
            if not field.startswith('_'):
                text += f"  {field}: {value}\n"
        return text

class SystemConfiguration:
    def __init__(self):
        self.beam_facing = None
        self.xdcr_hd = None
        self.sensor_config = None
        self.beam_pattern = None
        self.frequency = None
        self.janus_config = None
        self.beam_angle = None

class CoordTransform:
    def __init__(self):
        self.frame = None
        self.tilts_used = None
        self.three_beam = None
        self.bin_mapping = None
        self.raw_bytes = None

class Pd0Decoder:
    def __init__(self, filepath: str | Path, cfg: Dict[str, Any], scan: bool | bool = False) -> None:
        """
        Initialize the Pd0Decoder with the path to the binary PD0 file.

        Parameters:
            file_path (str): Path to the binary PD0 file.
            cfg (dict) : dictionary of pd0 config params 
            scan (bool) : if True, only fixed leaders are read and report generated. 
        """
        self.filepath = Utils._validate_file_path(filepath, Constants._PD0_SUFFIX)
        self.cfg = cfg
        self.name = self.cfg.get('name', self.filepath.stem)
        self.filesize = self.filepath.stat().st_size
        self.fobject = open(self.filepath, 'rb')
        # read the first ensemble
        self._first_ensemble_pos = self._find_first_ensemble()
        self._first_ensemble_header = self._get_single_header(offset = self._first_ensemble_pos) # read the header of the first ensemble

        # # extract metadata from first header
        self._n_data_types = self._first_ensemble_header.n_data_types
        self._n_bytes_in_ensemble = self._first_ensemble_header.n_bytes_in_ensemble
        self._n_ensembles = self.filesize // self._n_bytes_in_ensemble - 3
        
        # get all ensemble headers
        self.ensemble_headers = self._get_ensemble_headers()
        
        #update n_ensembles 
        self._n_ensembles = len(self.ensemble_headers)
        
        #get fixed and variable leader data 
        self.fixed_leaders = self._get_fixed_leaders()
        self.variable_leaders = self._get_variable_leaders()   
        
    def close(self):
        self.fobject.close()
        
    def get_fixed_leader_attr(self, attr: str) -> np.ndarray:
        """
        Retrieve a specific attribute from each fixed leader.
    
        Parameters
        ----------
        attr : str
            Name of the attribute to retrieve.
    
        Returns
        -------
        np.ndarray
            Array of attribute values from all ensembles.
    
        Raises
        ------
        AttributeError
            If the attribute does not exist on the fixed leader object.
        """
        if not hasattr(self.fixed_leaders[0], attr):
            raise AttributeError(f"'{type(self.fixed_leaders[0]).__name__}' has no attribute '{attr}'")
    
        return np.array([getattr(f, attr) for f in self.fixed_leaders])
            
    def get_variable_leader_attr(self, attr: str) -> np.ndarray:
        """
        Retrieve a specific attribute from each variable leader.
    
        Parameters
        ----------
        attr : str
            Name of the attribute to retrieve.
    
        Returns
        -------
        np.ndarray
            Array of attribute values from all ensembles.
    
        Raises
        ------
        AttributeError
            If the attribute does not exist on the variable leader object.
        """
        if not hasattr(self.variable_leaders[0], attr):
            raise AttributeError(f"'{type(self.variable_leader[0]).__name__}' has no attribute '{attr}'")
    
        vals = []
        for v in self.variable_leaders:
            vals.append(getattr(v, attr))
    
        return np.array(vals)
        

    def _find_first_ensemble(self, max_iter: int = 100) -> int:
        """
        Find the next ensemble start position in the PD0 file.
        Parameters:
        ----------
        length : int
            The number of bytes to search for a valid ensemble in it.
        max_iter : int
            The maximum number of iterations to search for a valid ensemble.
        Returns:
        -------
        int
            The start position of the next ensemble in the file.
        """
        self.fobject.seek(0)
        valid = False
        pos = 0
        iter_count = 0
        
        while not valid and iter_count < max_iter:
            self.fobject.seek(pos)
            try:
                header = self._decode_fields(Pd0Formats.ensemble_header, 0)
            except Exception as e:
                self.status = 1
                break
                
            if header is not None:
                self.fobject.seek(0)  # Reset to the beginning of the file
                return pos
            else:
                iter_count += 1
        if iter_count >= max_iter:
            self.status = 1
        
    
    def _get_single_header(self, offset: int = 0) -> Header:
        """
        Retrieve the header for a single ensemble at the specified byte offset.
    
        Parameters
        ----------
        offset : int, optional
            Byte offset in the file to seek to before reading the header (default is 0).
    
        Returns
        -------
        Header
            Parsed ensemble header at the specified file offset.
        """
        self.fobject.seek(offset)
        header = Header(self._decode_fields(Pd0Formats.ensemble_header, 0))
        n_data_types = header.n_data_types if header.n_data_types is not np.nan else 0
        address_offsets = []
        for i in range(n_data_types):
            value, _ = self._decode_field(Pd0Formats.address_offsets[0])
            address_offsets.append(value)
        header.address_offset = address_offsets 
        return header

    def _get_ensemble_headers(self) -> List[Header]:
        """
        Get the fixed leader data from the PD0 file.

        Returns:
            List[FixedLeader]: A list of FixedLeader objects for each ensemble.
        """
        self.fobject.seek(0)
        headers = []
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) 
            self.fobject.seek(pos)
            #fixed_leader = FixedLeader(self._decode_fields(Pd0Formats.ensemble_header))
            try:
                header = Header(self._decode_fields(Pd0Formats.ensemble_header))
            except:
                self.status = 1
                break
            n_data_types = header.n_data_types if header.n_data_types is not np.nan else 0
            address_offsets = []
            

            if n_data_types:
                for i in range(n_data_types):
                    value, _ = self._decode_field(Pd0Formats.address_offsets[0])
                    address_offsets.append(value)
                header.address_offset = address_offsets 
    
    
                if n_data_types >0:
                    headers.append(header)
                
        return headers
    
    def _get_fixed_leaders(self) -> List[FixedLeader]:
        """
        Get the fixed leader data from the PD0 file.

        Returns:
            List[FixedLeader]: A list of FixedLeader objects for each ensemble.
        """
        self.fobject.seek(0)
        fixed_leaders = []
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + self.ensemble_headers[i].address_offset[0]
            self.fobject.seek(pos)
            try:
                fixed_leader = FixedLeader(self._decode_fields(Pd0Formats.fixed_leader))
                fixed_leader.system_configuration = self._decode_system_configuration(fixed_leader.system_configuration)
                fixed_leader.coordinate_transform = self._decode_EX(fixed_leader.coordinate_transform_ex)
            except:
                self.status = 1
                break

            fixed_leaders.append(fixed_leader)
        return fixed_leaders

    def _get_variable_leaders(self) -> List[VariableLeader]:
        """
        Get the variable leader data from all ensembles in the PD0 file.

        Returns:
            List[VariableLeader]: A list of VariableLeader objects for each ensemble.
        """
        self.fobject.seek(0)
        variable_leaders = []
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + self.ensemble_headers[i].address_offset[1]
            self.fobject.seek(pos)
            try:
                variable_leader = VariableLeader(self._decode_fields(Pd0Formats.variable_leader))
            except Exception as e:
                self.status = 1
                break
 
            variable_leaders.append(variable_leader)
        return variable_leaders
    

    def _decode_field(self, field: FieldDef) -> Tuple[Any, bytes]:
        fmtstr = f"{field.endian}{field.fmt}"
        nbytes = struct.calcsize(fmtstr)
        field_bytes = self.fobject.read(nbytes)
        if len(field_bytes) < nbytes:
            value = None
        else:
            value = struct.unpack(fmtstr, field_bytes)[0]
        if not field.decode:
            value = field_bytes
        return value, nbytes

    def _decode_fields(self, fields: List[FieldDef], initial_offset: int = 0) -> Dict[str, Any]:
        """
        Decode fields from the binary file based on the provided field definitions.

        Parameters:
            fields (List[FieldDef]): List of FieldDef objects defining the fields to decode.
            initial_offset (int): Initial offset in the file to start decoding.

        Returns:
            Tuple[Dict[str, Any], int]: A dictionary of decoded field values and the total bytes read.
        """
        result = {}
        offset = initial_offset
        if offset > 0:
            self.fobject.read(offset)
        for field in fields:
            value, nbytes = self._decode_field(field)
            result[field.name] = value
            offset += nbytes
        return result

    def _get_LE_bit_string(self, byte: bytes) -> str:
        """
        make a bit string from little endian byte

        Args:
            byte: a byte
        Returns:
            a string of ones and zeros, the bits in the byte
        """
        # surely there's a better way to do this!!
        bits = ""
        for i in [7, 6, 5, 4, 3, 2, 1, 0]:  # Little Endian
            if (byte >> i) & 1:
                bits += "1"
            else:
                bits += "0"
        return bits


    def _decode_system_configuration(self, syscfg: str) -> SystemConfiguration:
        """
        determine the system configuration parameters from 2-byte hex

        Args:
            syscfg: 2-byte hex string 
        Returns:
            SystemConfiguration: a SystemConfiguration object with the decoded parameters
        """
        try:
            LSB = self._get_LE_bit_string(syscfg[0])
            MSB = self._get_LE_bit_string(syscfg[1])
        except:
            return SystemConfiguration()  # return empty object if decoding fails
        # determine system configuration
        # key for Beam facing
        beam_facing = {'0': 'DOWN', '1': 'UP'}

        # key for XDCR attached
        xdcr_att = {'0': 'NOT ATTACHED', '1': 'ATTACHED'}

        # key for sensor configuration
        sensor_cfg = {'00': '#1', '01': '#2', '10': '#3'}

        # key for beam pattern
        beam_pat = {'0': 'CONCAVE', '1': 'CONVEX'}

        # key for system frequencies
        sys_freq = {'000': '75-kHz', '001': '150-kHz', '010': '300-kHz', '011': '600-kHz', '100': '1200-kHz', '101': '2400-kHz'}

        # determine system configuration from MSB
        janus = {'0100': '4-BM', '0101': '5-BM (DEMOD)', '1111': '5-BM (2 DEMD)'}

        beam_angle = {'00': '15E', '01': '20E', '10': '30E', '11': 'OTHER'}

        system_configuration = SystemConfiguration()
        system_configuration.beam_facing = beam_facing[LSB[0]]
        system_configuration.xdcr_hd = xdcr_att[LSB[1]]
        system_configuration.sensor_config = sensor_cfg[LSB[2:4]]
        system_configuration.beam_pattern = beam_pat[LSB[4]]
        system_configuration.frequency = sys_freq[LSB[5:]]
        try:
            system_configuration.janus_config = janus[MSB[:4]]
        except:
            system_configuration.janus_config = 'UNKNOWN'
        system_configuration.beam_angle = beam_angle[MSB[-2:]]
        
        return system_configuration 
    
    
    def _decode_EX(self,ex_bytes: bytes) -> CoordTransform:
        
        """Decode PD0 Variable Leader EX / Coord Transform."""
        if len(ex_bytes) < 1:
            raise ValueError("need at least 1 byte")
        low = ex_bytes[0]                   # PD0 is LSB then MSB
        transform = (low >> 3) & 0b11       # bits 4..3 → xx
        frame = {0b00:"beam", 0b01:"instrument", 0b10:"ship", 0b11:"earth"}[transform]
        
        coord_trans = CoordTransform()
        coord_trans.frame = frame
        coord_trans.tilts_used = bool((low >> 2) & 1)
        coord_trans.three_beam = bool((low >> 1) & 1)
        coord_trans.bin_mapping = bool(low & 1)
        coord_trans.raw_bytes = ex_bytes
        
        return coord_trans 

    
    def get_datetimes(self) -> List[VariableLeader]:
        """
        Get the variable leader data from the PD0 file.

        Returns:
            List[VariableLeader]: A list of VariableLeader objects for each ensemble.
        """
        self.fobject.seek(0)
        datetimes = []
        first_offset = np.sum([Pd0Formats.variable_leader[i].nbytes for i in [0, 1]])
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + self.ensemble_headers[i].address_offset[1] + first_offset
            self.fobject.seek(pos)
            try:
                data = self._decode_fields(Pd0Formats.variable_leader[2:9])
            except Exception as e:
                self.status = 1
                break

            if any(d is None for d in data.values()):
                self._n_ensembles = i
                self._approximate_n_ensembles = False
                break
            _ = np.sum([Pd0Formats.variable_leader[i].nbytes for i in range(9,37)])
            _ = self.fobject.read(_)
            century = str(self._decode_fields([Pd0Formats.variable_leader[37]]))
            if not century in ['19','20']: century = '20'
            year = int(century + str(data["RTC YEAR {TS}"]))
            month = int(data["RTC MONTH {TS}"])
            day = int(data["RTC DAY {TS}"])
            hour = int(data["RTC HOUR {TS}"])
            minute = int(data["RTC MINUTE {TS}"])
            second = int(data["RTC SECOND {TS}"])
            hundredth = int(data["RTC HUNDREDTHS {TS}"])
            dt = datetime(year, month, day, hour, minute, second, hundredth * 10000)
            datetimes.append(dt)
        datetimes = np.array(datetimes)
        return datetimes

    def get_velocity(self) -> np.ndarray:
        self.fobject.seek(0)
        data = []
        break_flag = False
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + self.ensemble_headers[i].address_offset[2]
            self.fobject.seek(pos)
            self._decode_field(Pd0Formats.data_ID_code[0])
            ens_data = []
            for _ in range(self.fixed_leaders[i].number_of_cells_wn):
                cell_data = []
                for __ in range(self.fixed_leaders[i].number_of_beams):
                    value, _ = self._decode_field(Pd0Formats.velocity[0])
                    if value is None:
                        break_flag = True
                        break
                    if value == -32768:
                        value = np.nan
                    cell_data.append(value)
                ens_data.append(cell_data)
            if break_flag:
                self._n_ensembles = i
                self._approximate_n_ensembles = False
                break
            data.append(ens_data)
        return np.array(data)

    def _get_variable(self, name: Literal["echo_intensity", "correlation_magnitude", "percent_good"]) -> np.ndarray:
        """
        Wrapper function to get variable data from the PD0 file.
        """
        address_offsets = {
            "correlation_magnitude": self.ensemble_headers[0].address_offset[3],
            "echo_intensity": self.ensemble_headers[0].address_offset[4],
            "percent_good": self.ensemble_headers[0].address_offset[5]
        }

        labels = {
            "correlation_magnitude": "Correlation Magnitude",
            "echo_intensity": "Echo Intensity",
            "percent_good": "Percent Good"
        }


        field_map = {
            "echo_intensity": Pd0Formats.echo_intensity[0],
            "correlation_magnitude": Pd0Formats.corr_mag[0],
            "percent_good": Pd0Formats.pct_good[0]
        }
        
        self.fobject.seek(0)
        data = []
        break_flag = False
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + address_offsets[name]
            self.fobject.seek(pos)
            self._decode_field(Pd0Formats.data_ID_code[0])
            ens_data = []
            for _ in range(self.fixed_leaders[i].number_of_cells_wn):
                cell_data = []
                for __ in range(self.fixed_leaders[i].number_of_beams):
                    value, _ = self._decode_field(field_map[name])
                    #value, _ = self._decode_field(Pd0Formats.variable[0])
                    if value is None:
                        break_flag = True
                        break
                    cell_data.append(value)
                ens_data.append(cell_data)
            if break_flag:
                self._n_ensembles = i
                self._approximate_n_ensembles = False
                break
            data.append(ens_data)
        return np.array(data)

    def get_echo_intensity(self) -> np.ndarray:
        """
        Get the echo intensity data from the PD0 file.

        Returns:
            np.ndarray: A 2D array of echo intensity values for each ensemble and cell.
        """
        return self._get_variable("echo_intensity")
    
    def get_correlation_magnitude(self) -> np.ndarray:
        """
        Get the correlation magnitude data from the PD0 file.

        Returns:
            np.ndarray: A 2D array of correlation magnitude values for each ensemble and cell.
        """
        return self._get_variable("correlation_magnitude")
    
    def get_percent_good(self) -> np.ndarray:
        """
        Get the percent good data from the PD0 file.

        Returns:
            np.ndarray: A 2D array of percent good values for each ensemble and cell.
        """
        return self._get_variable("percent_good")

    def get_bottom_track(self) -> List[BottomTrack]:
        """
        Get the bottom track data from the PD0 file.

        Returns:
            List[BottomTrack]: A list of BottomTrack objects for each ensemble.
        """
        if self._n_data_types < 7:
            return None
        self.fobject.seek(0)
        bottom_tracks = []
        for i in range(self._n_ensembles):
            pos = self._first_ensemble_pos + i * (self._n_bytes_in_ensemble + 2) + self.ensemble_headers[i].address_offset[6]
            self.fobject.seek(pos)
            try:
                bottom_track = BottomTrack(self._decode_fields(Pd0Formats.bottom_track))
            except Exception as e:
                self.status = 1
                break
            bottom_tracks.append(bottom_track)
        return bottom_tracks

    
    def instrument_summary(self, out_path: str = "adcp_summary.txt", return_dict: bool = False):
        """
        Write a human-readable instrument summary from PD0 metadata.
    
        Parameters
        ----------
        out_path : str, default "adcp_summary.txt"
            File path to write the summary text report.
        return_dict : bool, default False
            If True, also return the summary as a dict.
    
        Returns
        -------
        dict or None
            Summary dictionary if return_dict is True, else None.
        """
        import numpy as np
        from datetime import datetime
    
        # Fixed leader and ensemble count
        fixed_leader = self.fixed_leaders[0]
        n_ens = getattr(self, "_n_ensembles", len(self.ensemble_headers))
    
        # Datetimes: prefer helper if present
        datetimes = self.get_datetimes()
        # Timing stats
        dt_diffs = np.diff(datetimes)
        duration = datetimes[-1] - datetimes[0]
        total_seconds = int(duration.total_seconds())
        days, rem = divmod(total_seconds, 86400)
        hours, rem = divmod(rem, 3600)
        minutes, seconds = divmod(rem, 60)
    
        out = {
            "Ensemble Timing and General Metadata": {
                "Number of Ensembles": n_ens,
                "First Ensemble DateTime (UTC)": datetimes[0],
                "Last Ensemble DateTime (UTC)": datetimes[-1],
                "Duration (d:h:m:s)": f"{days}:{hours:02}:{minutes:02}:{seconds:02}",
                "Mean Ensemble Duration (s)": round(np.nanmean(dt_diffs).total_seconds(), 3),
                "Median Ensemble Duration (s)": round(np.nanmedian(dt_diffs).total_seconds(), 3),
                "Minimum Ensemble Duration (s)": round(np.nanmin(dt_diffs).total_seconds(), 3),
                "Maximum Ensemble Duration (s)": round(np.nanmax(dt_diffs).total_seconds(), 3),
            },
            "Beam Configuration and System Geometry": {
                "Beam Facing": fixed_leader.system_configuration.beam_facing,
                "Beam Pattern": fixed_leader.system_configuration.beam_pattern,
                "Beam Angle (°)": fixed_leader.system_configuration.beam_angle,
                "Beam Angle (Redundant °)": getattr(fixed_leader, "beam_angle", None),
                "Janus Config": fixed_leader.system_configuration.janus_config,
                "Frequency": fixed_leader.system_configuration.frequency,
            },
            "Measurement Configuration and Resolution": {
                "Number of Beams": fixed_leader.number_of_beams,
                "Number of Cells": fixed_leader.number_of_cells_wn,
                "Pings per Ensemble": fixed_leader.pings_per_ensemble_wp,
                "Cell Size (cm)": fixed_leader.depth_cell_length_ws,
                "Blank After Transmit (cm)": fixed_leader.blank_after_transmit_wf,
                "Bin 1 Distance (cm)": fixed_leader.bin_1_distance,
                "Lag Length": fixed_leader.lag_length,
                "Transmit Lag Distance (cm)": fixed_leader.transmit_lag_distance,
                "Transmit Pulse Length Based on Water Track": fixed_leader.xmit_pulse_length_based_on_wt,
                "Ref Layer Start/End Cell": fixed_leader.starting_cell_wp_ref_layer_average_wl_ending_cell,
            },
            "Timing Parameters": {
                "TPP Minutes": fixed_leader.tpp_minutes,
                "TPP Seconds": fixed_leader.tpp_seconds,
                "TPP Hundredths": fixed_leader.tpp_hundredths_tp,
            },
            "Quality Control and Filtering Thresholds": {
                "Low Correlation Threshold": fixed_leader.low_corr_thresh_wc,
                "Number of Code Repetitions": fixed_leader.no_code_reps,
                "Minimum Good Data (%)": fixed_leader.gd_minimum_wg,
                "Max Error Velocity Threshold (mm/s)": fixed_leader.error_velocity_maximum_we,
                "False Target Threshold (dB)": fixed_leader.false_target_thresh_wa,
            },
            "Coordinate Transforms and Orientation": {
                "Coordinate Transform Flags": fixed_leader.coordinate_transform_ex,
                "Heading Alignment (°)": fixed_leader.heading_alignment_ea,
                "Heading Bias (°)": fixed_leader.heading_bias_eb,
            },
            "Sensor and Source Configuration": {
                "Sensor Source Flags": fixed_leader.sensor_source_ez,
                "Sensors Available Flags": fixed_leader.sensors_available,
            },
            "Firmware and Hardware Metadata": {
                "CPU Firmware Version": fixed_leader.cpu_fw_ver,
                "CPU Firmware Revision": fixed_leader.cpu_fw_rev,
                "CPU Board Serial Number": fixed_leader.cpu_board_serial_number,
                "Instrument Serial Number": fixed_leader.instrument_serial_number,
                "System Bandwidth (kHz)": fixed_leader.system_bandwidth_wb,
                "System Power (W)": fixed_leader.system_power_cq,
            },
            "Flags and Placeholders": {
                "Realsim Flag": fixed_leader.realsim_flag,
                "Spare1": fixed_leader.spare1,
                "Spare2": fixed_leader.spare2,
            },
        }
    
        # Text report
        lines = []
        for section, items in out.items():
            lines.append(section.upper())
            lines.append("=" * len(section))
            max_key_len = max(len(k) for k in items)
            for key, value in items.items():
                key_str = key.ljust(max_key_len + 4)
                lines.append(f"  {key_str}: {value}")
            lines.append("")
        report = "_br_".join(lines)
    
        if return_dict:
            return out
        else:
            return report
