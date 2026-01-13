from zempy.zosapi.tools.raytrace.results import Ray
from scanner3d.zemod.tools.zemod_tool import ZeModTool
from scanner3d.ray_trace.raytrace_settings import RayTraceSettings
from scanner3d.ray_trace.generic_ray_tracer import GenericRayTracer


class ZeModBatchRayTraceTool(ZeModTool):
    """
    Specialized ZeModTool subclass for batch ray tracing.
    Wraps GenericRayTracer but fits into the ZeModTools.run_tool pipeline.
    """

    __slots__ = ("settings", "generic_tracer", "rays")

    def __init__(self, native_batch_tool):
        super().__init__(native_batch_tool)
        self.settings: RayTraceSettings | None = None
        self.generic_tracer = GenericRayTracer(native_batch_tool)
        self.rays: list[Ray] | None = None

    def apply_settings(self, settings: RayTraceSettings):
        # override base apply_settings (which expects ZeModToolSettings.apply_to)
        self.settings = settings

    def run(self):
        if self.settings is None:
            raise RuntimeError("ZeModBatchRayTraceTool.run() called without settings")
        self.rays = self.generic_tracer.run_from_settings(self.settings)

    def run_wait_for_completion(self):
        """
        Override the ZeModTool behavior: do NOT call native.RunAndWaitForCompletion().
        Instead, execute the GenericRayTracer-based run.
        """
        self.run()
        return self.rays  # or bool(len(self.rays or [])), if you prefer
