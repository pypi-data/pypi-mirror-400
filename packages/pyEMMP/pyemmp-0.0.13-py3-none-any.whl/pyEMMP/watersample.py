import xml.etree.ElementTree as ET
import pandas as pd
from numpy.typing import NDArray
from dataclasses import dataclass, field
import numpy as np

class WaterSample():
    def __init__(self, cfg: ET.Element) -> None:
        self.root = cfg

        self.name = self.root.attrib.get('name', "MyWaterSample")

        rows = []
        for sample in self.root.findall("Sample"):
            rows.append(sample.attrib)
        df = pd.DataFrame(rows)

        @dataclass
        class WaterSampleData:
            sample: str = field(metadata={"desc": "Sample ID"})
            datetime: NDArray[np.datetime64] = field(metadata={"desc": "Datetime values"})
            depth: NDArray[np.float64] = field(metadata={"desc": "Depth values"})
            ssc: NDArray[np.float64] = field(metadata={"desc": "SSC values"})
            notes: str = field(default="", metadata={"desc": "Notes"})

        self.data = WaterSampleData(
            sample=df["Sample"].to_numpy(dtype=str),
            datetime=df["DateTime"].to_numpy(dtype=np.datetime64),
            depth=df["Depth"].to_numpy(dtype=np.float64),
            ssc=df["SSC"].to_numpy(dtype=np.float64),
            notes=df["Notes"].to_numpy(dtype=str)
        )