import h5py
import numpy as np
from pathlib import Path
from typing import TYPE_CHECKING

from allytools.units import Length
from scanner3d.afs.frame import Frame
from scanner3d.h5.camera_ref_to_h5 import load_camera_ref
from scanner3d.h5.frame.frame_read import frame_read
from scanner3d.h5.album.album_format import AlbumH5, ALBUM_H5_VERSION
from scanner3d.h5.album.album_settings_to_h5 import load_album_settings
from allytools.h5 import require_h5_version

if TYPE_CHECKING:
    from scanner3d.afs.album import Album


def album_load(path: Path) -> "Album":
    from scanner3d.afs.album import Album

    path = Path(path)
    with h5py.File(path) as f:
        require_h5_version(f, attr=AlbumH5.FORMAT_VERSION, expected=ALBUM_H5_VERSION)
        if AlbumH5.FRAMES not in f:
            raise KeyError(f"Missing '{AlbumH5.FRAMES}' group in {path}.")
        frames_grp = f[AlbumH5.FRAMES]
        frame_names = list(frames_grp.keys())
        if not frame_names:
            raise ValueError(f"No PSF frame groups found in {path} under /{AlbumH5.FRAMES}.")
        if AlbumH5.Z_SEQ not in f or AlbumH5.Z_VALUES not in f[AlbumH5.Z_SEQ]:
            raise KeyError(
                f"Missing '{AlbumH5.Z_SEQ}/{AlbumH5.Z_VALUES}' in file; "
                f"cannot reconstruct z_seq.")

        # z-sequence as stored in the file (may be unsorted / old order)
        z_seq_mm = np.asarray(
            f[AlbumH5.Z_SEQ][AlbumH5.Z_VALUES][:],
            dtype=float,)

        if len(z_seq_mm) != len(frame_names):
            raise ValueError(
                f"Mismatch: z_seq length ({len(z_seq_mm)}) != "
                f"number of PSF frame groups ({len(frame_names)}).")

        if AlbumH5.ALBUM_SETTINGS in f:
            album_settings = load_album_settings(f[AlbumH5.ALBUM_SETTINGS])
        else:
            raise KeyError("Missing album_settings in H5 file")

        frames_raw: list[Frame] = []
        z_from_frame: list[float] = []
        for name in frame_names:
            grp = frames_grp[name]
            frame = frame_read(grp)
            frames_raw.append(frame)
            z_from_frame.append(frame.z.value_mm)

        z_from_frame_arr = np.asarray(z_from_frame, dtype=float)

        # --- reorder frames to align with z_seq_mm from file ---
        frames_ordered: list[Frame] = [None] * len(z_seq_mm)  # type: ignore
        used: set[int] = set()

        for i, target_z in enumerate(z_seq_mm):
            candidates = np.where(
                np.isclose(z_from_frame_arr, target_z, rtol=0.0, atol=1e-9)
            )[0]
            candidates = [j for j in candidates if j not in used]
            if not candidates:
                raise ValueError(
                    f"Could not match z={target_z:.6f} mm from z_seq to any frame.z; "
                    f"z_from_frame={z_from_frame_arr}"
                )
            j = int(candidates[0])
            used.add(j)
            frames_ordered[i] = frames_raw[j]

        # scanner ref
        scanner_grp = f[AlbumH5.SCANNER]
        camera_ref = load_camera_ref(scanner_grp)


    z_mm_from_frames = np.array(
        [frame.z.value_mm for frame in frames_ordered],
        dtype=float)
    sort_idx = np.argsort(z_mm_from_frames)
    frames_sorted: list[Frame] = [frames_ordered[i] for i in sort_idx]
    z_seq: list[Length] = [frame.z for frame in frames_sorted]

    return Album.from_components(
        frames=frames_sorted,
        z_seq=z_seq,
        path=path,
        camera_ref=camera_ref,
        album_settings=album_settings,
    )
