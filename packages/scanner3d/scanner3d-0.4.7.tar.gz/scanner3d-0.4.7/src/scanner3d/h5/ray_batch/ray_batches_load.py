from __future__ import annotations
import h5py
from pathlib import Path
from typing import TYPE_CHECKING
from scanner3d.h5.ray_batch.ray_batch_read import ray_batch_read
from scanner3d.h5.ray_batch.ray_batches_format import BatchesH5, RAYBATCH_COLLECTION_H5_VERSION
if TYPE_CHECKING:
    from scanner3d.ray_trace.ray_batches import RayBatches

def ray_batches_load(path: Path | str) -> "RayBatches":
    from scanner3d.ray_trace.ray_batches import RayBatches
    path = Path(path)
    with h5py.File(path, "r") as f:
        if BatchesH5.BATCHES not in f:
            raise KeyError(f"Missing group '{BatchesH5.BATCHES}' in file {path}")

        batches_grp = f[BatchesH5.BATCHES]
        version = batches_grp.attrs.get("format_version")
        if version != RAYBATCH_COLLECTION_H5_VERSION:
            raise ValueError(
                f"Incompatible version: {version!r}, "
                f"expected {RAYBATCH_COLLECTION_H5_VERSION!r}")
        declared_n = batches_grp.attrs.get("n_batches")
        group_names = sorted(batches_grp.keys())
        if declared_n is not None and declared_n != len(group_names):
            raise ValueError(
                f"n_batches mismatch: header says {declared_n}, "
                f"found {len(group_names)} sub-groups")
        batches = RayBatches()
        for name in group_names:
            grp = batches_grp[name]
            batch = ray_batch_read(grp)
            batches.append(batch)
    return batches