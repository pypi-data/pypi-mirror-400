from __future__ import annotations
import numpy as np
from dataclasses import dataclass
from typing import Sequence, TYPE_CHECKING

if TYPE_CHECKING:
    from scanner3d.analysis.shot import Shot


@dataclass(frozen=True, slots=True)
class FrameMeta:
    value_min: float
    value_max: float

    @staticmethod
    def from_shots(shots: Sequence["Shot"]) -> "FrameMeta":
        if not shots:
            return FrameMeta(value_min=np.nan, value_max=np.nan)
        arrays = [np.asarray(s.raw_data, dtype=float).ravel() for s in shots]
        v = np.concatenate(arrays)
        finite_mask = np.isfinite(v)
        finite_vals = v[finite_mask]
        if finite_vals.size == 0:
            return FrameMeta(value_min=np.nan, value_max=np.nan)

        return FrameMeta(value_min=float(np.nanmin(finite_vals)),
                         value_max=float(np.nanmax(finite_vals)))

    def __str__(self) -> str:
        vmin = "NaN" if np.isnan(self.value_min) else f"{self.value_min:.6g}"
        vmax = "NaN" if np.isnan(self.value_max) else f"{self.value_max:.6g}"
        return f"📝 Frame meta:\n  • min = {vmin}\n  • max = {vmax}"

    def __repr__(self) -> str:
        return f"Frame min={self.value_min:.6g} max={self.value_max:.6g}>"
