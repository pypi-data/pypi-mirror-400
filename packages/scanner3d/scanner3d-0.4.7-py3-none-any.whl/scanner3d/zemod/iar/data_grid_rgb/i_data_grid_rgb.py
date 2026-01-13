from __future__ import annotations

from typing import Protocol
import numpy as np
from numpy.typing import NDArray

from scanner3d.zemod.iar.data_grid.i_data_grid import IDataGrid

class IDataGridRgb(IDataGrid, Protocol):
    """
    RGB extension of IDataGrid.

    Contract:
      - All IDataGrid methods/properties still apply to a *scalar* grid
        (e.g. intensity / luminance) exposed via `values` (ny, nx).
      - This protocol adds `rgb_values` (ny, nx, 3) and channel views
        r/g/b, plus an RGB sample accessor.
    """

    # ---- Extra core member: full RGB data -----------------------------
    @property
    def rgb_values(self) -> NDArray[np.float64]:
        """
        Full RGB data array of shape (ny, nx, 3) with channels (R, G, B).
        """
        ...

    # ---- Channel views ------------------------------------------------
    @property
    def r(self) -> NDArray[np.float64]:
        """Red channel view (ny, nx)."""
        return self.rgb_values[..., 0]

    @property
    def g(self) -> NDArray[np.float64]:
        """Green channel view (ny, nx)."""
        return self.rgb_values[..., 1]

    @property
    def b(self) -> NDArray[np.float64]:
        """Blue channel view (ny, nx)."""
        return self.rgb_values[..., 2]

    # ---- RGB sample access --------------------------------------------
    def rgb(self, ix: int, iy: int) -> NDArray[np.float64]:
        """
        Return RGB triplet at integer pixel position (ix, iy) as a length-3 array.
        """
        return self.rgb_values[iy, ix, :].astype(np.float64, copy=False)
