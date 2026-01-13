from typing import cast
import numpy as np
from numpy.typing import NDArray
from scanner3d.afs.i_shot_meta import IShotMeta
from scanner3d.afs.i_shot_result import IShotResult
from scanner3d.zemod.iar.grid_meta import GridMeta
from scanner3d.zemod.iar.data_grid.data_grid import DataGrid
from scanner3d.analysis.zernike_data import ZernikeMeta, ZernikeData


def shot_result_from_raw_and_meta(
    raw: NDArray[np.float64],
    meta: IShotMeta,
) -> IShotResult[IShotMeta]:
    """
    Central place to map meta type -> concrete Shot result.
    frame_read() stays completely generic and just calls this.
    """
    if isinstance(meta, GridMeta):
        # raw: (Ny, Nx)
        result = DataGrid.from_components(raw, cast(GridMeta, meta))
        return cast(IShotResult[IShotMeta], result)

    if isinstance(meta, ZernikeMeta):
        # raw: (Nterms,)
        result = ZernikeData.from_components(coefficients=raw, meta=cast(ZernikeMeta, meta))
        return cast(IShotResult[IShotMeta], result)

    raise TypeError(
        f"Unsupported meta type {type(meta)!r}; "
        "no factory registered in shot_result_from_raw_and_meta()."
    )
