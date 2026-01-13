from __future__ import annotations
from typing import TYPE_CHECKING
from scanner3d.zemod.core.indexed_collection     import IndexedCollection
from scanner3d.zemod.zemod_wavelength import ZeModWavelength

if TYPE_CHECKING:
    from zempy.zosapi.systemdata.protocols.i_wavelengths import IWavelengths
    from zempy.zosapi.systemdata.protocols.i_wavelength import IWavelength

class ZeModWavelengths(IndexedCollection[ZeModWavelength, "IWavelengths", "IWavelength"]):
    __slots__ = ()

    def _native_count(self) -> int:
        return int(self.native.NumberOfWavelengths)

    def _native_get(self, index: int) -> "IWavelength":
        return self.native.GetWavelength(index)

    def _native_add(self, value: float, weight: float = 1.0) -> "IWavelength":
        return self.native.AddWavelength(float(value), float(weight))

    def _native_delete_at(self, index:int) -> None:
        self.native.RemoveWavelength(index)

    def _child_from_native(self, native_child: "IWavelength") -> ZeModWavelength:
        return ZeModWavelength(native_child)

    @property
    def n_wavelengths(self) -> int:
        return self.count

    def get_wavelength(self, index: int) -> ZeModWavelength:
        return self.get_child(index)

    def add_wavelength(self, value: float, weight: float = 1.0) -> ZeModWavelength:
        return self.add_child(value, weight)
