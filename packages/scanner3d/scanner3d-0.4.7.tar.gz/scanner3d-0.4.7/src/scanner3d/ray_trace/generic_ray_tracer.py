from __future__ import annotations
import math
import time
import numpy as np
from allytools.logger import get_logger
from dataclasses import dataclass, fields, is_dataclass
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeVar
from zempy.zosapi.tools.raytrace.enums import OPDMode
from zempy.zosapi.tools.raytrace.enums.rays_type import RaysType
from scanner3d.ray_trace.trace_method import TraceMethod
from zempy.zosapi.tools.raytrace.results import (
    Ray,
    RayNormPolarized,
    RayNormUnpolarized,
    RayDirectPolarized,
    RayDirectUnpolarized,
    RayNormPolarizedFull,
    RayDirectPolarizedFull,
)

from scanner3d.ray_trace.raytrace_settings import RayTraceSettings

log = get_logger(__name__)

T_Ray = TypeVar("T_Ray", bound=Ray)


def _pol_to_components(
    pol: Optional[Tuple[float, float, float, float]]
) -> Tuple[float, float, float, float, float, float]:
    """
    Convert (Ex, Ey, phaX_deg, phaY_deg) to (ExRe, ExIm, EyRe, EyIm, EzRe, EzIm).

    Default: linearly polarized along X.
    """
    if pol is None:
        return 1.0, 0.0, 0.0, 0.0, 0.0, 0.0
    Ex, Ey, phaX_deg, phaY_deg = pol
    phiX = math.radians(phaX_deg)
    phiY = math.radians(phaY_deg)
    return (
        Ex * math.cos(phiX),
        Ex * math.sin(phiX),
        Ey * math.cos(phiY),
        Ey * math.sin(phiY),
        0.0,
        0.0,
    )


@dataclass(frozen=True)
class _Recipe:
    create: Callable[..., Any]  # -> buffer
    add_one: Callable[..., None]  # (buf, *coords)
    read_next: Callable[[Any], Any]  # (buf) -> rec
    accept: Callable[[Any], bool]  # record -> bool
    coord_iter: Callable[[], Iterable[Tuple]]  # yields tuples for add_one
    ray_class: Type[Ray]


def _accept_default(rec: Any) -> bool:
    return getattr(rec, "errorCode", 0) == 0 and getattr(rec, "vignetteCode", 0) == 0


