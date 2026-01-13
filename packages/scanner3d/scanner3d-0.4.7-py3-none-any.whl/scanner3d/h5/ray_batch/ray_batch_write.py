from __future__ import annotations
from typing import Any, Sequence, Optional, TYPE_CHECKING
from pathlib import Path
from h5py import Group
import numpy as np
import h5py
from scanner3d.h5.h5aid import suggest_chunks
from scanner3d.h5.ray_batch.ray_batch_format import RayBatchH5, RAYBATCH_H5_VERSION

if TYPE_CHECKING:
    from scanner3d.ray_trace.ray_batch import RayBatch

def _infer_numeric_fields(rays: Sequence[Any]) -> list[str]:
    """
    Inspect first ray and take all attributes that look like scalar numeric
    (int/float/np.floating). Non-numeric stuff (flags, enums) are ignored.
    """
    if not rays:
        raise ValueError("Cannot infer fields from empty rays list.")
    first = rays[0]
    fields: list[str] = []
    for name, value in vars(first).items():
        if isinstance(value, (int, float, np.floating)):
            fields.append(name)
    if not fields:
        raise ValueError("No numeric fields found on ray objects.")
    return fields


def _stack_values(rays: Sequence[Any], fields: list[str]) -> np.ndarray:
    data = []
    for r in rays:
        row = [float(getattr(r, f)) for f in fields]
        data.append(row)
    return np.asarray(data, dtype=float)  # shape (N, n_fields)

def ray_batch_write(
    grp: Group,
    batch: RayBatch[Any],
    *,
    compression: Optional[str],
    compression_opts: Optional[int]) -> None:
    grp.attrs[RayBatchH5.FORMAT_VERSION] = RAYBATCH_H5_VERSION
    grp.create_dataset(RayBatchH5.GRID, data=np.asarray(batch.grid, dtype=int))
    grp.create_dataset(RayBatchH5.TO_SURFACE, data=int(batch.to_surface))
    grp.create_dataset(RayBatchH5.WAVE_NUMBER, data=int(batch.wave_number))
    rays_type_name = getattr(batch.rays_type, "name", str(batch.rays_type))
    method_name = getattr(batch.method, "name", str(batch.method))
    grp.attrs[RayBatchH5.RAYS_TYPE] = rays_type_name
    grp.attrs[RayBatchH5.METHOD] = method_name
    if batch.process_time is not None:
        grp.attrs[RayBatchH5.PROCESS_TIME] = float(batch.process_time)

    batch_type_name = getattr(batch.batch_type, "name", str(batch.batch_type))
    grp.attrs[RayBatchH5.BATCH_TYPE] = batch_type_name
    if batch.x_lin is None or batch.y_lin is None:
        raise ValueError("RayBatch.x_lin / y_lin must not be None for H5 export.")
    grp.create_dataset(RayBatchH5.X_LIN, data=np.asarray(batch.x_lin, dtype=float))
    grp.create_dataset(RayBatchH5.Y_LIN, data=np.asarray(batch.y_lin, dtype=float))


    fields = _infer_numeric_fields(batch.rays)
    values = _stack_values(batch.rays, fields)   # (N, n_fields)
    ds_chunks = suggest_chunks(values.shape)

    dt = h5py.string_dtype(encoding="utf-8")
    grp.create_dataset(RayBatchH5.FIELD_NAMES, data=np.asarray(fields, dtype=dt))

    if compression is not None:
        grp.create_dataset(
            RayBatchH5.VALUES,
            data=values,
            compression=compression,
            compression_opts=compression_opts,
            chunks=ds_chunks,
        )
    else:
        grp.create_dataset(
            RayBatchH5.VALUES,
            data=values,
            chunks=ds_chunks,
        )


def ray_batch_save(
    *,
    batch: RayBatch[Any],
    path: Path | str,
    compression: Optional[str] = "gzip",
    compression_opts: Optional[int] = 4,
    group_name: str | None = None,
) -> str:
    path = Path(path)
    if group_name is None:
        group_name = RayBatchH5.GROUP
    with h5py.File(path, "w") as f:
        grp = f.create_group(group_name)
        ray_batch_write(grp, batch, compression=compression, compression_opts=compression_opts)
    return group_name
