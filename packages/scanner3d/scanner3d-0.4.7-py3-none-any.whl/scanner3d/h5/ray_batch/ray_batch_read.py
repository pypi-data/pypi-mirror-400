from __future__ import annotations
import h5py
from types import SimpleNamespace
from typing import Callable, TYPE_CHECKING
from pathlib import Path
from h5py import Group
import numpy as np
import h5py
from scanner3d.ray_trace.ray_batch_type import RayBatchType
from scanner3d.h5.ray_batch.ray_batch_format import RayBatchH5, RAYBATCH_H5_VERSION
from allytools.h5 import require_h5_version
if TYPE_CHECKING:
    from scanner3d.ray_trace.ray_batch import RayBatch, T_Ray


def ray_batch_load(
    path: Path | str,
    *,
    group_name: str | None = None,
    ray_factory: Callable[[dict[str, float]], T_Ray] | None = None,
) -> RayBatch[T_Ray]:

    path = Path(path)
    if group_name is None:
        group_name = RayBatchH5.GROUP

    with h5py.File(path, "r") as f:
        if group_name not in f:
            raise KeyError(f"Missing group '{group_name}' in {path}")
        grp = f[group_name]
        return ray_batch_read(grp, ray_factory=ray_factory)


def ray_batch_read(
    grp: Group,
    ray_factory: Callable[[dict[str, float]],T_Ray] | None = None,
) -> RayBatch[T_Ray]:

    require_h5_version(grp, attr=RayBatchH5.FORMAT_VERSION, expected=RAYBATCH_H5_VERSION)
    grid = tuple(int(v) for v in np.asarray(grp[RayBatchH5.GRID][...], dtype=int))
    to_surface = int(np.asarray(grp[RayBatchH5.TO_SURFACE][...], dtype=int))
    wave_number = int(np.asarray(grp[RayBatchH5.WAVE_NUMBER][...], dtype=int))
    rays_type = grp.attrs.get(RayBatchH5.RAYS_TYPE, "unknown")
    method = grp.attrs.get(RayBatchH5.METHOD, "unknown")
    process_time = grp.attrs.get(RayBatchH5.PROCESS_TIME, None)
    if process_time is not None:
        process_time = float(process_time)

    batch_type_attr = grp.attrs.get(RayBatchH5.BATCH_TYPE, "unknown")
    if isinstance(batch_type_attr, bytes):
        batch_type_attr = batch_type_attr.decode("utf-8")
    try:
        batch_type = RayBatchType[batch_type_attr]
    except Exception:
        batch_type = batch_type_attr

    x_lin = np.asarray(grp[RayBatchH5.X_LIN][...], dtype=float)
    y_lin = np.asarray(grp[RayBatchH5.Y_LIN][...], dtype=float)

    field_names = [s.decode("utf-8") if isinstance(s, (bytes, bytearray)) else str(s)
                   for s in grp[RayBatchH5.FIELD_NAMES][...]]
    values = np.asarray(grp[RayBatchH5.VALUES][...], dtype=float)  # (N, n_fields)

    n, n_fields = values.shape
    if n_fields != len(field_names):
        raise ValueError(
            f"Inconsistent RayBatch: values.shape[1]={n_fields}, "
            f"len(field_names)={len(field_names)}")

    if ray_factory is None:
        ray_factory = lambda d: SimpleNamespace(**d)

    rays: list[T_Ray] = []
    for k in range(n):
        row_vals = values[k, :]
        d = {name: float(val) for name, val in zip(field_names, row_vals)}
        rays.append(ray_factory(d))
    from scanner3d.ray_trace.ray_batch import RayBatch, T_Ray

    return RayBatch[T_Ray](
        batch_type=batch_type,
        method=method,
        rays_type=rays_type,
        grid=grid,
        to_surface=to_surface,
        wave_number=wave_number,
        rays=rays,
        x_lin=x_lin,
        y_lin=y_lin,
        process_time=process_time,
    )
