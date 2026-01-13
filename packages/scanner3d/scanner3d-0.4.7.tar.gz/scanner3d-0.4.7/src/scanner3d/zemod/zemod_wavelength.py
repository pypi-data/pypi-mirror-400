from __future__ import annotations
from typing import TYPE_CHECKING
import math
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.systemdata.protocols.i_wavelength import IWavelength

class ZeModWavelength(NativeAdapter["IWavelength"]):
    __slots__ = ()

    @property
    def number(self) -> int:
        return int(self.native.WavelengthNumber)

    @property
    def value(self) -> float:
        return float(self.native.Wavelength)

    @value.setter
    def value(self, w: float) -> None:
        w = float(w)
        if not math.isfinite(w) or w <= 0.0:
            raise ValueError(f"Wavelength must be finite and > 0, got {w!r}")
        if self.native.Wavelength != w:
            self.native.Wavelength = w

    @property
    def weight(self) -> float:
        return float(self.native.Weight)

    @weight.setter
    def weight(self, wt: float) -> None:
        wt = float(wt)
        if not math.isfinite(wt) or wt < 0.0:
            raise ValueError(f"Weight must be finite and >= 0, got {wt!r}")
        if self.native.Weight != wt:
            self.native.Weight = wt

    def __repr__(self) -> str:
        try:
            return (f"{self.__class__.__name__}"
                    f"(number={self.number}, value={self.value:.6f}, weight={self.weight:.4f})")
        except Exception:
            return f"{self.__class__.__name__}(?)"

    __str__ = __repr__
