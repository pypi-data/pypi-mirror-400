import h5py
import numpy as np
from h5py import Group
from typing import List
from scanner3d.zemod.iar.grid_meta import GridMeta


def _write_grid_meta_array(meta_grp: Group, metas: list[GridMeta]) -> None:
    n = len(metas)

    # numeric fields
    meta_grp.create_dataset(
        "min_x", data=np.asarray([m.min_x for m in metas], dtype=float)
    )
    meta_grp.create_dataset(
        "min_y", data=np.asarray([m.min_y for m in metas], dtype=float)
    )
    meta_grp.create_dataset(
        "dx", data=np.asarray([m.dx for m in metas], dtype=float)
    )
    meta_grp.create_dataset(
        "dy", data=np.asarray([m.dy for m in metas], dtype=float)
    )

    # string fields (vlen UTF-8)
    vlen_str = h5py.string_dtype(encoding="utf-8")
    meta_grp.create_dataset(
        "description",
        data=[m.description for m in metas],
        dtype=vlen_str,
    )
    meta_grp.create_dataset(
        "x_label",
        data=[m.x_label for m in metas],
        dtype=vlen_str,
    )
    meta_grp.create_dataset(
        "y_label",
        data=[m.y_label for m in metas],
        dtype=vlen_str,
    )
    meta_grp.create_dataset(
        "value_label",
        data=[m.value_label for m in metas],
        dtype=vlen_str,
    )


def _read_grid_meta_array(meta_grp: Group, n_shots: int) -> List[GridMeta]:
    """
    Read per-shot GridMeta saved as 1D datasets in `meta_grp`.

    Expected datasets (all length n_shots):
      - "min_x", "min_y", "dx", "dy" (float)
      - "description", "x_label", "y_label", "value_label" (string)
    """

    min_x = np.asarray(meta_grp["min_x"][...], dtype=float)
    min_y = np.asarray(meta_grp["min_y"][...], dtype=float)
    dx    = np.asarray(meta_grp["dx"][...],    dtype=float)
    dy    = np.asarray(meta_grp["dy"][...],    dtype=float)

    # safer: use asstr() so you always get Python str, not bytes
    description = meta_grp["description"].asstr()[...]
    x_label     = meta_grp["x_label"].asstr()[...]
    y_label     = meta_grp["y_label"].asstr()[...]
    value_label = meta_grp["value_label"].asstr()[...]

    if not (min_x.size == n_shots == min_y.size == dx.size == dy.size):
        raise ValueError(
            f"GridMeta arrays have inconsistent length: "
            f"min_x={min_x.size}, min_y={min_y.size}, dx={dx.size}, "
            f"dy={dy.size}, expected {n_shots}"
        )

    metas: List[GridMeta] = []
    for k in range(n_shots):
        metas.append(
            GridMeta(

                min_x=float(min_x[k]),
                min_y=float(min_y[k]),
                dx=float(dx[k]),
                dy=float(dy[k]),
                description=str(description[k]),
                x_label=str(x_label[k]),
                y_label=str(y_label[k]),
                value_label=str(value_label[k]),
            )
        )

    return metas