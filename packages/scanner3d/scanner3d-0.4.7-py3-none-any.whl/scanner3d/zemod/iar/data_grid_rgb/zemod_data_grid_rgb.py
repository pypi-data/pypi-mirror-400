from __future__ import annotations

from typing import TYPE_CHECKING, Tuple
import numpy as np
from numpy.typing import NDArray

from allytools.types.validate_cast import validate_cast
from scanner3d.zemod.core.native_adapter import NativeAdapter
from scanner3d.zemod.iar.data_grid_rgb.i_data_grid_rgb import IDataGridRgb
from scanner3d.zemod.iar.grid_meta import GridMeta

if TYPE_CHECKING:
    from zempy.zosapi.analysis.data.protocols.iar_data_grid_rgb import IAR_DataGridRgb
    from scanner3d.zemod.iar.i_grid_meta import IGridMeta


class ZeModDataGridRgb(NativeAdapter["IAR_DataGridRgb"], IDataGridRgb):
    """
    Adapter around ZOSAPI.Analysis.Data.IAR_DataGridRgb that exposes an
    IDataGridRgb interface.

    - Lazily pulls RGB data via FillValues into a numpy array (ny, nx, 3)
    - `values` is a scalar intensity (luminance) view as required by IDataGrid
    - Metadata is cached via GridMeta.from_zempy(native)
    """

    __slots__ = ("_meta", "_rgb_values")

    def __init__(self, native: IAR_DataGridRgb) -> None:
        super().__init__(native)
        # snapshot metadata once (Description, labels, min_x, dx, etc.)
        self._meta = GridMeta.from_zempy(native)
        self._rgb_values: NDArray[np.float64] | None = None

    # ------------------------------------------------------------------
    # IDataGrid core (scalar view)
    # ------------------------------------------------------------------
    @property
    def values(self) -> NDArray[np.float64]:
        """
        Scalar intensity image derived from RGB, required by IDataGrid.

        Currently uses ITU-style luminance:
            L = 0.299 R + 0.587 G + 0.114 B
        """
        rgb = self.rgb_values
        r = rgb[..., 0]
        g = rgb[..., 1]
        b = rgb[..., 2]
        return 0.299 * r + 0.587 * g + 0.114 * b

    # ------------------------------------------------------------------
    # IDataGridRgb core (full RGB)
    # ------------------------------------------------------------------
    @property
    def rgb_values(self) -> NDArray[np.float64]:
        """
        Full RGB data (ny, nx, 3) pulled once from the native grid.
        """
        if self._rgb_values is None:
            nx = int(self.native.Nx)
            ny = int(self.native.Ny)
            full_size = nx * ny

            # Allocate 1D buffers for FillValues
            r = np.empty(full_size, dtype=np.float64)
            g = np.empty(full_size, dtype=np.float64)
            b = np.empty(full_size, dtype=np.float64)

            # ZOSAPI fills the sequences in-place
            self.native.FillValues(full_size, r, g, b)

            # Reshape into (ny, nx, 3)
            rgb = np.empty((ny, nx, 3), dtype=np.float64)
            for k in range(full_size):
                x = k % nx
                y = k // nx
                rgb[y, x, 0] = r[k]
                rgb[y, x, 1] = g[k]
                rgb[y, x, 2] = b[k]

            self._rgb_values = rgb

        return self._rgb_values

    # ------------------------------------------------------------------
    # Geometry / metadata
    # ------------------------------------------------------------------
    @property
    def shape(self) -> Tuple[int, int]:
        """
        (ny, nx) – number of rows and columns (channel dimension excluded).
        """
        ny = int(self.native.Ny)
        nx = int(self.native.Nx)
        return ny, nx

    @property
    def meta(self) -> IGridMeta:
        return validate_cast(self._meta, IGridMeta)

    @property
    def min_x(self) -> float:
        return self._meta.min_x

    @property
    def min_y(self) -> float:
        return self._meta.min_y

    @property
    def dx(self) -> float:
        return self._meta.dx

    @property
    def dy(self) -> float:
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

    # ------------------------------------------------------------------
    # RGB sample access (optional override for speed)
    # ------------------------------------------------------------------
    def rgb(self, ix: int, iy: int) -> NDArray[np.float64]:
        return self.rgb_values[iy, ix, :]
