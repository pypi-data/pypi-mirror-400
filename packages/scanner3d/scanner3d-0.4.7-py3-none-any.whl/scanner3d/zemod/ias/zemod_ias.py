from __future__ import annotations
from typing import TYPE_CHECKING, Protocol
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.analysis.ias.protocols.ias_ import IAS_


class ZeModIASSettings(Protocol):
    def apply_to(self, ias: "ZeModIAS") -> None:
        ...


class ZeModIAS(NativeAdapter["IAS_"]):
    __slots__ = ()

    def set_field_number(self, n: int) -> None:
        self.native.Field.SetFieldNumber(n)

    def apply_settings(self, settings: ZeModIASSettings) -> None:
        settings.apply_to(self)