class GenericRayTracer:
    """
    Batch ray tracer around native ZOSAPI BatchRayTrace tool.

    This is *not* a ZeModTool itself, but is used by ZeModTools.run_tool
    when tool_type == ZeModToolList.BATCH_RAYTRACE.
    """

    def __init__(self, raytrace_native: Any):
        """
        raytrace_native: native BatchRayTrace object from OpticStudio,
        e.g. Tools.OpenBatchRayTrace().
        """
        self.raytrace = raytrace_native
        self.x_lin: np.ndarray | None = None
        self.y_lin: np.ndarray | None = None
        self.process_time: float | None = None

    def _grid_norm(
        self, gx: int, gy: int
    ) -> Iterable[Tuple[float, float, float, float]]:
        self.x_lin = np.linspace(-1.0, 1.0, gx)
        self.y_lin = np.linspace(-1.0, 1.0, gy)
        for yi in range(gy):
            for xi in range(gx):
                yield float(self.x_lin[xi]), float(self.y_lin[yi]), 0.0, 0.0
        log.info("grid_norm %d x %d: completed %d coordinates", gx, gy,gx*gy)

    def _grid_direct(
        self,
        gx: int,
        gy: int,
        wave_number: int,
        rays_type_native: Any,  # already native RaysType from ZOS
    ) -> Iterable[Tuple[float, float, float, float, float, float]]:
        """
        Convert normalized Hx,Hy to (X,Y,Z,L,M,N) via BatchRayTrace.GetDirectFieldCoordinates.
        """
        self.x_lin = np.linspace(-1.0, 1.0, gx)
        self.y_lin = np.linspace(-1.0, 1.0, gy)

        for yi in range(gy):
            for xi in range(gx):
                ok, X, Y, Z, L, M, N_ = self.raytrace.GetDirectFieldCoordinates(
                    wave_number,
                    rays_type_native,
                    float(self.x_lin[xi]),
                    float(self.y_lin[yi]),
                    0.0,
                    0.0,
                )
                if not ok:
                    log.warning("GetDirectFieldCoordinates failed")
                    # Fallback ray: along +Z
                    yield 0.0, 0.0, 0.0, 0.0, 0.0, 1.0
                else:
                    yield float(X), float(Y), float(Z), float(L), float(M), float(N_)
        log.info("grid_direct %d x %d: completed %d coordinates",gx,gy, gx*gy)

    @staticmethod
    def _build_ray(ray_cls: Type[T_Ray], rec: Any) -> T_Ray:
        if not is_dataclass(ray_cls):
            raise TypeError(f"{ray_cls!r} must be a dataclass")
        data: Dict[str, Any] = {}
        for f in fields(ray_cls):
            try:
                data[f.name] = getattr(rec, f.name)
            except AttributeError as e:
                raise AttributeError(
                    f"Record missing attribute '{f.name}' for {ray_cls.__name__}"
                ) from e
        return ray_cls(**data)  # type: ignore[arg-type]

    def run_from_settings(self, s: RayTraceSettings) -> List[T_Ray]:
        return self.run(
            method=s.method,
            rays_type=s.rays_type,
            grid=s.grid,
            to_surface=s.to_surface,
            wave_number=s.wave_number,
            opd=s.opd,
            start_surface=s.start_surface,
            pol=s.pol)

    def run(
        self,
        method: TraceMethod,
        rays_type: RaysType,
        grid: Tuple[int, int],
        to_surface: int,
        wave_number: int,
        opd: Optional[OPDMode] = OPDMode.None_,
        start_surface: Optional[int] = None,
        pol: Optional[Tuple[float, float, float, float]] = None,
    ) -> List[T_Ray]:
        gx, gy = grid
        total = gx * gy
        def _need_start_surface() -> None:
            if start_surface is None:
                raise ValueError(f"{method} requires start_surface to be set")

        ecomp = _pol_to_components(pol)

        recipes: Dict[TraceMethod, _Recipe] = {
            TraceMethod.Normal_Unpolarized: _Recipe(
                create=lambda: self.raytrace.CreateNormUnpol(total, rays_type, to_surface),
                add_one=lambda buf, hx, hy, px, py: buf.AddRay(
                    wave_number, hx, hy, px, py, opd
                ),
                read_next=lambda buf: buf.ReadNextResult(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_norm(gx, gy),
                ray_class=RayNormUnpolarized,
            ),
            TraceMethod.Direct_Unpolarized: _Recipe(
                create=lambda: (
                    _need_start_surface(),
                    self.raytrace.CreateDirectUnpol(
                        total, rays_type, start_surface, to_surface
                    ),
                )[1],
                add_one=lambda buf, X, Y, Z, L, M, N_: buf.AddRay(
                    wave_number, X, Y, Z, L, M, N_
                ),
                read_next=lambda buf: buf.ReadNextResult(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_direct(
                    gx, gy, wave_number, rays_type
                ),
                ray_class=RayDirectUnpolarized,
            ),
            TraceMethod.Normal_Polarized: _Recipe(
                create=lambda: self.raytrace.CreateNormPol(
                    total,
                    rays_type,
                    *(pol or (1.0, 0.0, 0.0, 0.0)),
                    to_surface,
                ),
                add_one=lambda buf, hx, hy, px, py: buf.AddRay(
                    wave_number, hx, hy, px, py, *ecomp
                ),
                read_next=lambda buf: buf.ReadNextResult(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_norm(gx, gy),
                ray_class=RayNormPolarized,
            ),
            TraceMethod.Direct_Polarized: _Recipe(
                create=lambda: (
                    _need_start_surface(),
                    self.raytrace.CreateDirectPol(
                        total,
                        rays_type,
                        *(pol or (1.0, 0.0, 0.0, 0.0)),
                        start_surface,
                        to_surface,
                    ),
                )[1],
                add_one=lambda buf, X, Y, Z, L, M, N_: buf.AddRay(
                    wave_number, X, Y, Z, L, M, N_, *ecomp
                ),
                read_next=lambda buf: buf.ReadNextResult(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_direct(
                    gx, gy, wave_number, rays_type
                ),
                ray_class=RayDirectPolarized,
            ),
            TraceMethod.Normal_Polarized_Full: _Recipe(
                create=lambda: self.raytrace.CreateNormPol(
                    total,
                    rays_type,
                    *(pol or (1.0, 0.0, 0.0, 0.0)),
                    to_surface,
                ),
                add_one=lambda buf, hx, hy, px, py: buf.AddRay(
                    wave_number, hx, hy, px, py, *ecomp
                ),
                read_next=lambda buf: buf.ReadNextResultFull(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_norm(gx, gy),
                ray_class=RayNormPolarizedFull,
            ),
            TraceMethod.Direct_Polarized_Full: _Recipe(
                create=lambda: (
                    _need_start_surface(),
                    self.raytrace.CreateDirectPol(
                        total,
                        rays_type,
                        *(pol or (1.0, 0.0, 0.0, 0.0)),
                        start_surface,
                        to_surface,
                    ),
                )[1],
                add_one=lambda buf, X, Y, Z, L, M, N_: buf.AddRay(
                    wave_number, X, Y, Z, L, M, N_, *ecomp
                ),
                read_next=lambda buf: buf.ReadNextResultFull(),
                accept=_accept_default,
                coord_iter=lambda: self._grid_direct(
                    gx, gy, wave_number, rays_type
                ),
                ray_class=RayDirectPolarizedFull,
            ),
        }

        if method not in recipes:
            raise ValueError(f"Unsupported method: {method}")

        recipe = recipes[method]
        ray_cls = recipe.ray_class
        buf = recipe.create()
        buf.ClearData()
        t0 = time.time()
        for coords in recipe.coord_iter():
            recipe.add_one(buf, *coords)
        t1 = time.time()
        log.info("Added %d rays in %.4f s", total, t1 - t0)

        self.raytrace.RunAndWaitForCompletion()
        buf.StartReadingResults()

        self.process_time = time.time() - t0
        log.info("Processing finished in %.4f s", self.process_time)

        out: List[T_Ray] = []
        valid = 0
        rec = recipe.read_next(buf)
        while getattr(rec, "ok", False):
            if recipe.accept(rec):
                out.append(self._build_ray(ray_cls, rec))
                valid += 1
            rec = recipe.read_next(buf)

        t2 = time.time()
        log.info("Read %d/%d accepted rays in %.4f s", valid, total, t2 - t1)
        return out
