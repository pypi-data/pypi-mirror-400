from __future__ import annotations
from dataclasses import dataclass, replace
from typing import Tuple, Optional, TYPE_CHECKING
from zempy.zosapi.tools.raytrace.enums import RaysType
from zempy.zosapi.tools.raytrace.enums import OPDMode
from scanner3d.ray_trace.trace_method import TraceMethod

if TYPE_CHECKING:
    from scanner3d.camera3d.camera3d import Camera3D


@dataclass(frozen=True)
class RayTraceSettings:
    name:str
    rays_type: RaysType
    method: TraceMethod
    wave_number: int
    grid: Optional[Tuple[int, int]]
    to_surface: int = 0
    start_surface: Optional[int] = 0
    opd: Optional[OPDMode] = OPDMode.None_
    pol: Optional[Tuple[float, float, float, float]] = None
    use_sensor_grid: bool = False

    def replace_surface(self, to_surface: int) -> "RayTraceSettings":
        return replace(self, to_surface=to_surface)

    def replace_grid(self, camera: "Camera3D") -> "RayTraceSettings":
        if not self.use_sensor_grid:
            return self
        sensor = camera.sensor
        grid = (sensor.width_pix, sensor.height_pix)
        return replace(self, grid=grid)

    def __str__(self) -> str:
        return (
            "RayTraceSettings(\n"
            f"  name={self.name!r},\n"
            f"  rays_type={self.rays_type.name},\n"
            f"  method={self.method.name},\n"
            f"  wave_number={self.wave_number},\n"
            f"  grid={self.grid if self.grid is not None else ('sensor' if self.use_sensor_grid else None)},\n"
            f"  to_surface={self.to_surface},\n"
            f"  start_surface={self.start_surface},\n"
            f"  opd={self.opd.name if self.opd is not None else None},\n"
            f"  pol={self.pol},\n"
            f"  use_sensor_grid={self.use_sensor_grid},\n"
            ")"
        )

normal_unpolarized_quick = RayTraceSettings(
    name="Quick 64x64",
    rays_type=RaysType.Real,
    method=TraceMethod.Normal_Unpolarized,
    wave_number=1,
    grid=(64, 64))

normal_unpolarized_full = RayTraceSettings(
    name="Full sensor",
    rays_type=RaysType.Real,
    method=TraceMethod.Normal_Unpolarized,
    wave_number=1,
    grid = None,
    use_sensor_grid=True)
