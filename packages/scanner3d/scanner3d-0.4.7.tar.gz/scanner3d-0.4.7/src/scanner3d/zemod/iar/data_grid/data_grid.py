from __future__ import annotations
from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray
from typing import TYPE_CHECKING
from allytools.units import Length
from scanner3d.zemod.iar.data_grid.i_data_grid import IDataGrid
from scanner3d.afs.i_shot_result import ShotResultType

if TYPE_CHECKING:
    from scanner3d.zemod.iar.i_grid_meta import IGridMeta

@dataclass(slots=True)
class DataGrid(IDataGrid):
    _values: NDArray[np.float64]
    _meta: IGridMeta

    @property
    def result_type(self) -> ShotResultType:
        return ShotResultType.GRID

    @property
    def meta(self) -> IGridMeta:
        return self._meta

    @property
    def shape(self) -> tuple[int, int]:
        h, w = self._values.shape
        return h, w

    @property
    def values(self) -> NDArray[np.float64]:
        return self._values

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

    @classmethod
    def from_components(
        cls,
        values: NDArray[np.float64],
        meta: IGridMeta,
    ) -> DataGrid:
        return cls(_values=np.asarray(values, dtype=np.float64), _meta=meta)
