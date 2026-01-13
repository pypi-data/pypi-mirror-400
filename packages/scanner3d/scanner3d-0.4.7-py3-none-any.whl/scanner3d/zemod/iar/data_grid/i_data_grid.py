from __future__ import annotations
from typing import Protocol
import numpy as np
from numpy.typing import NDArray
from allytools.units import Length
from scanner3d.zemod.iar.i_grid_meta import IGridMeta

class IDataGrid(IGridMeta, Protocol):

    def get_raw(self) -> NDArray[np.float64]:
        """
        IShotResult-compatible: return underlying array as-is.
        """
        return self.values


    @property
    def values(self) -> NDArray[np.float64]: ...

    @property
    def meta(self) -> IGridMeta: ...


    @property
    def shape(self) -> tuple[int, int]:
        """
        (ny, nx) – number of rows and columns.

        NOTE: Implementors must provide this so meta can be used
        without having direct access to the data array.
        """
        ...


    @property
    def nx(self) -> int:
        return self.shape[1]

    @property
    def ny(self) -> int:
        return self.shape[0]

    @property
    def x_max(self) -> Length:
        unit = self.min_x.unit
        dx_in_unit = self.dx.to(unit)
        min_x_in_unit = self.min_x.to(unit)
        x_max_value = min_x_in_unit + (self.nx - 1) * dx_in_unit
        return Length(x_max_value, unit)

    @property
    def y_max(self) -> Length:
        unit = self.min_y.unit
        dy_in_unit = self.dy.to(unit)
        min_y_in_unit = self.min_y.to(unit)
        y_max_value = min_y_in_unit + (self.ny - 1) * dy_in_unit
        return Length(y_max_value, unit)

    @property
    def extent(self) -> tuple[Length, Length, Length, Length]:
        return self.min_x, self.x_max, self.min_y, self.y_max

    @property
    def x_coords(self) -> NDArray[np.float64]:
        return self.min_x + self.dx * np.arange(self.nx, dtype=np.float64)

    @property
    def y_coords(self) -> NDArray[np.float64]:
        return self.min_y + self.dy * np.arange(self.ny, dtype=np.float64)

    def x(self, ix: int) -> Length:
        return self.min_x + ix * self.dx

    def y(self, iy: int) -> Length:
        return self.min_y + iy * self.dy

    @property
    def value_min(self) -> float:
        try:
            return float(np.nanmin(self.values))
        except ValueError:
            return float("nan")

    @property
    def value_max(self) -> float:
        try:
            return float(np.nanmax(self.values))
        except ValueError:
            return float("nan")

