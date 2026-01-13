import h5py
import numpy as np
from pathlib import Path
from typing import Optional
from h5py import Group
from scanner3d.afs.frame import Frame
from scanner3d.h5.h5aid import suggest_chunks
from scanner3d.h5.frame.frame_format import FrameH5, FRAME_H5_VERSION
from allytools.h5 import attribute_write, dataclass_list_write

def frame_write(
    grp: Group,
    frame: Frame,
    *,
    compression: Optional[str],
    compression_opts: Optional[int],
) -> None:
    shots = frame.shots
    n_shots = len(shots)
    if n_shots == 0:
        raise ValueError("Frame has no shots; nothing to save.")

    values = np.stack([s.raw_data for s in shots])
    metas = np.stack([s.meta for s in shots])
    ds_chunks = suggest_chunks(values.shape)
    if compression is not None:
        grp.create_dataset(
            FrameH5.RESULT_VALUES,
            data=values,
            compression=compression,
            compression_opts=compression_opts,
            chunks=ds_chunks)

    else:
        grp.create_dataset(
            FrameH5.RESULT_VALUES,
            data=values,
            chunks=ds_chunks)
    meta_grp = grp.create_group(FrameH5.RESULT_META)
    dataclass_list_write(meta_grp, metas, compression=compression)
    grp.create_dataset(FrameH5.X_SEQ, data=np.asarray(frame.x_seq_mm, dtype=float))
    grp.create_dataset(FrameH5.Y_SEQ, data=np.asarray(frame.y_seq_mm, dtype=float))
    grp.create_dataset(FrameH5.Z, data=frame.z_mm)
    sys_grp = grp.create_group(FrameH5.TUNER_PROFILE)
    attribute_write(sys_grp, frame.profile)
    grp.attrs[FrameH5.FORMAT_VERSION] = FRAME_H5_VERSION


def frame_save(
    *,
    frame: Frame,
    path: Path | str,
    compression: Optional[str] = "gzip",
    compression_opts: Optional[int] = 4,
) -> None:
    """
    Save a single Frame to an HDF5 file.
    Creates/overwrites the file at `path` and writes the frame into the root group.
    """
    p = Path(path)
    with h5py.File(p, "w") as f:
        frame_write(
            f,
            frame,
            compression=compression,
            compression_opts=compression_opts,
        )
