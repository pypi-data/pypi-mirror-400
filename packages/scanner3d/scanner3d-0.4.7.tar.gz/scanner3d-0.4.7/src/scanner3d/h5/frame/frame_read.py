from __future__ import annotations
import numpy as np
from typing import List
from h5py import Group
from scanner3d.afs.frame import Frame, FrameMeta
from scanner3d.afs.shot import Shot
from scanner3d.afs.i_shot_meta import IShotMeta
from scanner3d.tuner.profile import Profile
from scanner3d.h5.frame.frame_format import FrameH5, FRAME_H5_VERSION
from scanner3d.h5.shot.shot_factories import shot_result_from_raw_and_meta
from allytools.units import Length
from allytools.h5 import (
    require_h5_version,
    attribute_read,
    dataclass_list_read,
)


def frame_read(grp: Group) -> Frame:
    require_h5_version(
        grp,
        attr=FrameH5.FORMAT_VERSION,
        expected=FRAME_H5_VERSION)

    values = np.asarray(grp[FrameH5.RESULT_VALUES][...], dtype=float)
    x_seq_mm = np.asarray(grp[FrameH5.X_SEQ][...], dtype=float)
    y_seq_mm = np.asarray(grp[FrameH5.Y_SEQ][...], dtype=float)
    z_mm = float(grp[FrameH5.Z][()])
    n_shots = values.shape[0]
    nx_seq = x_seq_mm.size
    ny_seq = y_seq_mm.size
    if nx_seq * ny_seq != n_shots:
        raise ValueError(f"Inconsistent frame: nx*ny={nx_seq * ny_seq}, "
            f"but values.shape[0]={n_shots}")
    profile_grp = grp[FrameH5.TUNER_PROFILE]
    profile = attribute_read(profile_grp, Profile)

    meta_grp = grp[FrameH5.RESULT_META]
    metas: List[IShotMeta] = dataclass_list_read(meta_grp)

    if len(metas) != n_shots:
        raise ValueError(
            f"Inconsistent frame: have {len(metas)} meta entries "
            f"but {n_shots} value slices.")

    shots: List[Shot] = []
    for k, meta in enumerate(metas):
        row, col = divmod(k, nx_seq)
        x = float(x_seq_mm[col])
        y = float(y_seq_mm[row])
        raw_k = values[k, ...]
        result = shot_result_from_raw_and_meta(raw_k, meta)
        shot = Shot.from_components(
            result=result,
            field_x=Length(x),
            field_y=Length(y),
        )
        shots.append(shot)


    frame_meta = FrameMeta.from_shots(shots)
    x_seq: list[Length] = [Length(v) for v in x_seq_mm]
    y_seq: list[Length] = [Length(v) for v in y_seq_mm]
    z = Length(z_mm)

    return Frame.from_components(
        shots=shots,
        x_seq=x_seq,
        y_seq=y_seq,
        meta=frame_meta,
        profile=profile,
        z=z)
