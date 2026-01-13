from __future__ import annotations
import logging
from numbers import Integral
import numpy as np
from pathlib import Path
from typing import Optional, Sequence, TYPE_CHECKING, Iterator, overload
from numbers import Real
from allytools.units.length import Length
from scanner3d.afs.frame import Frame
from scanner3d.h5.album.album_save import album_save
from scanner3d.h5.album.album_load import album_load
from scanner3d.scanner.scanner_ref import ScannerRef
from scanner3d.test.base.album_settings import AlbumSettings

if TYPE_CHECKING:
    from scanner3d.tuner.tuner import Tuner
    from scanner3d.zemod.zemod_analysis import ZeModAnalysis
    from scanner3d.test.base.analysis_settings import AnalysisSettings

log = logging.getLogger(__name__)
class Album:
    __slots__ = ("_frames", "_z_seq", "_path", "_n_frames", "_camera_ref", "_album_settings")

    def __init__(
            self,
            *,
            album_settings: AlbumSettings,
            frames: list[Frame],
            z_seq: Sequence[Length],
            path: Optional[Path] = None,
            camera_ref: ScannerRef | None = None,
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Direct construction of PsfBank is not allowed. "
                "Use PsfBank.compute(...) or PsfBank.load(...)."
            )
        self._album_settings = album_settings
        self._frames = list(frames)
        self._z_seq = list(z_seq)
        self._path = path
        self._n_frames = len(frames)
        self._camera_ref = camera_ref

    @property
    def album_settings(self) -> AlbumSettings:
        return self._album_settings

    @property
    def frames(self) -> list[Frame]:
        return self._frames

    @property
    def z_seq(self) -> list[Length]:
        return self._z_seq

    def z_seq_mm(self) -> np.ndarray:
        return np.array([z.value_mm for z in self._z_seq], dtype=float)

    @property
    def path(self) -> Optional[Path]:
        return self._path

    @property
    def n_frames(self) -> int:
        return self._n_frames

    @property
    def camera_ref(self) -> ScannerRef:
        return self._camera_ref


    def __iter__(self) -> Iterator[Frame]:
        return iter(self._frames)

    def __len__(self) -> int:
        return self.n_frames

    @overload
    def __getitem__(self, item: Length) -> Frame: ...
    @overload
    def __getitem__(self, item: slice) -> list[Frame]: ...
    @overload
    def __getitem__(self, item: int) -> Frame: ...

    def __getitem__(self, item):

        if isinstance(item, Length):
            return self.get_nearest(item)
        if isinstance(item, Integral):
            return self._frames[item]  # will raise IndexError naturally if out of range
        if isinstance(item, slice):
            return self._frames[item]

        raise TypeError(
            f"Unsupported index type for PSF Album: {type(item)!r}; "
            f"use Length (for nearest-z), int (for direct index), or a slice.")

    def get_nearest(self, z: Length) -> Frame:
        if not self._z_seq:
            raise ValueError("PSF Album has no z sequence; cannot search nearest frame.")
        z_mm = self.z_seq_mm()
        target_mm = z.value_mm
        eligible = z_mm[z_mm <= target_mm]
        if eligible.size > 0:
            chosen_z = eligible.max()
        else:
            chosen_z = z_mm.min()
        idx = int(np.where(z_mm == chosen_z)[0][0])
        psf = self._frames[idx]
        log.info("Requested Z=%s → selected frame %.3f mm (index %d)",z, chosen_z, idx)
        return psf

    @classmethod
    def load(cls, path: Path | str) -> "Album":
        return album_load(Path(path))

    def save(self, path: Path | str, **kwargs):
        album_save(album=self, path=Path(path), **kwargs)
        self._path = Path(path)


    @classmethod
    def from_components(
            cls,
            *,
            album_settings: AlbumSettings,
            frames: list[Frame],
            z_seq: Sequence[Length],
            path: Optional[Path] = None,
            camera_ref: ScannerRef | None = None) -> Album:
        return cls(frames=list(frames),z_seq=list(z_seq),path=path,camera_ref=camera_ref, album_settings=album_settings, _internal=True)

    @classmethod
    def compute(
            cls,
            *,
            tuner: Tuner,
            analysis: ZeModAnalysis,
            analysis_settings: AnalysisSettings,
            album_settings: AlbumSettings,
            z_seq: Sequence[Length],
            x_seq,
            y_seq) -> "Album":
        frames: list[Frame] = []
        z_row = tuner.sm.get_wd_row() #ask tuner for surface (row) in LDE for set working distance
        field = tuner.fm.get_test_field()  #ask tuner which field used for test
        for z in z_seq:
            z_row.thickness = z.value_mm
            profile = tuner.get_profile()
            psf_slice = Frame.compute(
                field=field,
                analysis=analysis,
                analysis_settings= analysis_settings,
                x_seq=x_seq,
                y_seq=y_seq,
                profile=profile,
                z= z
            )
            log.debug("PSF Frame @ %.2f mm created", z.value_mm)
            frames.append(psf_slice)
        return cls(
            frames=frames,
            z_seq=z_seq,
            camera_ref=tuner.scanner_ref,
            _internal=True,
            album_settings=album_settings,
        )

    def __str__(self) -> str:
        if not self._z_seq:
            return "📘 PSF Album (empty)>"

        z_mm = sorted(self.z_seq_mm())
        n = len(z_mm)
        lines = [
            "📘 PSF Album",
            "────────────────────────────",
            f"  File: {self._path.name if self._path else '(unsaved)'}",
            f"  Number of frames: {n}",
            f"  Range: {z_mm[0]:.2f} mm → {z_mm[-1]:.2f} mm",
        ]
        return "\n".join(lines)

    def __repr__(self) -> str:
        if not self._z_seq:
            return "PSF Album"
        z_mm = sorted(self.z_seq_mm())
        return f"PSF Album {len(z_mm)} frames {z_mm[0]:.2f}–{z_mm[-1]:.2f} mm>"
