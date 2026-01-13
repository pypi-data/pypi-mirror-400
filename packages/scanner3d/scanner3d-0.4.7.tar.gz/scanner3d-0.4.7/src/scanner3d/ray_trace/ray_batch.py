from __future__ import annotations
import numpy as np
from pathlib import  Path
from dataclasses import dataclass
from typing import Generic, List, Tuple, Iterable, Any
from scanner3d.ray_trace.raytrace_settings import RayTraceSettings
from scanner3d.ray_trace.generic_ray_tracer import T_Ray
from scanner3d.ray_trace.ray_batch_type import RayBatchType
from scanner3d.h5.ray_batch.ray_batch_write import ray_batch_save


@dataclass(slots=True)
class RayBatch(Generic[T_Ray]):
    batch_type: RayBatchType
    method: Any
    rays_type: Any
    grid: Tuple[int, int]             # (gx, gy) = (Nx, Ny)
    to_surface: int
    wave_number: int
    rays: List[T_Ray]
    x_lin: np.ndarray | None          # shape (gx,)
    y_lin: np.ndarray | None          # shape (gy,)
    process_time: float | None = None

    @property
    def gx(self) -> int: return self.grid[0]

    @property
    def gy(self) -> int: return self.grid[1]

    @property
    def total(self) -> int: return self.gx * self.gy

    @property
    def shape(self) -> tuple[int, int]: return self.gy, self.gx  # (Ny, Nx)

    @property
    def n(self) -> int: return len(self.rays)

    def flat_index(self, ix: int, iy: int) -> int:
        """
        Return flat index k for (ix, iy), assuming x is fast axis.

        Same convention as Frame.read_frame:
        k = row*nx + col, row = iy, col = ix.
        """
        if not (0 <= ix < self.gx and 0 <= iy < self.gy):
            raise IndexError(f"(ix, iy)=({ix}, {iy}) out of bounds gx={self.gx}, gy={self.gy}")
        return iy * self.gx + ix

    def ray_ij(self, ix: int, iy: int) -> T_Ray:
        """Get ray at grid index (ix, iy)."""
        return self.rays[self.flat_index(ix, iy)]

    def array(self, attr: str) -> np.ndarray:
        """Return a (gy, gx) array of a per-ray attribute (e.g. 'x', 'y', 'z', 'intensity', 'opd', ...)."""
        vals = [getattr(r, attr) for r in self.rays]
        if len(vals) != self.total:
            # If acceptance rules changed and counts differ, pad with NaN
            pad = self.total - len(vals)
            vals += [np.nan] * max(0, pad)
        return np.asarray(vals, dtype=float).reshape(self.shape)

    def flat(self, attr: str) -> np.ndarray:
        """Return a 1D float array of length total for attribute `attr` (for H5 export)."""
        vals = [getattr(r, attr) for r in self.rays]
        if len(vals) != self.total:
            pad = self.total - len(vals)
            vals += [np.nan] * max(0, pad)
        return np.asarray(vals, dtype=float)  # shape (total,)

    def vectors(self, *attrs: str) -> dict[str, np.ndarray]:
        """Batch-pull multiple attributes at once, all reshaped (gy, gx)."""
        return {a: self.array(a) for a in attrs}

    def as_struct(self, attrs: Iterable[str]) -> dict[str, np.ndarray]:
        """Alias of vectors; pass any iterable of attribute names."""
        return self.vectors(*tuple(attrs))

    def xy(self) -> tuple[np.ndarray, np.ndarray]:
        return self.array("x"), self.array("y")

    def xyz(self) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
        return self.array("x"), self.array("y"), self.array("z")

    def __str__(self) -> str:
        """Pretty one-line summary."""
        n = len(self.rays)
        gx, gy = self.grid
        first = self.rays[0] if n else None
        attrs = ", ".join(vars(first).keys()) if first else "–"
        return (
            f"🌐 RayBatch {self.batch_type.value} - [{gx}×{gy}]\n "
            f"────────────────────────────\n"
            f"Processed time {self.process_time:.3f} sec"
            f"({n} rays) \n"
            f"method={getattr(self.method, 'name', self.method)}\n"
            f"wave={self.wave_number}\n"
            f"to_surface={self.to_surface}\n"
            f"rays_type={getattr(self.rays_type, 'name', self.rays_type)}\n"
            f"fields: {attrs}")

    @classmethod
    def compute(
            cls,
            *,
            batch_type: RayBatchType,
            rays: List[T_Ray],
            x_lin: np.ndarray,
            y_lin: np.ndarray,
            process_time: float,
            settings: RayTraceSettings) -> "RayBatch[T_Ray]":
        return cls(
            batch_type=batch_type,
            method=settings.method,
            rays_type=settings.rays_type,
            grid=settings.grid,
            to_surface=settings.to_surface,
            wave_number=settings.wave_number,
            rays=rays,
            x_lin=x_lin,
            y_lin=y_lin,
            process_time=process_time,
        )

    def save_to_h5(self, path: Path | str,**kwargs) -> str:
        """
        Save this RayBatch to an HDF5 file.
        Returns the group name used inside the file.
        """
        return ray_batch_save(
            batch=self,
            path=Path(path),
            **kwargs)



