from __future__ import annotations
import numpy as np
import logging
from typing import Sequence, TYPE_CHECKING, Optional
from allytools.units import  Length
from scanner3d.tuner.profile import Profile
from scanner3d.afs.shot import Shot
from scanner3d.afs.frame_meta import FrameMeta


if TYPE_CHECKING:
    from scanner3d.zemod.zemod_field import ZeModField
    from scanner3d.zemod.zemod_analysis import ZeModAnalysis
    from scanner3d.test.base.analysis_settings import AnalysisSettings


log = logging.getLogger(__name__)
class Frame:
    __slots__ = ("_shots", "_x_seq", "_y_seq", "_meta", "_profile", "_values", "_z")

    def __init__(
        self,
        *,
        shots: list[Shot],
        x_seq: Sequence[Length],
        y_seq: Optional[Sequence[Length]],
        meta: FrameMeta,
        profile: Profile,
        z: Length,
        _internal: bool = False,
    ) -> None:
        if not _internal:
            raise RuntimeError(
                "Direct construction of Frame is not allowed. "
                "Use compute(...) to calculate it from Zemax, or from_components() to reconstruct it.")

        self._shots = shots
        self._x_seq = list(x_seq)
        self._y_seq = list(y_seq)
        self._meta = meta
        self._profile = profile
        self._z = z
        if shots:
            shapes = {shot.raw_data.shape for shot in shots}
            if len(shapes) != 1:
                raise ValueError(f"All shots in a Frame must have the same raw_data.shape, got: {shapes}")
            self._values = np.stack([shot.raw_data for shot in shots])
        else:
            self._values = np.empty((0, 0, 0), dtype=float)  # -> (n_shots, Ny, Nx)

    @classmethod
    def from_components(
        cls,
        *,
        shots: list[Shot],
        x_seq: Sequence[Length],
        y_seq: Optional[Sequence[Length]],
        profile: Profile,
        z: Length,
        meta: FrameMeta | None = None,
    ) -> "Frame":
        return cls(
            shots=shots,
            x_seq=x_seq,
            y_seq=y_seq,
            meta=meta,
            profile=profile,
            z=z,
            _internal=True,
        )

    @classmethod
    def compute(
        cls,
        *,
        field: ZeModField,
        analysis: ZeModAnalysis,
        analysis_settings: AnalysisSettings,
        x_seq: Optional[Sequence[Length]],
        y_seq: Optional[Sequence[Length]],
        profile: Profile,
        z: Length,
    ) -> "Frame":
        if x_seq is None and y_seq is None:
            raise ValueError("Provide x_seq and/or y_seq (x for 1D-X, y for 1D-Y, both for 2D).")
        x_list: list[Length] | None = list(x_seq) if x_seq is not None else None
        y_list: list[Length] | None = list(y_seq) if y_seq is not None else None

        # 1️⃣ 2D CASE — both x_seq and y_seq provided
        if x_list is not None and y_list is not None:
            xs: list[Length] = []
            ys: list[Length] = []
            for yv in y_list:
                for xv in x_list:
                    xs.append(xv)
                    ys.append(yv)
            x_meta = x_list
            y_meta = y_list

        # 2️⃣ 1D CASE — scan along X (y = 0 mm)
        elif x_list is not None:
            zero = Length(0.0)
            xs = x_list
            ys = [zero for _ in x_list]
            x_meta = x_list
            y_meta = [zero]

        # 3️⃣ 1D CASE — scan along Y (x = 0 mm)
        else:
            assert y_list is not None  # since we checked both None above
            zero = Length(0.0)
            ys = y_list
            xs = [zero for _ in y_list]
            x_meta = [zero]
            y_meta = y_list

        shots: list[Shot] = []
        for xv, yv in zip(xs, ys):
            shot = Shot.compute(
                field=field,
                analysis=analysis,
                analysis_settings=analysis_settings,
                x=xv,
                y=yv)
            shots.append(shot)

        meta = FrameMeta.from_shots(shots=shots)

        return cls(
            shots=shots,
            x_seq=x_meta,
            y_seq=y_meta,
            meta=meta,
            profile=profile,
            z=z,
            _internal=True,
        )

    @property
    def shots(self) -> list[Shot]:
        return self._shots

    @property
    def x_seq(self) -> list[Length]:
        return self._x_seq

    @property
    def y_seq(self) -> list[Length]:
        return self._y_seq

    @property
    def meta(self) -> FrameMeta:
        return self._meta

    @property
    def profile(self) -> Profile:
        return self._profile

    @property
    def values(self) -> np.ndarray:
        return self._values

    @property
    def z(self) -> Length:
        return self._z

    @property
    def z_mm(self) -> float:
        return self._z.value_mm

    @property
    def x_seq_mm(self) -> np.ndarray:
        return np.array([v.value_mm for v in self._x_seq], dtype=float)

    @property
    def y_seq_mm(self) -> np.ndarray:
        return np.array([v.value_mm for v in self._y_seq], dtype=float)

    @property
    def n_rows(self) -> int:
        return len(self._y_seq)

    @property
    def n_cols(self) -> int:
        return len(self._x_seq)

    def top_right_shot(self) -> Shot:
        return self[self.n_rows - 1, self.n_cols - 1]

    def __call__(self, row: int, col: int) -> Shot:
        """
        Return the Shot at grid position (row, col).
        row = index into y_seq
        col = index into x_seq
        """
        nx = len(self._x_seq)
        idx = row * nx + col
        return self._shots[idx]

    def __getitem__(self, idx):
        """
        Access PSF shots in the frame.

        Supports:
            frame[i]          -> 1D flat index (0 .. N-1)
            frame[row, col]   -> 2D grid index
                                 row: Y index (0 .. len(y_seq) - 1)
                                 col: X index (0 .. len(x_seq) - 1)
        """
        if isinstance(idx, tuple) and len(idx) == 2:
            row, col = idx
            n_cols = len(self._x_seq)
            n_rows = len(self._y_seq)
            if not (0 <= row < n_rows and 0 <= col < n_cols):
                raise IndexError(
                    f"Grid index out of range: row={row}, col={col}, "
                    f"valid rows [0..{n_rows - 1}], cols [0..{n_cols - 1}]")
            i = row * n_cols + col
            return self._shots[i]
        return self._shots[idx]

    def __str__(self) -> str:
        x_arr = np.array([v.value_mm for v in self._x_seq], dtype=float)
        y_arr = np.array([v.value_mm for v in self._y_seq], dtype=float)
        z_mm = self._z.value_mm
        parts = [
            "🖼️ PSF Frame",
            "────────────────────────────",
            f"  z: {z_mm:.2f} mm",
            f"  x: shape={x_arr.shape}, "
            f"min={np.nanmin(x_arr):.4g}, max={np.nanmax(x_arr):.4g} mm,",
            f"  y: shape={y_arr.shape}, "
            f"min={np.nanmin(y_arr):.4g}, max={np.nanmax(y_arr):.4g} mm,",
            f"  total shots: {len(self._shots)},",
            f"  values shape: {self._values.shape},",
            f"  meta: {self._meta}"]
        return "\n".join(parts)

    def plot(self, *args, **kwargs):
        from scanner3d.afs.plotter import plot_frame
        return plot_frame(self, *args, **kwargs)