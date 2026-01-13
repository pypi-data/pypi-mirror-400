
"""
XMLUtils — single-XML initializer with clear, minimal helpers.

Design:
- Initialize once from a project XML path.
- Provide small, predictable helper finders for @id/@type/@name.
- Resolve a Survey by id or name (id wins).
- Build config dictionaries for ADCP, OBS, and WaterSample.
- Public entrypoint: get_cfgs_from_survey(survey_name, survey_id, instrument_type).

Notes:
- This is a readable baseline. Field coverage mirrors your prior implementation
  where relevant but avoids hidden globals and ambiguous lookups.
- Extend builders in-place when you need more fields.
"""

from __future__ import annotations
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Optional, List, Dict, Any

from .utils import Constants  # expects FAR_PAST/FUTURE and LOW/HIGH sentinels
from .utils_shapefile import ShapefileLayer
from .utils_crs import CRSHelper

class XMLUtils:
    """Parse a project XML and build instrument configuration dicts."""

    # ----------------------
    # Construction
    # ----------------------
    def __init__(self, xml_file: str):
        """
        Load and parse a single project XML file.

        Parameters
        ----------
        xml_file : str
            Filesystem path to the project XML.
        """
        if isinstance(xml_file, str):
            try:
                self.tree = ET.parse(xml_file)
                self.project: ET.Element = self.tree.getroot()
            except:
                self.project = ET.fromstring(xml_file)
        else:
            self.project = xml_file  # assume already an ET.Element
        # Lazy-built map for parent lookup; populated on first use
        self._parent_map: Optional[dict[ET.Element, ET.Element]] = None

    # ----------------------
    # Public API
    # ----------------------
    def get_cfgs_from_survey(
        self,
        survey_name: Optional[str],
        survey_id: Optional[str],
        instrument_type: str,
    ) -> List[Dict[str, Any]]:
        """
        Get configuration dictionaries for all instruments of a type within a survey.

        Parameters
        ----------
        survey_name : Optional[str]
            Survey @name value. Used if survey_id is not provided or not found.
        survey_id : Optional[str]
            Survey @id value. Takes precedence over survey_name when provided.
        instrument_type : str
            Instrument type tag stored in the XML @type attribute.
            Examples: "VesselMountedADCP", "OBSVerticalProfile", "WaterSample".

        Returns
        -------
        List[Dict[str, Any]]
            List of configuration dictionaries, one per instrument element found.
            Empty list if the survey cannot be resolved or no instruments match.
        """
        survey = self._resolve_survey(survey_name=survey_name, survey_id=survey_id)
        if survey is None:
            return []

        # Collect instruments under the resolved Survey
        elems = self.find_elements(type_name=instrument_type, root=survey)

        cfgs: List[Dict[str, Any]] = []
        for el in elems:
            inst_id = el.attrib.get("id")
            if not inst_id:
                # Skip instruments without an id because builders expect one
                continue
            if instrument_type == "VesselMountedADCP":
                cfgs.append(self.CreateADCPDict(inst_id, add_ssc=True))
            elif instrument_type == "OBSVerticalProfile":
                cfgs.append(self.CreateOBSDict(inst_id, add_ssc=True))
            elif instrument_type == "WaterSample":
                cfgs.append(self.CreateWaterSampleDict(inst_id))
            else:
                # Unknown instrument: return minimal identity info
                cfgs.append({
                    "type": el.attrib.get("type"),
                    "id": inst_id,
                    "name": el.attrib.get("name"),
                })
        return cfgs

    # ----------------------
    # Element finders
    # ----------------------
    def find_element(
        self,
        elem_id: Optional[str] = None,
        _type: Optional[str] = None,
        name: Optional[str] = None,
        root: Optional[ET.Element] = None,
    ) -> Optional[ET.Element]:
        """
        Find the first element matching any provided attribute constraints.

        Parameters
        ----------
        elem_id : Optional[str]
            Match @id.
        _type : Optional[str]
            Match @type.
        name : Optional[str]
            Match @name.
        root : Optional[ET.Element]
            Search root. Defaults to the project root.

        Returns
        -------
        Optional[ET.Element]
            First matching element or None if no match.
        """
        root = self.project if root is None else root
        for el in root.findall(".//*"):
            if elem_id is not None and el.attrib.get("id") != elem_id:
                continue
            if _type is not None and el.attrib.get("type") != _type:
                continue
            if name is not None and el.attrib.get("name") != name:
                continue
            return el
        return None

    def find_elements(
        self,
        type_name: Optional[str] = None,
        elem_id: Optional[str] = None,
        name: Optional[str] = None,
        tag: str = "*",
        root: Optional[ET.Element] = None,
    ) -> List[ET.Element]:
        """
        Find all elements meeting optional attribute constraints.

        Parameters
        ----------
        type_name : Optional[str]
            Match @type.
        elem_id : Optional[str]
            Match @id.
        name : Optional[str]
            Match @name.
        tag : str
            XML tag name filter. Defaults to '*' (any tag).
        root : Optional[ET.Element]
            Search root. Defaults to the project root.

        Returns
        -------
        List[ET.Element]
            All matching elements (possibly empty).
        """
        root = self.project if root is None else root
        matches: List[ET.Element] = []
        for el in root.findall(f".//{tag}"):
            if type_name is not None and el.attrib.get("type") != type_name:
                continue
            if elem_id is not None and el.attrib.get("id") != elem_id:
                continue
            if name is not None and el.attrib.get("name") != name:
                continue
            matches.append(el)
        return matches

    # ----------------------
    # Survey resolution
    # ----------------------
    def _resolve_survey(
        self,
        survey_name: Optional[str],
        survey_id: Optional[str],
    ) -> Optional[ET.Element]:
        """
        Resolve a Survey element by id or name. Id is preferred.

        Returns
        -------
        Optional[ET.Element]
            The Survey element, or None if not found.
        """
        # Prefer id lookup if provided
        if survey_id:
            el = self.project.find(f".//Survey[@id='{survey_id}']")
            if el is not None:
                return el
        # Fallback to name lookup
        if survey_name:
            el = self.project.find(f".//Survey[@name='{survey_name}']")
            if el is not None:
                return el
        return None

    def _parent(self, el: ET.Element) -> Optional[ET.Element]:
        """
        Return parent of the given element using a cached map.
        """
        if self._parent_map is None:
            # Build a dict mapping each child to its parent
            self._parent_map = {child: parent for parent in self.project.iter() for child in parent}
        return self._parent_map.get(el)

    # ----------------------
    # Value helpers
    # ----------------------
    @staticmethod
    def _text(root: Optional[ET.Element], tag: str, default: Optional[str]) -> Optional[str]:
        """
        Get .text for a child tag or return default if missing/blank.
        """
        if root is None:
            return default
        n = root.find(tag)
        if n is None or n.text is None or n.text.strip() == "":
            return default
        return n.text

    @staticmethod
    def _get_value(element: Optional[ET.Element], tag: str, default):
        """
        Safe accessor for a child tag's .text with fallback default.
        """
        if element is None:
            return default
        node = element.find(tag)
        if node is None or node.text is None or node.text.strip() == "":
            return default
        return node.text

    # ----------------------
    # Config builders
    # ----------------------
    def CreateADCPDict(self, instrument_id: str, add_ssc: bool = True) -> Dict[str, Any]:
        """
        Build an ADCP configuration dictionary for a given instrument id.

        Pulls water/sediment context from the parent Survey.
        Returns a dictionary with masking limits, georeferencing params,
        position CSV mapping, water/sediment properties, absolute backscatter
        parameters, and SSC model parameters.

        Raises
        ------
        ValueError
            If the ADCP instrument id is not found.
        """
        instrument = self.find_element(elem_id=instrument_id, _type="VesselMountedADCP")
        if instrument is None:
            raise ValueError(f"ADCP id={instrument_id} not found")

        # Survey-scoped context
        parent = self._parent(instrument)
        water = parent.find("Water") if parent is not None else None
        sediment = parent.find("Sediment") if parent is not None else None

        # Settings / EPSG
        settings = self.project.find("Settings")
        epsg = self._text(settings, "EPSG", "4326")

        # Required structure under <Pd0>
        pd0 = instrument.find("Pd0")
        configuration = pd0.find("Configuration") if pd0 is not None else None
        crp_offset = configuration.find("CRPOffset") if configuration is not None else None
        rssis = configuration.find("RSSICoefficients") if configuration is not None else None
        transect_shift = configuration.find("TransectShift") if configuration is not None else None
        masking = pd0.find("Masking") if pd0 is not None else None
        position = instrument.find("PositionData")

        # Paths and identifiers
        filename = self._text(pd0, "Path", "")
        name = instrument.attrib.get("name", Path(filename).stem if filename else "ADCP")
        sscmodelid = self._text(pd0, "SSCModelID", None)

        # Helper to read "Enabled" flags safely
        def _enabled(node: Optional[ET.Element]) -> bool:
            return node is not None and node.attrib.get("Enabled", "").lower() == "true"

        # Individual mask nodes (some may be missing)
        maskEchoIntensity = masking.find("MaskEchoIntensity") if masking is not None else None
        maskPercentGood = masking.find("MaskPercentGood") if masking is not None else None
        maskCorrelationMagnitude = masking.find("MaskCorrelationMagnitude") if masking is not None else None
        maskCurrentSpeed = masking.find("MaskCurrentSpeed") if masking is not None else None
        maskErrorVelocity = masking.find("MaskErrorVelocity") if masking is not None else None
        maskAbsoluteBackscatter = masking.find("MaskAbsoluteBackscatter") if masking is not None else None
        backgroundSSC = masking.find("BackgroundSSC") if masking is not None else None

        # Percent good
        pg_min = float(self._get_value(maskPercentGood, "Min", 0)) if _enabled(maskPercentGood) else 0

        # Current speed limits
        if _enabled(maskCurrentSpeed):
            vel_min = float(self._get_value(maskCurrentSpeed, "Min", Constants._LOW_NUMBER))
            vel_max = float(self._get_value(maskCurrentSpeed, "Max", Constants._HIGH_NUMBER))
        else:
            vel_min, vel_max = Constants._LOW_NUMBER, Constants._HIGH_NUMBER

        # Echo intensity limits
        if _enabled(maskEchoIntensity):
            echo_min = float(self._get_value(maskEchoIntensity, "Min", 0))
            echo_max = float(self._get_value(maskEchoIntensity, "Max", 255))
        else:
            echo_min, echo_max = 0, 255

        # Correlation magnitude limits
        if _enabled(maskCorrelationMagnitude):
            cmn = self._get_value(maskCorrelationMagnitude, "Min", None)
            cmx = self._get_value(maskCorrelationMagnitude, "Max", None)
            cormag_min = float(cmn) if cmn is not None else None
            cormag_max = float(cmx) if cmx is not None else None
        else:
            cormag_min = cormag_max = None

        # Absolute backscatter bounds
        if _enabled(maskAbsoluteBackscatter):
            absback_min = float(self._get_value(maskAbsoluteBackscatter, "Min", 0))
            absback_max = float(self._get_value(maskAbsoluteBackscatter, "Max", 255))
        else:
            absback_min, absback_max = 0, 255

        # Error velocity cap
        if _enabled(maskErrorVelocity):
            err_vel_max = self._get_value(maskErrorVelocity, "Max", "auto")
            if err_vel_max != "auto":
                err_vel_max = float(err_vel_max)
        else:
            err_vel_max = "auto"

        # Time window and ensemble filters
        start_datetime = self._get_value(masking, "StartDateTime", None)
        end_datetime = self._get_value(masking, "EndDateTime", None)
        fge = self._get_value(masking, "FirstEnsemble", None)
        first_good_ensemble = int(fge) if fge is not None else None
        lge = self._get_value(masking, "LastEnsemble", None)
        last_good_ensemble = int(lge) if lge is not None else None

        background_ssc_mode = self._get_value(backgroundSSC, "Mode", "fixed").lower()
        background_ssc_value = float(self._get_value(backgroundSSC, "Value", 0)) if backgroundSSC is not None else 0

        # Configuration and coordinate parameters
        magnetic_declination = float(self._get_value(configuration, "MagneticDeclination", 0))
        velocity_average_window_len = float(self._get_value(configuration, "EnsembleAverageInterval", 5))
        utc_offset = self._get_value(configuration, "UTCOffset", None)
        utc_offset = float(utc_offset) if utc_offset is not None else None
        crp_rotation_angle = float(self._get_value(configuration, "RotationAngle", 0.0))
        crp_offset_x = float(self._get_value(crp_offset, "X", 0))
        crp_offset_y = float(self._get_value(crp_offset, "Y", 0))
        crp_offset_z = float(self._get_value(crp_offset, "Z", 0))
        transect_shift_x = float(self._get_value(transect_shift, "X", 0))
        transect_shift_y = float(self._get_value(transect_shift, "Y", 0))
        transect_shift_z = float(self._get_value(transect_shift, "Z", 0))
        transect_shift_t = float(self._get_value(transect_shift, "T", 0))

        # Position file mapping for track CSVs
        pos_cfg = {
            'filename': self._get_value(position, "Path", ""),
            'epsg': epsg,
            'X_mode': "Variable", 'Y_mode': "Variable",
            'Depth_mode': "Constant", 'Pitch_mode': "Constant", 'Roll_mode': "Constant",
            'Heading_mode': "Variable", 'DateTime_mode': "Variable",
            'X_value': self._get_value(position, "XColumn", "Longitude"),
            'Y_value': self._get_value(position, "YColumn", "Latitude"),
            'Depth_value': 0, 'Pitch_value': 0, 'Roll_value': 0,
            'Heading_value': self._get_value(position, "HeadingColumn", "Course"),
            'DateTime_value': self._get_value(position, "DateTimeColumn", "DateTime"),
            'header': int(self._get_value(position, "Header", 0)),
            'sep': self._get_value(position, "Sep", ","),
        }

        # Water and sediment properties (optional)
        water_properties = {}
        if water is not None:
            water_properties = {
                'density': float(water.attrib.get("Density", "1023")),
                'salinity': float(water.attrib.get("Salinity", "32")),
                'temperature': float(water.attrib["Temperature"]) if "Temperature" in water.attrib and water.attrib["Temperature"].strip() != "" else None,
                'pH': float(water.attrib.get("pH", "8.1")),
            }

        sediment_properties = {}
        if sediment is not None:
            sediment_properties = {
                'particle_density': float(sediment.attrib.get("Density", "2650")),
                'particle_diameter': float(sediment.attrib.get("Diameter", "2.5e-4")),
            }

        # Absolute backscatter calibration params
        C = float(self._get_value(configuration, "C", -139.0))
        P_dbw = float(self._get_value(configuration, "Pdbw", 9))
        E_r = float(self._get_value(rssis, "Er", 39))
        rssi_beam1 = float(self._get_value(rssis, "Beam1", 0.41))
        rssi_beam2 = float(self._get_value(rssis, "Beam2", 0.41))
        rssi_beam3 = float(self._get_value(rssis, "Beam3", 0.41))
        rssi_beam4 = float(self._get_value(rssis, "Beam4", 0.41))
        abs_params = {
            'C': C, 'P_dbw': P_dbw, 'E_r': E_r,
            'rssi_beam1': rssi_beam1, 'rssi_beam2': rssi_beam2,
            'rssi_beam3': rssi_beam3, 'rssi_beam4': rssi_beam4
        }

        # SSC model parameters (from linked model id if available)
        if add_ssc and sscmodelid:
            sscmodel = self.find_element(elem_id=sscmodelid)
            A = float(self._get_value(sscmodel, "A", None)) 
            B = float(self._get_value(sscmodel, "B", None)) 
        else:
            A, B = None, None
        ssc_params = {'A': A, 'B': B}

        # Final structured configuration
        return {
            'filename': filename,
            'name': name,
            'pg_min': pg_min,
            'vel_min': vel_min, 'vel_max': vel_max,
            'echo_min': echo_min, 'echo_max': echo_max,
            'cormag_min': cormag_min, 'cormag_max': cormag_max,
            'err_vel_max': err_vel_max,
            'start_datetime': start_datetime, 'end_datetime': end_datetime,
            'first_good_ensemble': first_good_ensemble, 'last_good_ensemble': last_good_ensemble,
            'abs_min': absback_min, 'abs_max': absback_max,
            'background_ssc_mode': background_ssc_mode, 'background_ssc': background_ssc_value,
            'magnetic_declination': magnetic_declination, 'velocity_average_window_len': velocity_average_window_len, 'utc_offset': utc_offset,
            'crp_rotation_angle': crp_rotation_angle,
            'crp_offset_x': crp_offset_x, 'crp_offset_y': crp_offset_y, 'crp_offset_z': crp_offset_z,
            'transect_shift_x': transect_shift_x, 'transect_shift_y': transect_shift_y,
            'transect_shift_z': transect_shift_z, 'transect_shift_t': transect_shift_t,
            'pos_cfg': pos_cfg,
            'water_properties': water_properties,
            'sediment_properties': sediment_properties,
            'abs_params': abs_params,
            'ssc_params': ssc_params,
        }

    def CreateOBSDict(self, instrument_id: str, add_ssc: bool = True) -> Dict[str, Any]:
        """
        Build an OBS vertical profile configuration dictionary.

        Includes file mapping, optional SSC model parameters, and masking ranges.

        Raises
        ------
        ValueError
            If the OBS instrument id is not found.
        """
        instrument = self.find_element(elem_id=instrument_id, _type="OBSVerticalProfile")
        if instrument is None:
            raise ValueError(f"OBS id={instrument_id} not found")

        # EPSG (optional, for downstream georeferencing)
        settings = self.project.find("Settings")
        epsg = self._text(settings, "EPSG", "4326")

        # File mapping
        name = instrument.attrib.get("name", "OBSProfile")
        fileinfo = instrument.find("FileInfo")
        filename = self._text(fileinfo, "Path", "")
        header = int(self._text(fileinfo, "Header", "0"))
        sep = self._text(fileinfo, "Sep", ",")
        date_col = self._text(fileinfo, "DateColumn", "Date")
        time_col = self._text(fileinfo, "TimeColumn", "Time")
        depth_col = self._text(fileinfo, "DepthColumn", "Depth")
        ntu_col = self._text(fileinfo, "NTUColumn", "NTU")
        sscmodelid = self._text(fileinfo, "SSCModelID", None)

        # SSC model
        if add_ssc and sscmodelid:
            sscmodel = self.find_element(elem_id=sscmodelid, _type="NTU2SSC")
            A = float(self._get_value(sscmodel, "A", None))
            B = float(self._get_value(sscmodel, "B", None)) 
        else:
            A, B = None, None
        ssc_params = {'A': A, 'B': B}

        # Masking ranges
        masking = instrument.find("Masking")
        maskDateTime = masking.find("MaskDateTime") if masking is not None else None
        if maskDateTime is not None and maskDateTime.attrib.get("Enabled", "").lower() == "true":
            start_datetime = self._get_value(maskDateTime, "Start", Constants._FAR_PAST_DATETIME)
            end_datetime = self._get_value(maskDateTime, "End", Constants._FAR_FUTURE_DATETIME)
        else:
            start_datetime = Constants._FAR_PAST_DATETIME
            end_datetime = Constants._FAR_FUTURE_DATETIME

        maskDepth = masking.find("MaskDepth") if masking is not None else None
        if maskDepth is not None and maskDepth.attrib.get("Enabled", "").lower() == "true":
            maskDepthMin = float(self._get_value(maskDepth, "Min", Constants._LOW_NUMBER))
            maskDepthMax = float(self._get_value(maskDepth, "Max", Constants._HIGH_NUMBER))
        else:
            maskDepthMin = Constants._LOW_NUMBER
            maskDepthMax = Constants._HIGH_NUMBER

        maskNTU = masking.find("MaskNTU") if masking is not None else None
        if maskNTU is not None and maskNTU.attrib.get("Enabled", "").lower() == "true":
            maskNTUMin = float(self._get_value(maskNTU, "Min", Constants._LOW_NUMBER))
            maskNTUMax = float(self._get_value(maskNTU, "Max", Constants._HIGH_NUMBER))
        else:
            maskNTUMin = Constants._LOW_NUMBER
            maskNTUMax = Constants._HIGH_NUMBER

        return {
            'name': name,
            'epsg': epsg,
            'filename': filename,
            'header': header,
            'sep': sep,
            'date_col': date_col,
            'time_col': time_col,
            'depth_col': depth_col,
            'ntu_col': ntu_col,
            'ssc_params': ssc_params,
            'start_datetime': start_datetime,
            'end_datetime': end_datetime,
            'depthMin': maskDepthMin,
            'depthMax': maskDepthMax,
            'ntuMin': maskNTUMin,
            'ntuMax': maskNTUMax
        }

    def CreateWaterSampleDict(self, instrument_id: str) -> Dict[str, Any]:
        """
        Build a Water Sample configuration dictionary.

        Supports both external file mapping and inline <Sample> entries.
        Returns basic masks and an embedded 'samples' section listing inline points.

        Raises
        ------
        ValueError
            If the WaterSample instrument id is not found.
        """
        instrument = self.find_element(elem_id=instrument_id, _type="WaterSample")
        if instrument is None:
            raise ValueError(f"WaterSample id={instrument_id} not found")

        fileinfo = instrument.find("FileInfo") or instrument

        def first_text(elem: Optional[ET.Element], tags: List[str], default: str) -> str:
            """Return first present non-blank text among candidate tags."""
            if elem is None:
                return default
            for t in tags:
                v = elem.find(t)
                if v is not None and v.text and v.text.strip():
                    return v.text
            return default

        # File mapping
        filename = first_text(fileinfo, ["Path", "File", "Filename"], "")
        header = int(first_text(fileinfo, ["Header"], "0"))
        sep = first_text(fileinfo, ["Sep", "Delimiter"], ",")
        datetime_col = first_text(fileinfo, ["DateTimeColumn", "DatetimeColumn"], None)
        date_col = first_text(fileinfo, ["DateColumn"], None)
        time_col = first_text(fileinfo, ["TimeColumn"], None)
        depth_col = first_text(fileinfo, ["DepthColumn", "ZColumn"], None)
        ssc_col = first_text(fileinfo, ["SSCColumn", "TSSColumn", "ConcentrationColumn"], "SSC")

        # Masking
        masking = instrument.find("Masking")
        if masking is not None:
            mdt = masking.find("MaskDateTime")
            if mdt is not None and mdt.attrib.get("Enabled", "").lower() == "true":
                start_datetime = self._get_value(mdt, "Start", Constants._FAR_PAST_DATETIME)
                end_datetime = self._get_value(mdt, "End", Constants._FAR_FUTURE_DATETIME)
            else:
                start_datetime = Constants._FAR_PAST_DATETIME
                end_datetime = Constants._FAR_FUTURE_DATETIME

            md = masking.find("MaskDepth")
            if md is not None and md.attrib.get("Enabled", "").lower() == "true":
                depth_min = float(self._get_value(md, "Min", Constants._LOW_NUMBER))
                depth_max = float(self._get_value(md, "Max", Constants._HIGH_NUMBER))
            else:
                depth_min = Constants._LOW_NUMBER
                depth_max = Constants._HIGH_NUMBER

            ms = masking.find("MaskSSC") or masking.find("MaskConcentration")
            if ms is not None and ms.attrib.get("Enabled", "").lower() == "true":
                ssc_min = float(self._get_value(ms, "Min", Constants._LOW_NUMBER))
                ssc_max = float(self._get_value(ms, "Max", Constants._HIGH_NUMBER))
            else:
                ssc_min = Constants._LOW_NUMBER
                ssc_max = Constants._HIGH_NUMBER
        else:
            # No masking block: fall back to global sentinels
            start_datetime = Constants._FAR_PAST_DATETIME
            end_datetime = Constants._FAR_FUTURE_DATETIME
            depth_min = Constants._LOW_NUMBER
            depth_max = Constants._HIGH_NUMBER
            ssc_min = Constants._LOW_NUMBER
            ssc_max = Constants._HIGH_NUMBER

        # Inline <Sample/> parsing → raw list (leave pandas to caller)
        records: List[Dict[str, Any]] = []
        for s in instrument.findall("Sample"):
            dt_txt = s.attrib.get("DateTime")
            depth_txt = s.attrib.get("Depth")
            ssc_txt = s.attrib.get("SSC")
            try:
                depth_val = float(depth_txt) if depth_txt is not None else None
            except ValueError:
                depth_val = None
            try:
                ssc_val = float(ssc_txt) if ssc_txt is not None else None
            except ValueError:
                ssc_val = None
            records.append({
                "sample": s.attrib.get("Sample"),
                "datetime": dt_txt,
                "depth": depth_val,
                "ssc": ssc_val,
                "notes": s.attrib.get("Notes", ""),
            })

        return {
            "filename": filename,
            "header": header,
            "sep": sep,
            "datetime_col": datetime_col,
            "date_col": date_col,
            "time_col": time_col,
            "depth_col": depth_col,
            "ssc_col": ssc_col,
            "start_datetime": start_datetime,
            "end_datetime": end_datetime,
            "depthMin": depth_min,
            "depthMax": depth_max,
            "sscMin": ssc_min,
            "sscMax": ssc_max,
            "samples": {
                "records": records,
                "count": len(records),
                "units": {"depth": "m", "ssc": "mg/L"},
                "source": "inline" if records else "file",
            },
        }

    def parse_settings(self) -> Dict[str, Any]:
        """
        Parse the <Settings> and <MapSettings> sections.
        Returns
        -------
        Dict[str, Any]
            Dictionary of settings with sensible defaults.
        """
        settings = self.find_element(elem_id="1", _type="Settings")
        mapSettings = self.find_element(elem_id="2", _type="MapSettings")

        # Settings
        name = self._get_value(settings, "Name", "Unnamed Project")
        directory = self._get_value(settings, "Directory", ".")
        epsg = self._get_value(settings, "EPSG", "4326")
        description = self._get_value(settings, "Description", "")
        settings_dict = {
            "name": name,
            "directory": directory,
            "epsg": epsg,
            "description": description,
        }
        crs_helper = CRSHelper(epsg)

        # MapSettings
        # Map2D
        map2D = mapSettings.find("Map2D")
        map3D = mapSettings.find("Map3D")
        mapShapefiles = mapSettings.find("MapShapefiles")
        
        map2D_dict = self.__parse_map_settings(map2D)
        map2D_dict["transect_line_width"] = int(self._get_value(map2D, "TransectLineWidth", "2"))
        bin_method = self._get_value(map2D, "VerticalAggBinItem", "bin").lower()
        bin_value = str(self._get_value(map2D, "VerticalAggBinTarget", "Mean")).lower()
        if bin_value != "mean":
            bin_value = float(bin_value)
        beam_value = str(self._get_value(map2D, "VerticalAggBeam", "Mean")).lower()
        if beam_value != "mean":
            beam_value = int(beam_value)
        map2D_dict["vertical_agg"] = {
            "method": bin_method,
            "target": bin_value,
            "beam": beam_value
        }
        
        map3D_dict = self.__parse_map_settings(map3D)
        map3D_dict["z_scale"] = float(self._get_value(map3D, "ZScale", "3.0"))

        shapefiles = self.find_elements(tag="Shapefile", root=mapShapefiles)
        shp_list = []
        for shp in shapefiles:
            if shp.attrib.get("visible", "").lower() != "true":
                continue
            shp_path = shp.find("Path").text
            shp_kind = shp.find("Kind").text
            shp_label_text = self._get_value(shp, "LabelText", None)
            shp_label_fontsize = int(self._get_value(shp, "LabelFontSize", 8))
            shp_label_color = self._get_value(shp, "LabelColor", "#000000")
            shp_label_ha = self._get_value(shp, "LabelHA", "left").lower()
            shp_label_va = self._get_value(shp, "LabelVA", "center").lower()
            shp_label_offset_points_x = float(self._get_value(shp, "LabelOffsetPointsX", 0.0))
            shp_label_offset_points_y = float(self._get_value(shp, "LabelOffsetPointsY", 0.0))
            shp_label_offset_points = (shp_label_offset_points_x, shp_label_offset_points_y)
            shp_label_offset_data_x = float(self._get_value(shp, "LabelOffsetDataX", 0.0))
            shp_label_offset_data_y = float(self._get_value(shp, "LabelOffsetDataY", 0.0))
            shp_label_offset_data = (shp_label_offset_data_x, shp_label_offset_data_y)
            if shp_kind.lower() == "polygon":
                poly_edgecolor = self._get_value(shp, "PolyEdgeColor", "#000000")
                poly_linewidth = float(self._get_value(shp, "PolyLineWidth", 0.8))
                poly_facecolor = self._get_value(shp, "PolyFaceColor", "none")
                poly_alpha = float(self._get_value(shp, "PolyAlpha", 1.0))
                shp_object = ShapefileLayer(path=shp_path, kind=shp_kind, crs_helper=crs_helper,
                                            poly_edgecolor=poly_edgecolor, poly_linewidth=poly_linewidth, poly_facecolor=poly_facecolor, alpha=poly_alpha,
                                            label_text=shp_label_text, label_fontsize=shp_label_fontsize, label_color=shp_label_color, label_ha=shp_label_ha, label_va=shp_label_va, label_offset_pts=shp_label_offset_points, label_offset_data=shp_label_offset_data)
                shp_list.append(shp_object)
            elif shp_kind.lower() == "point":
                point_color = self._get_value(shp, "PointColor", "#000000")
                point_marker = self._get_value(shp, "PointMarker", "o")
                point_markersize = float(self._get_value(shp, "PointMarkerSize", 12))
                point_alpha = float(self._get_value(shp, "PointAlpha", 1.0))
                shp_object = ShapefileLayer(path=shp_path, kind=shp_kind, crs_helper=crs_helper,
                                            point_color=point_color, point_marker=point_marker, point_markersize=point_markersize, alpha=point_alpha,
                                            label_text=shp_label_text, label_fontsize=shp_label_fontsize, label_color=shp_label_color, label_ha=shp_label_ha, label_va=shp_label_va, label_offset_pts=shp_label_offset_points, label_offset_data=shp_label_offset_data)
                shp_list.append(shp_object)
            elif shp_kind.lower() == "line":
                line_color = self._get_value(shp, "LineColor", "#000000")
                line_width = float(self._get_value(shp, "LineLineWidth", 1.0))
                line_alpha = float(self._get_value(shp, "LineAlpha", 1.0))
                shp_object = ShapefileLayer(path=shp_path, kind=shp_kind, crs_helper=crs_helper,
                                            line_color=line_color, line_width=line_width, alpha=line_alpha,
                                            label_text=shp_label_text, label_fontsize=shp_label_fontsize, label_color=shp_label_color, label_ha=shp_label_ha, label_va=shp_label_va, label_offset_pts=shp_label_offset_points, label_offset_data=shp_label_offset_data)
                shp_list.append(shp_object)
        map_settings_dict = {
            "Map2D": map2D_dict,
            "Map3D": map3D_dict,
            "Shapefiles": shp_list
        }

        return settings_dict, map_settings_dict
        
    def __parse_map_settings(self, map: ET.Element) -> Dict[str, Any]:
        """
        Helper to parse common settings between Map2D and Map3D settings.
        """
        if map is None:
            return {}
        vmin = self._get_value(map, "vmin", None)
        vmax = self._get_value(map, "vmax", None)
        if vmin is not None:
            try:
                vmin = float(vmin)
            except ValueError:
                vmin = None
        if vmax is not None:
            try:
                vmax = float(vmax)
            except ValueError:
                vmax = None
        surveys = map.find("Surveys")
        surveys_list = surveys.findall("Survey")
        survey_ids = []
        for s in surveys_list:
            sid = s.text
            if sid:
                survey_ids.append(sid)
        return {
            "bgcolor": self._get_value(map, "BackgroundColor", "#000000"),
            "field_name": self._get_value(map, "FieldName", "Echo Intensity"),
            "cmap": self._get_value(map, "ColorMap", "jet"),
            "vmin": vmin,
            "vmax": vmax,
            "pad_deg": float(self._get_value(map, "Padding", "0.03")),
            "grid_lines": int(self._get_value(map, "NGridLines", "5")),
            "grid_opacity": float(self._get_value(map, "GridOpacity", "0.2")),
            "grid_color": self._get_value(map, "GridColor", "#000000").lower(),
            "grid_width": int(self._get_value(map, "GridWidth", "1")),
            "bgcolor": self._get_value(map, "BackgroundColor", "#FFFFFF").lower(),
            "axis_ticks": int(self._get_value(map, "NAxisTicks", "5")),
            "tick_fontsize": int(self._get_value(map, "TickFontSize", "10")),
            "tick_decimals": int(self._get_value(map, "TickNDecimals", "2")),
            "axis_label_fontsize": int(self._get_value(map, "AxisLabelFontSize", "12")),
            "axis_label_color": self._get_value(map, "AxisLabelColor", "#000000").lower(),
            "hover_fontsize": int(self._get_value(map, "HoverFontSize", "10")),
            "surveys": survey_ids
        }

    def project_info(self) -> Dict[str, Any]:
        """
        Aggregate overview of the project.
    
        Returns
        -------
        dict with:
          - "surveys": list of {id, name, counts, total_instruments}
            * counts: per-@type tally within each Survey
          - "models": {
                "BKS2SSC": {"count": N, "items": [...]},
                "NTU2SSC": {"count": N, "items": [...]},
                "MTModels": {"count": N, "items": [...]},
                "HDModels": {"count": N, "items": [...]},
            }
        """
        overview: Dict[str, Any] = {"surveys": [], "models": {}}
    
        # 1) Surveys + instrument counts
        surveys = list(self.project.findall(".//Survey"))
        for idx, s in enumerate(surveys, start=1):
            sid = s.attrib.get("id")
            sname = s.attrib.get("name")
            counts: Dict[str, int] = {}
            for el in s.findall(".//*[@type]"):
                t = el.attrib.get("type")
                counts[t] = counts.get(t, 0) + 1
            overview["surveys"].append({
                "id": sid,
                "name": sname,
                "counts": counts,
                "total_instruments": sum(counts.values()),
                "index": idx,
            })
    
        # 2) SSC models (BKS2SSC, NTU2SSC)
        def _ssc_models(tname: str) -> Dict[str, Any]:
            items = []
            for m in self.find_elements(type_name=tname):
                items.append({
                    "id": m.attrib.get("id"),
                    "name": m.attrib.get("name"),
                    "mode": self._get_value(m, "Mode", None),
                    "A": _to_float(self._get_value(m, "A", None)),
                    "B": _to_float(self._get_value(m, "B", None)),
                })
            return {"count": len(items), "items": items}
    
        # 3) MTModels and HDModels
        def _generic_models(tname: str) -> Dict[str, Any]:
            items = []
            for m in self.find_elements(type_name=tname):
                # Capture shallow fields so this remains schema-agnostic
                d = {"id": m.attrib.get("id"), "name": m.attrib.get("name")}
                # Common optional children (silently ignore if absent)
                for tag in ("Path", "ConfigFile", "Version", "Description"):
                    val = self._get_value(m, tag, None)
                    if val is not None:
                        d[tag] = val
                items.append(d)
            return {"count": len(items), "items": items}
    
        def _to_float(x):
            try:
                return float(x) if x is not None else None
            except Exception:
                return None
    
        overview["models"]["BKS2SSC"] = _ssc_models("BKS2SSC")
        overview["models"]["NTU2SSC"] = _ssc_models("NTU2SSC")
        overview["models"]["MTModels"] = _generic_models("MTModel")
        overview["models"]["HDModels"] = _generic_models("HDModel")
    
        return overview

    def get_cfg_by_instrument(
        self,
        instrument_type: str,
        instrument_name: Optional[str] = None,
        instrument_id: Optional[str] = None,
        add_ssc: bool = True,
    ) -> Optional[Dict[str, Any]]:
        """
        Return one configuration dict for a specific instrument.
    
        Parameters
        ----------
        instrument_type : str
            Expected @type of the instrument ("VesselMountedADCP", "OBSVerticalProfile", "WaterSample", ...).
        instrument_name : Optional[str]
            Match @name (used if id not found).
        instrument_id : Optional[str]
            Match @id (preferred).
        add_ssc : bool
            Pass-through for ADCP/OBS builders.
    
        Resolution
        ----------
        - Constrain search by `instrument_type`.
        - Prefer `instrument_id`; fall back to `instrument_name`.
        - Dispatch to the correct builder based on `instrument_type`.
    
        Returns
        -------
        Optional[Dict[str, Any]]
            Config dict or None if not found.
        """
        if not instrument_id and not instrument_name:
            return None
    
        el = None
        if instrument_id:
            el = self.find_element(elem_id=instrument_id, _type=instrument_type)
        if el is None and instrument_name:
            el = self.find_element(name=instrument_name, _type=instrument_type)
        if el is None:
            return None
    
        inst_id = el.attrib.get("id")
        if not inst_id:
            return None
    
        if instrument_type == "VesselMountedADCP":
            return self.CreateADCPDict(inst_id, add_ssc=add_ssc)
        if instrument_type == "OBSVerticalProfile":
            return self.CreateOBSDict(inst_id, add_ssc=add_ssc)
        if instrument_type == "WaterSample":
            return self.CreateWaterSampleDict(inst_id)
    
        # Generic fallback for other types
        cfg: Dict[str, Any] = {
            "type": instrument_type,
            "id": inst_id,
            "name": el.attrib.get("name"),
        }
        for tag in ("Path", "File", "Filename"):
            val = self._get_value(el, tag, None)
            if val is not None:
                cfg["path"] = val
                break
        return cfg


if __name__ == '__main__':
    xml_path = r'//usden1-stor.dhi.dk/Projects/61803553-05/Projects/Clean Project F3 2 Oct 2024.mtproj'

    project = XMLUtils(xml_path)

    # ADCP by survey name
    adcp_cfgs = project.get_cfgs_from_survey(
        survey_name="20241002_F3(E)",
        survey_id=0,
        instrument_type="VesselMountedADCP",
    )

    # OBS by survey name (use survey_id="..." if you prefer id)
    obs_cfgs = project.get_cfgs_from_survey(
        survey_name="20241002_F3(E)",
        survey_id=0,
        instrument_type="OBSVerticalProfile",
    )

    # Water Samples by survey name
    ws_cfgs = project.get_cfgs_from_survey(
        survey_name="20241002_F3(E)",
        survey_id=0,
        instrument_type="WaterSample",
    )
    
    info = project.project_info()
    
    
    # get individual instrument configs by name and ID
    cfg1 = project.get_cfg_by_instrument("VesselMountedADCP",instrument_name = '20241002_F3(E)_006r', instrument_id=5)
    cfg2 = project.get_cfg_by_instrument("OBSVerticalProfile", instrument_name="OBS1",instrument_id=18)