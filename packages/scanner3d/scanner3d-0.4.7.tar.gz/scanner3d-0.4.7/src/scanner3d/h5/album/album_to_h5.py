from __future__ import annotations
import h5py
import numpy as np
from pathlib import Path
from typing import Optional, Literal, TYPE_CHECKING
from allytools.units import Length
from scanner3d.analysis.frame import Frame
from scanner3d.h5.resolve_h5_name import resolve_h5_name
from scanner3d.h5.camera_ref_to_h5 import load_camera_ref, save_camera_ref
from scanner3d.h5.frame_to_h5 import write_frame, read_frame
from scanner3d.h5.album_h5 import AlbumH5, ALBUM_H5_VERSION
from scanner3d.h5.h5aid import frame_name
from scanner3d.h5.album_settings_to_h5 import save_album_settings, load_album_settings
from allytools.h5 import require_h5_version

if TYPE_CHECKING:
    from scanner3d.analysis.album import Album

def save_album(
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
            write_frame(
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

def load_album(path: Path) -> "Album":
    from scanner3d.analysis.album import Album

    path = Path(path)
    with h5py.File(path, "r") as f:
        require_h5_version(f, attr=AlbumH5.FORMAT_VERSION, expected=ALBUM_H5_VERSION)
        if AlbumH5.FRAMES not in f:
            raise KeyError(f"Missing '{AlbumH5.FRAMES}' group in {path}.")
        frames_grp = f[AlbumH5.FRAMES]
        frame_names = list(frames_grp.keys())
        if not frame_names:
            raise ValueError(f"No PSF frame groups found in {path} under /{AlbumH5.FRAMES}.")
        if AlbumH5.Z_SEQ not in f or AlbumH5.Z_VALUES not in f[AlbumH5.Z_SEQ]:
            raise KeyError(
                f"Missing '{AlbumH5.Z_SEQ}/{AlbumH5.Z_VALUES}' in file; cannot reconstruct z_seq."
            )
        z_seq_mm = np.asarray(
            f[AlbumH5.Z_SEQ][AlbumH5.Z_VALUES][:],
            dtype=float,
        )
        if len(z_seq_mm) != len(frame_names):
            raise ValueError(
                f"Mismatch: z_seq length ({len(z_seq_mm)}) != "
                f"number of PSF frame groups ({len(frame_names)})."
            )
        if AlbumH5.ALBUM_SETTINGS in f:
            album_settings = load_album_settings(f[AlbumH5.ALBUM_SETTINGS])
        else:
            raise KeyError("Missing album_settings in H5 file")
        frames: list[Frame] = []
        for name in frame_names:
            grp = frames_grp[name]
            frame = read_frame(grp)
            frames.append(frame)
        scanner_grp = f[AlbumH5.SCANNER]
        camera_ref = load_camera_ref(scanner_grp)
        z_seq: list[Length] = [Length(z) for z in z_seq_mm]
    return Album.from_components(frames=frames,z_seq=z_seq,path=path,camera_ref=camera_ref,album_settings=album_settings)