from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from scanner3d.geo import Position, ZRange
from isensor.sensor import Sensor
from lensguild.objective import Objective
from allytools.strings import first_token
from allytools.units import LengthUnit
from gosti.wavelength import Wavelength

class Camera3DTypes(Enum):
    Reconstruction = "3D Reconstruction"
    Texture = "Texture"

@dataclass(frozen=True, slots=True, kw_only=True)
class Camera3D:
    name: str
    type: Camera3DTypes
    objective: Objective
    sensor: Sensor
    position: Position
    z_range: ZRange
    primary_wavelength: Wavelength

    @property
    def description(self) -> str:
        return (
            f"{first_token(self.objective.objectiveID.model)}_"
            f"{first_token(str(self.objective.f_number))}_"
            f"{first_token(self.sensor.sensor_model.model)}"
        )

    def __str__(self) -> str:
        return (
            f"🎥 Camera3D '{self.name}'\n"
            f"────────────────────────────\n"
            f"  type      : {self.type}\n"
            f"  objective : {self.objective}\n"
            f"  sensor    : {self.sensor}\n"
            f"  position  : {self.position}\n"
            f"  z_range   : {self.z_range}\n"
            f"  primary wavelength : "
            f"{self.primary_wavelength.to(LengthUnit.NM):.1f} nm"
        )

    def __repr__(self) -> str:
        t = getattr(self.type, "name", self.type)
        obj = getattr(self.objective, "name", self.objective)
        sen = getattr(self.sensor, "name", self.sensor)
        return (
            f"Camera3D(name={self.name!r}, type={t!s}, "
            f"objective={obj!s}, sensor={sen!s}, "
            f"position={self.position!s}, z_range={self.z_range!s})"
        )
