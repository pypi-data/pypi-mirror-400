from __future__ import annotations
from typing import TYPE_CHECKING
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.editors.lde.protocols.ilde_row import ILDERow

class ZeModRow(NativeAdapter["ILDERow"]):
    __slots__ = ()

    @property
    def thickness(self) -> float:
        return self.native.Thickness

    @thickness.setter
    def thickness(self, value: float) -> None:
        self.native.Thickness = float(value)

    @property
    def comment(self) -> str:
        return self.native.Comment

    @comment.setter
    def comment(self, comment:str):
        self.native.Comment = comment





