from __future__ import annotations
from dataclasses import dataclass
from typing import Tuple
import numpy as np
from allytools.units import Length, average_length

@dataclass(frozen=True, kw_only=True)
class ZRange:
    z_min: Length
    z_max: Length
    z_focus: Length

    def __post_init__(self) -> None:
        for name, z in (("z_min", self.z_min),
                        ("z_max", self.z_max),
                        ("z_focus", self.z_focus)):
            if z.value_mm < 0:
                raise ValueError(f"{name} must be non-negative; got {z}.")
        if self.z_min > self.z_max:
            raise ValueError(
                f"z_min ({self.z_min}) cannot be greater than z_max ({self.z_max})."
            )
        if not (self.z_min <= self.z_focus <= self.z_max):
            raise ValueError(
                f"z_focus ({self.z_focus}) must lie within "
                f"[{self.z_min}, {self.z_max}]."
            )

    @property
    def span(self) -> Length:
        """Total Z range (z_max - z_min)."""
        return self.z_max - self.z_min

    @property
    def center(self) -> Length:
        """Middle point between z_min and z_max, as Length."""
        return (self.z_min + self.z_max) / 2

    @property
    def mid(self) -> Length:
        return average_length(self.z_min, self.z_max)

    def contains(self, z: Length, *, inclusive: bool = True) -> bool:
        return (self.z_min <= z <= self.z_max) if inclusive else (self.z_min < z < self.z_max)

    def to_tuple(self) -> Tuple[Length, Length, Length]:
        return self.z_min, self.z_max, self.z_focus

    def __str__(self) -> str:
        return f"ZRange[{self.z_min} .. {self.z_max}] (focus={self.z_focus})"

    def __repr__(self) -> str:
        return (
            f"ZRange(z_min={self.z_min!s}, "
            f"z_max={self.z_max!s}, "
            f"z_focus={self.z_focus!s})"
        )

    def wd_sequence(self, step_z: Length) -> list[Length]:
        """
        Generate a sequence of working distances from z_min to z_max (inclusive)
        with step `step_z`. Returned as a list of Length in mm.
        """
        if not isinstance(step_z, Length):
            raise TypeError("step_z must be a Length instance.")
        if step_z.value_mm <= 0:
            raise ValueError("step_z must be positive.")

        z_min_mm = self.z_min.value_mm
        z_max_mm = self.z_max.value_mm
        step_mm = step_z.value_mm
        seq_mm = np.arange(z_min_mm, z_max_mm + step_mm, step_mm, dtype=float)
        if seq_mm[-1] > z_max_mm:
            seq_mm[-1] = z_max_mm
        return [Length(z) for z in seq_mm]
