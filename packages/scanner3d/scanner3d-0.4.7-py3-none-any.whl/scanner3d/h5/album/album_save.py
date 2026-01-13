from __future__ import annotations
import h5py
import numpy as np
from pathlib import Path
from typing import Optional, Literal, TYPE_CHECKING
from scanner3d.h5.h5aid import resolve_h5_name
from scanner3d.h5.camera_ref_to_h5 import save_camera_ref
from scanner3d.h5.frame.frame_write import frame_write
from scanner3d.h5.album.album_format import AlbumH5, ALBUM_H5_VERSION
from scanner3d.h5.h5aid import frame_name
from scanner3d.h5.album.album_settings_to_h5 import save_album_settings

if TYPE_CHECKING:
    from scanner3d.analysis.album import Album

def album_save(
    *,
    album: Album,
    path: Path,
    compression: Optional[str] = "gzip",
    compression_opts: Optional[int] = 4,
    append: bool = False,
    on_conflict: Literal["error", "overwrite", "skip", "rename"] = "error",
) -> None:
    mode = "a" if append and path.exists() else "w"

    if album.z_seq is None:
        raise ValueError("Album.z_seq is None; cannot save z_seq.")
    if len(album.z_seq) != len(album.frames):
        raise ValueError(
            f"Length mismatch: z_seq ({len(album.z_seq)}) vs "
            f"frames ({len(album.frames)}).")

    with h5py.File(path, mode) as f:
        f.attrs[AlbumH5.FORMAT_VERSION] = ALBUM_H5_VERSION
        frames_grp = f.require_group(AlbumH5.FRAMES)
        for frame in album.frames:
            base = frame_name(frame)
            name, skip = resolve_h5_name(
                container=frames_grp,
                base=base,
                on_conflict=on_conflict,
                what="PSF frame group")
            if skip:
                continue
            grp = frames_grp.create_group(name)
            frame_write(
                grp, frame, compression=compression, compression_opts=compression_opts
            )
        settings_grp = f.create_group(AlbumH5.ALBUM_SETTINGS)
        save_album_settings(settings_grp, album.album_settings)
        z_grp = f.create_group(AlbumH5.Z_SEQ)
        z_ds = z_grp.create_dataset(AlbumH5.Z_VALUES,data=np.asarray(album.z_seq_mm(), dtype=float))
        z_grp.attrs[AlbumH5.Z_UNITS] = "mm"
        z_ds.attrs[AlbumH5.Z_DESC] = "Working distance sequence (z) for PSF frames"
        scanner_grp = f.create_group(AlbumH5.SCANNER)
        save_camera_ref(scanner_grp=scanner_grp, ref=album.camera_ref)