from __future__ import annotations
from typing import TYPE_CHECKING, List, cast
from scanner3d.zemod.core.native_adapter import NativeAdapter

if TYPE_CHECKING:
    from zempy.zosapi.analysis.data.protocols.iar_header_data import IAR_HeaderData


class ZeModHeaderData(NativeAdapter["IAR_HeaderData"]):
    """
    Lightweight ZeMod wrapper for IAR_HeaderData.
    Matches the style of ZeModDataGrid.
    """
    __slots__ = ()

    @property
    def lines(self) -> List[str]:
        # Native.Lines is a sequence of strings
        return [cast(str, line) for line in self.native.Lines]

    def __len__(self) -> int:
        return len(self.native.Lines)

    def __getitem__(self, idx: int) -> str:
        return cast(str, self.native.Lines[idx])

    def __repr__(self) -> str:
        return f"ZeModHeaderData({len(self)} lines)"
