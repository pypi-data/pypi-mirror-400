from __future__ import annotations
from dataclasses import dataclass, asdict
from enum import Enum
from typing import Optional
from scanner3d.zemod.enums.enums import ZeModFieldTypes, ZeModFieldNormalizationType
from isensor.sensor_positions import SensorPosition


class WavelengthCriteria(Enum):
    Primary = "Primary"

class FocusDistanceCriteria(Enum):
    BestFocus = "Best focus position from camera"
    AverageFocus = "Average between z_min and z_max"

@dataclass
class TunerSettings:
    field_type: ZeModFieldTypes
    filed_normalization : ZeModFieldNormalizationType
    focus_distance_criteria: Optional[FocusDistanceCriteria] =None
    wavelength_criteria: Optional[WavelengthCriteria] = None
    analysis_field_number: Optional[int] = None
    extra_field_position: Optional[SensorPosition] = None

    def to_dict(self) -> dict:
        d = asdict(self)
        for key, value in d.items():
            if isinstance(value, Enum):
                d[key] = value.value
            elif isinstance(value, SensorPosition):
                d[key] = str(value)
        return d

    def __str__(self) -> str:
        parts = []
        for key, value in self.to_dict().items():
            parts.append(f"{key}={value}")
        # Join with newline and indent each field
        body = "\n".join("  " + p for p in parts)
        return f"TunerSettings(\n{body}\n)"

album_settings = TunerSettings(
    field_type=ZeModFieldTypes.RealImageHeight,
    filed_normalization=ZeModFieldNormalizationType.Rectangular,
    focus_distance_criteria=FocusDistanceCriteria.BestFocus,
    wavelength_criteria=WavelengthCriteria.Primary,
    analysis_field_number=1)

matrix_settings = TunerSettings(
    field_type=ZeModFieldTypes.RealImageHeight,
    filed_normalization=ZeModFieldNormalizationType.Rectangular,
    focus_distance_criteria=FocusDistanceCriteria.BestFocus,
    wavelength_criteria=WavelengthCriteria.Primary,
    analysis_field_number=1,
    extra_field_position=SensorPosition.TOP_RIGHT
)