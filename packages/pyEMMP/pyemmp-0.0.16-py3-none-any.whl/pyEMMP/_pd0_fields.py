from dataclasses import dataclass
from typing import List

@dataclass
class FieldDef:
    """
    Represents a field definition in a PD0 binary record.

    Attributes
    ----------
    name : str
        The name of the field.
    nbytes : int
        The number of bytes occupied by the field.
    endian : str
        The byte order specifier (e.g., '<' for little-endian).
    fmt : str
        The struct format character for this field.
    decode : bool
        If True, the field should be decoded to a Python value.
    """
    name: str
    nbytes: int
    endian: str
    fmt: str
    decode: bool

class Pd0Formats:
    """
    Contains the field definitions for the PD0 file format.

    Each attribute is a list (or a single instance for miscellaneous fields)
    of FieldDef objects defining the fields for that section of the PD0 file.
    """
    ensemble_header: List[FieldDef] = [
        FieldDef("HEADER ID", 1, "<", "B", True),
        FieldDef("DATA SOURCE ID", 1, "<", "B", True),
        FieldDef("N BYTES IN ENSEMBLE", 2, "<", "H", True),
        FieldDef("SPARE", 1, "<", "B", True),
        FieldDef("N DATA TYPES", 1, "<", "B", True)
    ]

    fixed_leader: List[FieldDef] = [
        FieldDef("FIXED LEADER ID", 2, "<", "H", True),
        FieldDef("CPU F/W VER.", 1, "<", "B", True),
        FieldDef("CPU F/W REV.", 1, "<", "B", True),
        FieldDef("SYSTEM CONFIGURATION", 2, "<", "H", False),
        FieldDef("REAL/SIM FLAG", 1, "<", "B", True),
        FieldDef("LAG LENGTH", 1, "<", "B", True),
        FieldDef("NUMBER OF BEAMS", 1, "<", "B", True),
        FieldDef("NUMBER OF CELLS {WN}", 1, "<", "B", True),
        FieldDef("PINGS PER ENSEMBLE {WP}", 2, "<", "H", True),
        FieldDef("DEPTH CELL LENGTH {WS}", 2, "<", "H", True),
        FieldDef("BLANK AFTER TRANSMIT {WF}", 2, "<", "H", True),
        FieldDef("PROFILING MODE {WM}", 1, "<", "B", True),
        FieldDef("LOW CORR THRESH {WC}", 1, "<", "B", True),
        FieldDef("NO. CODE REPS", 1, "<", "B", True),
        FieldDef("%GD MINIMUM {WG}", 1, "<", "B", True),
        FieldDef("ERROR VELOCITY MAXIMUM {WE}", 2, "<", "H", True),
        FieldDef("TPP MINUTES", 1, "<", "B", True),
        FieldDef("TPP SECONDS", 1, "<", "B", True),
        FieldDef("TPP HUNDREDTHS {TP}", 1, "<", "B", True),
        FieldDef("COORDINATE TRANSFORM {EX}", 1, "<", "B", False),
        FieldDef("HEADING ALIGNMENT {EA}", 2, "<", "H", True),
        FieldDef("HEADING BIAS {EB}", 2, "<", "H", True),
        FieldDef("SENSOR SOURCE {EZ}", 1, "<", "B", True),
        FieldDef("SENSORS AVAILABLE", 1, "<", "B", True),
        FieldDef("BIN 1 DISTANCE", 2, "<", "H", True),
        FieldDef("XMIT PULSE LENGTH BASED ON {WT}", 2, "<", "H", True),
        FieldDef('starting cell WP REF LAYER AVERAGE {WL} ending cell', 2, "<", "H", True),
        FieldDef("FALSE TARGET THRESH {WA}", 1, "<", "B", True),
        FieldDef("SPARE1", 1, "<", "B",True),
        FieldDef("TRANSMIT LAG DISTANCE", 2, "<", "H", True),
        FieldDef("CPU BOARD SERIAL NUMBER", 8, "<", "Q", True),
        FieldDef("SYSTEM BANDWIDTH {WB}", 2, "<", "H", True),
        FieldDef("SYSTEM POWER {CQ}", 1, "<", "B", True),
        FieldDef("SPARE2", 1, "<", "B", True),
        FieldDef("INSTRUMENT SERIAL NUMBER", 4, "<", "I", True),
        FieldDef("BEAM ANGLE", 1, "<", "B", True)
    ]

    variable_leader = [
        FieldDef('VARIABLE LEADER ID', 2, '<', 'H', True),
        FieldDef('ENSEMBLE NUMBER', 2, '<', 'H', True),
        FieldDef('RTC YEAR {TS}', 1, '<', 'B', True),
        FieldDef('RTC MONTH {TS}', 1, '<', 'B', True),
        FieldDef('RTC DAY {TS}', 1, '<', 'B', True),
        FieldDef('RTC HOUR {TS}', 1, '<', 'B', True),
        FieldDef('RTC MINUTE {TS}', 1, '<', 'B', True),
        FieldDef('RTC SECOND {TS}', 1, '<', 'B', True),
        FieldDef('RTC HUNDREDTHS {TS}', 1, '<', 'B', True),
        FieldDef('ENSEMBLE # MSB', 1, '<', 'B', True),
        FieldDef('BIT RESULT', 2, '<', 'H', True),
        FieldDef('SPEED OF SOUND {EC}', 2, '<', 'H', True),
        FieldDef('DEPTH OF TRANSDUCER {ED}', 2, '<', 'H', True),
        FieldDef('HEADING {EH}', 2, '<', 'H', True),
        FieldDef('PITCH TILT 1 {EP}', 2, '<', 'h', True),
        FieldDef('ROLL TILT 2 {ER}', 2, '<', 'h', True),
        FieldDef('SALINITY {ES}', 2, '<', 'H', True),
        FieldDef('TEMPERATURE {ET}', 2, '<', 'h', True),
        FieldDef('MPT MINUTES', 1, '<', 'B', True),
        FieldDef('MPT SECONDS', 1, '<', 'B', True),
        FieldDef('MPT HUNDREDTHS', 1, '<', 'B', True),
        FieldDef('HDG STD DEV', 1, '<', 'B', True),
        FieldDef('PITCH STD DEV', 1, '<', 'B', True),
        FieldDef('ROLL STD DEV', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 0', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 1', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 2', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 3', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 4', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 5', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 6', 1, '<', 'B', True),
        FieldDef('ADC CHANNEL 7', 1, '<', 'B', True),
        FieldDef('ERROR STATUS WORD ESW {CY}', 4, '<', 'I', True),
        FieldDef('SPARE1', 2, '<', 'B', False),
        FieldDef('PRESSURE', 4, '<', 'I', True),
        FieldDef('PRESSURE SENSOR VARIANCE', 4, '<', 'I', True),
        FieldDef('SPARE2', 1, '<', 'B', False),
        FieldDef('RTC CENTURY', 1, '<', 'B', True),
        FieldDef('RTC YEAR', 1, '<', 'B', True),
        FieldDef('RTC MONTH', 1, '<', 'B', True),
        FieldDef('RTC DAY', 1, '<', 'B', True),
        FieldDef('RTC HOUR', 1, '<', 'B', True),
        FieldDef('RTC MINUTE', 1, '<', 'B', True),
        FieldDef('RTC SECOND', 1, '<', 'B', True),
        FieldDef('RTC HUNDREDTH', 1, '<', 'B', True)
    ]

    
    bottom_track: List[FieldDef] = [
        FieldDef("BOTTOM TRACK ID", 2, ">", "H", True),
        FieldDef("BT PINGS PER ENSEMBLE {BP}", 2, "<", "H", True),
        FieldDef("BT DELAY BEFORE RE-ACQUIRE {BD}", 2, "<", "H", True),
        FieldDef("BT CORR MAG MIN {BC}", 1, "<", "B", True),
        FieldDef("BT EVAL AMP MIN {BA}", 1, "<", "B", True),
        FieldDef("BT PERCENT GOOD MIN {BG}", 1, "<", "B", True),
        FieldDef("BT MODE {BM}", 1, "<", "B", True),
        FieldDef("BT ERR VEL MAX {BE}", 2, "<", "H", True),
        FieldDef("Reserved", 4, "<", "I", True),
        FieldDef("BEAM#1 BT RANGE", 2, "<", "H", True),
        FieldDef("BEAM#2 BT RANGE", 2, "<", "H", True),
        FieldDef("BEAM#3 BT RANGE", 2, "<", "H", True),
        FieldDef("BEAM#4 BT RANGE", 2, "<", "H", True),
        FieldDef("BEAM#1 BT VEL", 2, "<", "h", True),
        FieldDef("BEAM#2 BT VEL", 2, "<", "h", True),
        FieldDef("BEAM#3 BT VEL", 2, "<", "h", True),
        FieldDef("BEAM#4 BT VEL", 2, "<", "h", True),
        FieldDef("BEAM#1 BT CORR.", 1, "<", "B", True),
        FieldDef("BEAM#2 BT CORR.", 1, "<", "B", True),
        FieldDef("BEAM#3 BT CORR.", 1, "<", "B", True),
        FieldDef("BEAM#4 BT CORR.", 1, "<", "B", True),
        FieldDef("BEAM#1 EVAL AMP", 1, "<", "B", True),
        FieldDef("BEAM#2 EVAL AMP", 1, "<", "B", True),
        FieldDef("BEAM#3 EVAL AMP", 1, "<", "B", True),
        FieldDef("BEAM#4 EVAL AMP", 1, "<", "B", True),
        FieldDef("BEAM#1 BT PGOOD", 1, "<", "B", True),
        FieldDef("BEAM#2 BT PGOOD", 1, "<", "B", True),
        FieldDef("BEAM#3 BT PGOOD", 1, "<", "B", True),
        FieldDef("BEAM#4 BT PGOOD", 1, "<", "B", True),
        FieldDef("REF LAYER MIN {BL}", 2, "<", "H", True),
        FieldDef("REF LAYER NEAR {BL}", 2, "<", "H", True),
        FieldDef("REF LAYER FAR {BL}", 2, "<", "H", True),
        FieldDef("BEAM #1 REF LAYER VEL", 2, "<", "h", True),
        FieldDef("BEAM #2 REF LAYER VEL", 2, "<", "h", True),
        FieldDef("BEAM #3 REF LAYER VEL", 2, "<", "h", True),
        FieldDef("BEAM #4 REF LAYER VEL", 2, "<", "h", True),
        FieldDef("BM#1 REF CORR", 1, "<", "B", True),
        FieldDef("BM#2 REF CORR", 1, "<", "B", True),
        FieldDef("BM#3 REF CORR", 1, "<", "B", True),
        FieldDef("BM#4 REF CORR", 1, "<", "B", True),
        FieldDef("BM#1 REF INT", 1, "<", "B", True),
        FieldDef("BM#2 REF INT", 1, "<", "B", True),
        FieldDef("BM#3 REF INT", 1, "<", "B", True),
        FieldDef("BM#4 REF INT", 1, "<", "B", True),
        FieldDef("BM#1 REF PGOOD", 1, "<", "B", True),
        FieldDef("BM#2 REF PGOOD", 1, "<", "B", True),
        FieldDef("BM#3 REF PGOOD", 1, "<", "B", True),
        FieldDef("BM#4 REF PGOOD", 1, "<", "B", True),
        FieldDef("BT MAX. DEPTH {BX}", 2, "<", "H", True),
        FieldDef("BM#1 RSSI AMP", 1, "<", "B", True),
        FieldDef("BM#2 RSSI AMP", 1, "<", "B", True),
        FieldDef("BM#3 RSSI AMP", 1, "<", "B", True),
        FieldDef("BM#4 RSSI AMP", 1, "<", "B", True),
        FieldDef("GAIN", 1, "<", "B", True),
        FieldDef("*SEE BYTE 17", 1, "<", "B", True),
        FieldDef("*SEE BYTE 19", 1, "<", "B", True),
        FieldDef("*SEE BYTE 21", 1, "<", "B", True),
        FieldDef("*SEE BYTE 23", 1, "<", "B", True),
        FieldDef("RESERVED", 4, "<", "I", True)
    ]
    
    # Miscellaneous field definitions
    address_offsets: FieldDef = [FieldDef("ADDRESS OFFSET", 2, "<", "H", True)]
    
    
    data_ID_code: FieldDef = [FieldDef("DATA ID CODE", 2, "<", "H", True)]
    echo_intensity: FieldDef = [FieldDef("ECHO INTENSITY", 1, "<", "B", True)]
    velocity: FieldDef = [FieldDef("VELOCITY", 2, "<", "h", True)]
    corr_mag: FieldDef = [FieldDef("CORRELATION MAGNITUDE", 1, "<", "B", True)]
    pct_good: FieldDef = [FieldDef("PERCENT GOOD", 1, "<", "B", True)]
    #variable: FieldDef = [FieldDef("Variable", 1, "<", "B", True)]
    
    reserved_bit_data: FieldDef = [FieldDef("RESERVED BIT DATA", 2, "<", "H", True)]
    
    external_fields = [
        FieldDef("LEADER ID", 2, "<", "H", True),             # 2-byte unsigned int
        FieldDef("GEODETIC DATUM", 10, "<", "10s", True),       # 10-byte fixed-width string (e.g., "WGS84")
        FieldDef("VERTICAL DATUM", 10, "<", "10s", True),        # 10-byte fixed-width string (e.g., "SEAFLOOR")
        FieldDef("MAGNETIC DECLINATION", 4, "<", "f", True),     # 4-byte float
        FieldDef("UTC OFFSET", 1, "<", "b", True),               # 1-byte signed int
        FieldDef("CRP X", 4, "<", "f", True),                    # 4-byte float
        FieldDef("CRP Y", 4, "<", "f", True),                    # 4-byte float
        FieldDef("CRP Z", 4, "<", "f", True),                    # 4-byte float
        FieldDef("SITE NAME", 20, "<", "20s", True),             # 20-byte fixed-width string
        FieldDef("SURVEYOR", 20, "<", "20s", True),              # 20-byte fixed-width string
        FieldDef("DEPLOYMENT ID", 20, "<", "20s", True),         # 20-byte fixed-width string
        FieldDef("X", 4, "<", "f", True),                        # 4-byte float
        FieldDef("Y", 4, "<", "f", True),                        # 4-byte float
        FieldDef("Z", 4, "<", "f", True),                        # 4-byte float
        FieldDef("PITCH", 4, "<", "f", True),                    # 4-byte float
        FieldDef("ROLL", 4, "<", "f", True),                     # 4-byte float
        FieldDef("YAW", 4, "<", "f", True),                      # 4-byte float
        FieldDef("TURBIDITY", 4, "<", "f", True),                # 4-byte float
        FieldDef("RSSI BEAM 1", 4, "<", "f", True), 
        FieldDef("RSSI BEAM 2", 4, "<", "f", True), 
        FieldDef("RSSI BEAM 3", 4, "<", "f", True), 
        FieldDef("RSSI BEAM 4", 4, "<", "f", True),]
    
    
# Example usage:
if __name__ == "__main__":
    # Print out fixed leader fields as a demonstration.
    for field in Pd0Formats.fixed_leader:
        print(f"{field.name}: {field.nbytes} bytes, format '{field.fmt}', decode={field.decode}")
