from __future__ import annotations
from typing import TYPE_CHECKING, cast, Tuple
import numpy as np
from numpy.typing import NDArray
from allytools.units import Length
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.iar.data_grid.i_data_grid import IDataGrid
from scanner3d.zemod.iar.grid_meta import GridMeta
from scanner3d.afs.i_shot_result import ShotResultType

if TYPE_CHECKING:
    from zempy.zosapi.analysis.data.protocols.iar_data_grid import IAR_DataGrid
    from scanner3d.zemod.iar.i_grid_meta import IGridMeta


class ZeModDataGrid(NativeAdapter["IAR_DataGrid"], IDataGrid):
    __slots__ = ("_meta",)

    def __init__(self, native: IAR_DataGrid) -> None:
        super().__init__(native)
        self._meta = GridMeta.from_zempy(native)

    @property
    def result_type(self) -> ShotResultType:
        return ShotResultType.GRID


    @property
    def values(self) -> NDArray[np.float64]:
        return cast(NDArray[np.float64], self.native.Values)

    @property
    def min_x(self) -> Length:
        return self._meta.min_x

    @property
    def min_y(self) -> Length:
        return self._meta.min_y

    @property
    def dx(self) -> Length:
        return self._meta.dx

    @property
    def dy(self) -> Length:
        return self._meta.dy

    @property
    def shape(self) -> Tuple[int, int]:
        ny = int(self.native.Ny)
        nx = int(self.native.Nx)
        return ny, nx

    @property
    def meta(self) -> IGridMeta:
        return self._meta

    @property
    def description(self) -> str:
        return self._meta.description

    @property
    def x_label(self) -> str:
        return self._meta.x_label

    @property
    def y_label(self) -> str:
        return self._meta.y_label

    @property
    def value_label(self) -> str:
        return self._meta.value_label
