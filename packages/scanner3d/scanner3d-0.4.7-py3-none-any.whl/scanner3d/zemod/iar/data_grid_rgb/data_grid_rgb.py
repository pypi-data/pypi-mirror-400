from __future__ import annotations

from dataclasses import dataclass
import numpy as np
from numpy.typing import NDArray

from scanner3d.zemod.iar.i_grid_meta import IGridMeta
from scanner3d.zemod.iar.i_data_grid_rgb import IDataGridRgb


@dataclass(slots=True)
class DataGridRgb(IDataGridRgb):
    """
    Concrete RGB grid implementation of IDataGridRgb.
    Stores full RGB data (_rgb_values) of shape (ny, nx, 3).

    - `rgb_values` gives full RGB data (ny, nx, 3)
    - `values` returns scalar intensity (ny, nx) as required by IDataGrid
    """

    _rgb_values: NDArray[np.float64]   # shape (ny, nx, 3)
    _meta: IGridMeta

    # ---- IDataGrid core (scalar view) ---------------------------------
    @property
    def values(self) -> NDArray[np.float64]:
        """
        Return scalar intensity image required by IDataGrid.

        You may choose:
          - luminance: 0.299 R + 0.587 G + 0.114 B
          - max channel
          - norm
        For now: Luminance.
        """
        r = self._rgb_values[..., 0]
        g = self._rgb_values[..., 1]
        b = self._rgb_values[..., 2]
        return 0.299 * r + 0.587 * g + 0.114 * b

    @property
    def rgb_values(self) -> NDArray[np.float64]:
        return self._rgb_values

    @property
    def shape(self) -> tuple[int, int]:
        # (ny, nx) — ignore channel dimension
        ny, nx = self._rgb_values.shape[:2]
        return ny, nx

    @property
    def meta(self) -> IGridMeta:
        return self._meta

    # ---- Faster RGB sample access -------------------------------------
    def rgb(self, ix: int, iy: int) -> NDArray[np.float64]:
        return self._rgb_values[iy, ix, :]

    # (r, g, b) properties inherited from IDataGridRgb work automatically

    # ---- Construction helpers -----------------------------------------
    @classmethod
    def from_components(
        cls,
        values: NDArray[np.float64],
        meta: IGridMeta,
    ) -> "DataGridRgb":
        """
        Create DataGridRgb from (ny, nx, 3) float array.
        """
        arr = np.asarray(values, dtype=np.float64)

        if arr.ndim != 3 or arr.shape[2] != 3:
            raise ValueError(
                f"RGB grid values must have shape (ny, nx, 3), got {arr.shape!r}"
            )

        return cls(
            _rgb_values=arr,
            _meta=meta,
        )
