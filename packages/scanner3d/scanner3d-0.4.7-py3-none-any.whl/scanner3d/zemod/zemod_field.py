from __future__ import annotations
from typing import TYPE_CHECKING
from scanner3d.zemod.core.native_adapter import NativeAdapter
if TYPE_CHECKING:
    from zempy.zosapi.systemdata.protocols.i_fields import IFields
    from zempy.zosapi.systemdata.protocols.i_field import IField

class ZeModField(NativeAdapter["IField"]):
    __slots__ = ()

    def number(self) -> int:
        return int(self.native.FieldNumber)

    @property
    def x(self) -> float:
        return float(self.native.X)

    @x.setter
    def x(self, v: float) -> None:
        self.native.X = float(v)

    @property
    def y(self) -> float:
        return float(self.native.Y)

    @y.setter
    def y(self, v: float) -> None:
        self.native.Y = float(v)

    def set_xy(self, x: float, y: float) -> None:
        self.native.SetXY(float(x), float(y))

    def __str__(self) -> str:
        try:
            return f"ZeModField(number={self.number()}, x={self.x:.4f}, y={self.y:.4f})"
        except Exception:
            return "ZeModField(number=?, x=?, y=?)"
