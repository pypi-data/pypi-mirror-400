from __future__ import annotations
from dataclasses import dataclass
from enum import Enum
from typing import Callable, Sequence, Dict, Optional, Union, Any
from allytools.units.length import Length
from isensor.grid import Grid
from scanner3d.geo.z_range import ZRange
import inspect

def callable_info(fun: Callable[..., Any] | None) -> str:
    """
    Return a short string description of a callable (or 'None').
    """
    if fun is None:
        return "None"
    try:
        sig = inspect.signature(fun)
        name = getattr(fun, "__name__", repr(fun))
        return f"{name}{sig}"
    except (TypeError, ValueError):
        # Some callables may not have a retrievable signature
        return getattr(fun, "__name__", repr(fun))

class AlbumTypes(Enum):
    MAJOR_FRAMES = "Major Frames"
    RADIAL = "Radial"
    SPARSE_GRID = "Sparse grid"


GridStep = Union[int, Length]
LenSeq   = Sequence[Length]


@dataclass(frozen=True)
class AlbumTemplate:
    """
    Strategy only: describes *how* to build X/Y/Z axes,
    but not *with what step values*.
    """
    x: Callable[[Grid, GridStep], LenSeq]
    y: Optional[Callable[[Grid, GridStep], LenSeq]]
    z: Callable[[ZRange, Optional[Length]], LenSeq]
    save_image: bool
    save_h5: bool


@dataclass
class AlbumSettings:
    name: str
    album_type: AlbumTypes
    template: AlbumTemplate
    dx: Optional[GridStep]
    dy: Optional[GridStep]
    dz: Optional[Length]

    @property
    def enable_image_save(self) -> bool:
        return self.template.save_image

    @property
    def enable_h5_save(self) -> bool:
        return self.template.save_h5

    def get_x_seq(self, grid: Grid) -> Sequence[Length]:
        if self.dx is None:
            raise RuntimeError("dx is not set for this album")
        xs = self.template.x(grid, self.dx)
        return [x for x in xs]

    def get_y_seq(self, grid: Grid) -> Optional[Sequence[Length]]:
        if self.template.y is None:
           return None
        if self.dy is None:
            raise RuntimeError("dy is not set for this album")
        y_fun = self.template.y
        ys = y_fun(grid, self.dy)
        return [y for y in ys]

    def get_z_seq(self, z_range: ZRange) -> Sequence[Length]:
        zs = self.template.z(z_range, self.dz)
        return [z for z in zs]


    def __str__(self) -> str:

        def fmt_step(v):
            if v is None:
                return "—"
            if isinstance(v, int):
                return str(v)
            if isinstance(v, Length):
                return f"{v.value_mm:.3g} mm"
            return str(v)

        def fmt_len(v: Optional[Length]):
            if v is None:
                return "—"
            return f"{v.value_mm:.3g} mm"

        lines = [
            f"📀 AlbumSettings [{self.name}]",
            "----------------------------------------",
            f"  Type:        {self.album_type.name}",
            "",
            "  Axes:",
            f"    X: {callable_info(self.template.x)}",
            f"    Y: {callable_info(self.template.y)}",
            f"    Z: {callable_info(self.template.z)}",
            "",
            "  Steps:",
            f"    dx: {fmt_step(self.dx)}",
            f"    dy: {fmt_step(self.dy)}",
            f"    dz: {fmt_len(self.dz)}",
            "",
            "  Saving:",
            f"    Save image: {self.enable_image_save}",
            f"    Save HDF5:  {self.enable_h5_save}",
        ]
        return "\n".join(lines)



ALBUM_TYPES_REG: Dict[AlbumTypes, AlbumTemplate] = {
    AlbumTypes.MAJOR_FRAMES: AlbumTemplate(
        x=lambda g, n: g.x1d_n(int(n)),
        y=lambda g, n: g.y1d_n(int(n)),
        z=lambda zr, step: zr.to_tuple(),
        save_image=True,
        save_h5=True,
    ),
    AlbumTypes.RADIAL: AlbumTemplate(
        x=lambda g, step: g.get_radial(step),
        y=None,
        z=lambda zr, step: zr.wd_sequence(step),
        save_image=False,
        save_h5=True,
    ),
    AlbumTypes.SPARSE_GRID: AlbumTemplate(
        x=lambda g, n: g.sparse_quadrant(int(n))[0],
        y=lambda g, n: g.sparse_quadrant(int(n))[1],
        z=lambda zr, step: zr.wd_sequence(step),
        save_image=False,
        save_h5=True,
    ),
}